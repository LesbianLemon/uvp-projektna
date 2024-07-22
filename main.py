import typing

from utils.webscraping import WebPage


def main():
    # Website URL
	url: str = "https://www.lpi.usra.edu/meteor/metbull.php?sea=%2A&sfor=names&valids=yes&stype=contains&lrec=50000&page=1"

	page: WebPage = WebPage(url)
	page.save_html("data/page1.html", force=True) # force=True to rewrite the file if it already exists




if __name__ == "__main__":
    main()
