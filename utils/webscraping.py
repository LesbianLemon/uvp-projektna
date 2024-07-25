import requests as req
import bs4 as bs

import os

import concurrent.futures as cf

from typing import Literal
from io import TextIOWrapper

from .datafiles import Directory, HTMLFile


class PageScraper:
	url: str
	headers: dict[str, str]
	html_file: HTMLFile | None

	initialised: bool
	parser: bs.BeautifulSoup | None

	def __init__(self, url: str, headers: dict[str, str]={}, html_file: HTMLFile | None=None) -> None:
		"""
		PageScraper initialiser.

		Parameters
		----------
		url : str
			| the website URL
		headers : dict[str, str], default=`{}`
			| headers to be supplied with the http request
		html_file : HTMLFile, optional
			| HTMLFile object representing the file to save to
		"""

		self.url = url
		self.headers = headers
		self.html_file = html_file

		self.initialised = False
		self.parser = None


	def __str__(self) -> str:
		return f"<PageScraper url={self.url}>"


	def __repr__(self) -> str:
		return f"PageScraper(url={self.url}, headers={self.headers}, html_file={self.html_file}, initialised={self.initialised})"

	
	def get_html(self) -> str:
		"""
		Access the website URL and return the HTML source code representing the webpage.
		
		Returns
		-------
		str
			| HTML source code
		"""

		# adding headers requires Session
		session = req.Session()
		return req.get(self.url, headers=self.headers).text


	def save_html(self, dir: Directory, filename: str, force: bool=False) -> Literal[0, 1, 2]:
		"""
		Saves HTML of given website URL to given directory with given filename and properly sets `html_file` instance variable.

		Parameters
		----------
		dir : Directory
			| the directory where to store the read HTML data
		filename : str
			| name of the file to create/write to
		force : bool, default=`False`
			| whether to force over-writing the provided file (if `False` and file already exists it will also set `html_file` variable to said file)

		Returns
		-------
		int
			| `0` if writing failed, `1` if the file is already present and force=False, `2` if writing was successful
		"""

		self.html_file = HTMLFile(dir, filename)

		# not the nicest implementation, but will do
		def custom_writer(file: TextIOWrapper) -> None:
			file.write(self.get_html())
		# we override with our custom writer to make sure self.get_html() gets called as late as possible
		return self.html_file.write_html("", force=force, writer=custom_writer) # since we are overriding with out custom writer, write content is skipped


	def clear_html(self, remove: bool=False) -> None:
		"""
		Clears the `html_file` instance variable and deletes the file if desired.

		Parameters
		----------
		remove : bool, default=`False`
			| whether to delete the file while clearing the `html_file` instance variable
		"""

		if self.html_file and remove:
			self.html_file.remove()
		self.html_file = None

	
	def start_parser(self, parser_type: str="html.parser") -> None:
		"""
		Starts the parser if html_file variable is set.

		Parameters
		----------
		parser_type : str, default=`"html.parser"`
			| a valid `BeautifulSoup` parser for the saved HTML file
		"""

		# make sure htaml_file is set before trying to initialise BeautifulSoup
		if not self.html_file:
			raise RuntimeError("Cannot start parser without `html_file` being set")

		self.parser = bs.BeautifulSoup(self.html_file.read(), parser_type)
		self.initialised = True


	def stop_parser(self) -> None:
		"""
		Clears the current parser.
		"""

		self.parser = None

	
class MultiScraper:
	pages: dict[str, str]
	headers: dict[str, str]

	scrapers: dict[str, PageScraper]

	def __init__(self, pages: dict[str, str], headers: dict[str, str]={}) -> None:
		"""
		MultiScraper initialiser.

		Parameters
		----------
		pages : dict[str, str]
			| a dictionary of custom name and URL pairs (the name will be used to represent the said URL anywhere possible)
		headers : dict[str, str], default=`{}`
			| headers to be supplied with the http requests for all the pages
		"""

		self.pages = pages
		self.headers = headers

		self.scrapers = {}


	def init_scrapers(self, save_dir: Directory, threads: int, force: bool=False) -> dict[str, Literal[0, 1, 2]]:
		"""
		Create and initialise all the scrapes for the provided pages.
		This constructs the required PageScraper objects and saves them into `class.scrapers`, then performs a multithreaded HTML file save.

		Parameters
		----------
		save_dir : Directory
			| a Directory object representing where the method will save the pages HTML files
		threads : int
			| number of threads to be used during the multithreaded saving process
		force : bool, default=`False`
			| whether to force overwriting exsisting files when initiating scrapers

		Returns
		-------
		dict[str, int]
			| a dictionary of name and integer pairs (`0` - writing failed, `1` - file already exists, `2` - writing successful)
		"""

		with cf.ThreadPoolExecutor(max_workers=threads) as executor:
			futures_to_name: dict[cf.Future, str] = {}

			name: str
			url: str
			for name, url in self.pages.items():
				page_scraper: PageScraper = PageScraper(url, headers=self.headers)
				self.scrapers[name] = page_scraper

				futures_to_name.update({executor.submit(page_scraper.save_html, save_dir, name, force=force): name})

			return_types: dict[str, Literal[0, 1, 2]] = {}

			future: cf.Future
			for future in cf.as_completed(futures_to_name):
				return_types[futures_to_name[future]] = future.result()

			return return_types
