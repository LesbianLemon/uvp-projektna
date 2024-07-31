import requests as req
import bs4 as bs

import concurrent.futures as cf

from io import TextIOWrapper

from .datafiles import Directory, HTMLFile


class PageScraper:
    url: str
    headers: dict[str, str]
    html_file: HTMLFile | None

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
            | an HTMLFile object representing the file to save to
        """

        self.url = url
        self.headers = headers
        self.html_file = html_file

        self.parser = None


    def __str__(self) -> str:
        return f"<PageScraper url={self.url}>"


    def __repr__(self) -> str:
        return f"PageScraper(url={self.url}, headers={self.headers}, html_file={self.html_file})"


    def is_initialised(self) -> bool:
        """
        Checks if the PageScraper is ready to start parsing.

        Returns
        -------
        bool
            | `True` if ready otherwise `False`
        """

        return not self.html_file is None


    def is_parsing(self) -> bool:
        """
        Checks if the PageScraper parser is running.

        Returns
        -------
        bool
            | `True` if the parser is active otherwise `False`
        """

        return not self.parser is None


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


    def save_html(self, html_file: HTMLFile, force: bool=False) -> None:
        """
        Saves HTML of given website URL to given directory with given filename and properly sets `html_file` instance variable.

        Parameters
        ----------
        file : HTMLFile
            | HTMLFile object of the file to write to
        force : bool, default=`False`
            | whether to force over-writing the provided file (if `False` and file already exists it will also set `html_file` variable to said file)
        """

        self.html_file = html_file

        # not the nicest implementation, but will do
        def custom_writer(file: TextIOWrapper) -> None:
            file.write(self.get_html())
        # we override with our custom writer to make sure self.get_html() gets called as late as possible (overriding causes write content to be skipped)
        self.html_file.write_html("", force=force, writer=custom_writer)


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
            | a valid BeautifulSoup parser

        Raises
        ------
        RuntimeError
            | when trying to start the parser without `html_file` being set
        """

        # make sure htaml_file is set before trying to initialise BeautifulSoup
        if not self.html_file:
            raise RuntimeError("Cannot start parser without `html_file` being set")

        self.parser = bs.BeautifulSoup(self.html_file.read_html(), parser_type)


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


    def init_scrapers(self, save_dir: Directory, threads: int, force: bool=False) -> None:
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
            | whether to force over-writing exsisting files when initiating scrapers
        """

        with cf.ThreadPoolExecutor(max_workers=threads) as executor:
            name: str
            url: str
            for name, url in self.pages.items():
                page_scraper: PageScraper = PageScraper(url, headers=self.headers)
                self.scrapers[name] = page_scraper

                html_file = HTMLFile(save_dir, name)
                executor.submit(page_scraper.save_html, html_file, force=force)


    def is_used(self, page_name: str) -> bool:
        """
        Checks if `page_name` is part of list of pages being used by MultiScraper.

        Parameters
        ----------
        page_name : str
            | name representing the page you wish to check

        Returns
        -------
        bool
            | `True` if is being used and `False` if not
        """

        return page_name in self.pages.keys()


    def get_scraper(self, page_name: str) -> PageScraper:
        """
        Gets the PageScraper of the page represented by `page_name` from class initialisation.

        Parameters
        ----------
        page_name
            | name given to page at start of MultiScraper initialisation

        Returns
        -------
        PageScraper
            | the requested PageScraper

        Raises
        ------
        ValueError
            | when improper `page_name` is supplied
        """

        if not self.is_used(page_name):
            raise ValueError("No page matches given `page_name`")

        return self.scrapers[page_name]
