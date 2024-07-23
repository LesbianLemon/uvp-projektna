import requests as req
import bs4 as bs

import os

import concurrent.futures as cf


class PageScraper:
	url: str
	headers: dict[str, str]
	html_path: str | None

	initialised: bool
	_parser: bs.BeautifulSoup | None

	def __init__(self, url: str, headers: dict[str, str]={}, html_path: str | None=None) -> None:
		"""
		PageScraper constructor.

		Parameters
		----------
		url : str
			| the website URL.
		headers : dict[str, str], default=`{}`
			| headers to be supplied with the http request
		html_path : str, optional
			| path to webpage HTML file.
		"""

		self.url = url
		self.headers = headers
		self.html_path = html_path

		self.initialised = False
		self._parser = None


	def __str__(self) -> str:
		return f"<PageScraper url={self.url}>"


	def __repr__(self) -> str:
		return f"PageScraper(url={self.url}, headers={self.headers}, html_path={self.html_path}, initialised={self.initialised})"

	
	def get_html(self) -> str:
		"""
		Access the website URL and return the HTML source code representing the webpage.
		
		Returns
		-------
		str
			| HTML source code.
		"""

		# adding headers requires Session
		session = req.Session()
		return req.get(self.url, headers=self.headers).text


	def save_html(self, path: str, force: bool=False) -> int:
		"""
		Saves HTML of given website URL to given path and adds said path to `html_path` class variable.

		Parameters
		----------
		path : str
			| the location where to store the read HTML data.
		force : bool, default=`False`
			| whether to force over-writing the provided file path (if `False` and path already exists it will also set `html_path` variable to said path)

		Returns
		-------
		int
			| `0` if writing failed, `1` if the file is already present and force=False, `2` if writing was successful
		"""

		if os.path.exists(path) and not force:
			return 1

		try:
			html = self.get_html()
			with open(path, "w") as file:
				file.write(html)
				self.html_path = path
				return 2
				
		except Exception as err:
			if os.path.exists(path):
				os.remove(path)

			print(f"{self} could not successfuly write to '{path}': {err}")
			return 0

	
	def start_parser(self, parser_type: str="html.parser") -> None:
		"""
		Starts the parser if html_path variable is set.

		Parameters
		----------
		parser_type : str, default=`"html.parser"`
			| a valid `BeautifulSoup` parser for the saved HTML file
		"""

		# make sure htaml_path is set before trying to initialise BeautifulSoup
		assert self.html_path, "'html_path' class variable is not set, make sure to run 'class.save_html(path)'"

		with open(self.html_path, "r") as html_doc:
			self._parser = bs.BeautifulSoup(html_doc.read(), parser_type)
			self.initialised = True


	def stop_parser(self) -> None:
		"""
		Clears the current parser.
		"""

		self._parser = None
	


class MultiScraper:
	pages: dict[str, str]
	headers: dict[str, str]

	scrapers: dict[str, PageScraper]

	def __init__(self, pages: dict[str, str], headers: dict[str, str]={}) -> None:
		"""
		MultiScraper constructor.

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


	def init_scrapers(self, save_dir: str, threads: int) -> dict[str, int]:
		"""
		Create and initialise all the scrapes for the provided pages.
		This constructs the required PageScraper objects and saves them into `class.scrapers`, then performs a multithreaded HTML file save.

		Parameters
		----------
		save_dir : str
			| a directory of the following form `"path/to/dir/"` of where the method will save the pages HTML files
		threads : int
			| number of threads to be used during the multithreaded saving process

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

				path: str = save_dir + f"{name}.html"
				futures_to_name.update({executor.submit(page_scraper.save_html, path): name})

			return_types: dict[str, int] = {}

			future: cf.Future
			for future in cf.as_completed(futures_to_name):
				return_types[futures_to_name[future]] = future.result()

			return return_types
