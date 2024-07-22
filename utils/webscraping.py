import requests as req
import bs4 as bs

import os.path

import typing
from typing import Optional


class WebPage(bs.BeautifulSoup):
	url: str
	html_path: Optional[str]

	def __init__(self, url: str, html_path: Optional[str]=None) -> None:
		"""
		WebPage class constructor.

		Parameters
		----------
		url : str
			| the website URL.

		html : str, optional
			| path to webpage HTML file.
		"""

		self.url = url
		self.html_path = html_path


	def get_html(self) -> str:
		"""
		Access the website URL and return the HTML source code representing the webpage.
		
		Returns
		-------
		str
			| HTML source code.
		"""

		# trick website into thinking its a request from a real browser
		headers: dict = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
			"Dnt": "1",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
		}
		
		session = req.Session()
		return req.get(self.url, headers=headers).text


	def save_html(self, path: str, force: bool=False) -> bool:
		"""
		Saves HTML of given website URL to given path and adds said path to `html` class variable.

		Parameters
		----------
		path : str
			| the location where to store the read HTML data.
		force : bool, default=False
			| whether to force over-writing the provided file path.

		Returns
		-------
		bool
			| True if the write was successful and False if not.
		"""

		mode: str = "x" if not force else "w"

		try:
			with open(path, mode) as file:
				file.write(self.get_html())
				print(f"File saved to `{path}` and `html_path` will be set to its path")
				self.html_path = path
				return True
				
		except Exception as e:
			msg: str = "File could not be written and `html_path` was not set"

			if type(e) is FileExistsError:
				msg = f"File `{path}` already exists, `html_path` will be set to that file path"
				self.html_path = path
			
			print(msg)
			return False

	
	def init_parser(self, parser: str="html.parser") -> None:
		"""
		Starts the parser if html_path variable is set.

		Parameters
		----------
		parser : str, default="html.parser"
			| a valid BeautifulSoup parser for the saved HTML file
		"""

		assert self.html_path, "html_path class variable is not set, make sure to run `class.save_html(path)`"

		with open(self.html_path, "r") as html_doc:
			super().__init__(html_doc.read(), parser)
