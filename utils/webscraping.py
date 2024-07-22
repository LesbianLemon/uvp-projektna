import requests as req
import bs4 as bs

import os.path

import typing
from typing import Optional

class WebPage():
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
		Saves HTML of given website URL to given path.

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
				return True

		except FileExistsError:
			return False
