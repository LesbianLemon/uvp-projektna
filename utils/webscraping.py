import requests as req
import bs4 as bs

import os.path


class WebPage(bs.BeautifulSoup):
	# variable typing
	url: str
	html_path: str | None
	initialised: bool

	def __init__(self, url: str, html_path: str | None=None) -> None:
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
		self.initialised = False


	# useful for printing
	def __str__(self):
		return f"WebPage(url={self.url}, html_path={self.html_path}, initialised={self.initialised})"

	
	def get_html(self) -> str:
		"""
		Access the website URL and return the HTML source code representing the webpage.
		
		Returns
		-------
		str
			| HTML source code.
		"""

		# trick website into thinking its a request from a real browser
		headers: dict[str, str] = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
			"Dnt": "1",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
		}
		
		# adding headers requires Session
		session = req.Session()
		return req.get(self.url, headers=headers).text


	def save_html(self, path: str, force: bool=False) -> bool:
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

		mode: str = "x" if not force else "w"

		# if mode is "x" and file already exists a FileExistsError is thrown
		try:
			with open(path, mode) as file:
				file.write(self.get_html())
				self.html_path = path
				return 2
				
		except Exception as e:
			if type(e) is FileExistsError:
				self.html_path = path
				return 1
			
			print(e)
			return 0

	
	def init_parser(self, parser: str="html.parser") -> None:
		"""
		Starts the parser if html_path variable is set.

		Parameters
		----------
		parser : str, default=`"html.parser"`
			| a valid `BeautifulSoup` parser for the saved HTML file
		"""

		# make sure htaml_path is set before trying to initialise BeautifulSoup
		assert self.html_path, "`html_path` class variable is not set, make sure to run `class.save_html(path)`"

		with open(self.html_path, "r") as html_doc:
			super().__init__(html_doc.read(), parser)
			self.initialised = True
