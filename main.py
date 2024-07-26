import re
import time
import argparse # command-line arguments

# locally sourced modules
from utils.webscraping import PageScraper, MultiScraper
from utils.datafiles import Directory, File, CSVFile

from typing import Callable # typing for functions


#===================GLOBAL VARIABLES====================#
# see `get_url()` function for info on valid options
sea: str = "%2A" # sea - search string (%2A = *)
sfor: str = "names" # sfor - search for
valids: str = "" # valids - disable search for only valid meteorites
stype: str = "contains" # stype - type of search
lrec: str = "5000" # lrec - meteorites per page
map: str = "ll" # map - display decimal degrees location

# Example URL: https://www.lpi.usra.edu/meteor/metbull.php?sea=%2A&sfor=names&ants=&nwas=&falls=&valids=yes&stype=contains&lrec=50&map=ll&browse=&country=All&srt=name&categ=All&mblist=All&rect=&phot=&strewn=&snew=0&pnt=Normal%20table&dr=&page=1
# website URL with preset search options
homepage_url: str = "https://www.lpi.usra.edu/meteor/metbull.php?"

# trick website into thinking its a request from a real browser
headers: dict[str, str] = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"Accept-Encoding": "gzip, deflate",
	"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
	"Dnt": "1",
	"Upgrade-Insecure-Requests": "1",
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
}

# directory where to save resulting csv/json files
data_dir: Directory = Directory("data/")
# directory where to save HTML files
html_data_dir: Directory = Directory("data/html/")
#=======================================================#


# command-line argument setup
parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("--threads", "-t", help="number of threads used for saving the HTML files", type=int, default=8)
parser.add_argument("--no-force", help="will disable overwriting files with the same name", action="store_false", dest="force")
args: argparse.Namespace = parser.parse_args()


# typing for **kwargs ignored due to annoyance and complexity
# make the url with valid options
def get_url(**kwargs) -> str:
	# preset the valid options we can change and a lambda function to validate the input with
	options: dict[str, Callable[[str], bool]] = {
		"sea": lambda x: type(x) is str,
		"sfor": lambda x: x in ["names", "text", "places", "classes", "years"],
		"valids": lambda x: x in ["yes", ""],
		"stype": lambda x: x in ["contains", "starts", "exact", "sounds"],
		"lrec": lambda x: type(x) is str and x.isnumeric(), # lrec can be any number positive number represented as a string
		"map": lambda x: x in ["gg", "ge", "ww", "ll", "dm", "none"]
	}
	url: str = homepage_url

	arg_name: str
	for arg_name in kwargs:
		value: str = kwargs[arg_name] # have to do it like this to avoid mypy complaints

		if arg_name in options.keys():

			if options[arg_name](value):
				url += f"&{arg_name}={value}"

	return url


# get page count from number of results on smaller page to save time
# this improves execution speed from previous method of getting pagecount from first page (no need to load that much data)
def get_page_count() -> int:
	# scrape with same options, but only 1 meteorite per page to save time
	small_scraper: PageScraper = PageScraper(get_url(sea=sea, sfor=sfor, valids=valids, stype=stype, lrec="1", map=map), headers=headers)
	pattern: str = r"(\d+) records found"
	match: re.Match[str] | None = re.search(pattern, small_scraper.get_html())

	if match is None:
		return -1

	meteor_count: int = int(match.group(1))

	# kind of a hack to get rounding up
	per_page: int = int(lrec)
	page_count: int = (meteor_count - 1)//per_page + 1

	print(f"Found {page_count} pages.")
	return page_count


def download_pages(scraper: MultiScraper) -> None:
	print(f"Starting HTML download...", "\n", sep="")
	start_time: float = time.time()

	# initialise the scrapers (download HTML files)
	scraper.init_scrapers(html_data_dir, args.threads, force=args.force)

	end_time: float = time.time()

	for page_name in scraper.scrapers.keys():
		print(f"Page '{page_name}' is being parsed with {scraper.scrapers[page_name].html_file}")
	print("\n", f"Downloading finished, took about: {round(end_time - start_time, 5)}s", sep = "")


def parse_page(page_scraper: PageScraper) -> bool:
	# skipping typing in try block due to complexity
	# mypy does not automatically ignore try/except block so we add "# type: ignore"
	try:
		table = page_scraper.parser.find("table", { "id": "maintable" }) # type: ignore
		table_rows = table.find_all("tr") # type: ignore

		table_head = table_rows[0] # type: ignore
		thead_variables = [th.text for th in table_head.find_all("th", { "class": "insidehead" })] # type: ignore

		return True
	
	except Exception as err:
		print(f"Error while parsing with {page_scraper}: {err}")
		return False


def parse_all_pages(scraper: MultiScraper, output_file: File | None=None) -> None:
	page_name: str
	for page_name in scraper.pages.keys():
		page_scraper: PageScraper = scraper.get_scraper(page_name)

		print("\n", f"Starting parsing for '{page_name}'...", sep="")
		start_time: float = time.time()
		
		page_scraper.start_parser()
		success: bool = parse_page(page_scraper)
		page_scraper.stop_parser()

		end_time: float = time.time()
		time_taken: float = round(end_time - start_time, 5)

		if success:
			print(f"Successfuly parsed '{page_name}'! Time taken: {time_taken}s")
		else:
			print(f"Parsing '{page_name}' failed! Time taken: {time_taken}")


def main() -> None:
	# get url with proper search options
	url = get_url(sea=sea, sfor=sfor, valids=valids, stype=stype, lrec=lrec, map=map)

	# need page count to know how many websites to scrape
	page_count: int = get_page_count()
	# function return -1 if no match was found
	if page_count == -1:
		print(f"Could not find number of pages. Aborting!")
		return

	pages: dict[str, str] = {f"page{i}": url + f"&page={i}" for i in range(1, page_count + 1)}
	scraper: MultiScraper = MultiScraper(pages, headers=headers)

	# start page downloading
	download_pages(scraper)

	# start HTML parsing
	parse_all_pages(scraper)

	
if __name__ == "__main__":
	main()
