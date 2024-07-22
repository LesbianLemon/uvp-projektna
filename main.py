import typing
import re

from utils.webscraping import WebPage


def main():
    # Website URL
	url: str = "https://www.lpi.usra.edu/meteor/metbull.php?sea=%2A&sfor=names&valids=yes&stype=contains&lrec=50&map=ll&page=1"

	page: WebPage = WebPage(url)
	page.save_html("data/page1.html", force=False) # force=False do not rewrite the file if it already exists
	page.init_parser()


if __name__ == "__main__":
    main()
