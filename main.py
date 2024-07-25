import re
import time
import argparse # command-line arguments

# locally sourced modules
from utils.webscraping import MultiScraper, PageScraper
from utils.datafiles import Directory, File, HTMLFile

from typing import Callable, Literal # typing for functions


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
# url: str = homepage_url + f"?sea={sea}&sfor={sfor}&valids={valids}&stype={stype}&lrec={lrec}&map={map}"

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


# save time and space by making a dedicated function for file saving feedback
def print_save_success(save_success: Literal[0, 1, 2], file: File) -> None:
	match save_success:
		case 0:
			print(f"'{file}' failed to be saved.") 
		case 1:
			print(f"'{file}' already exists, using that instead.")
		case 2:
			print(f"'{file}' saved successfully.") 


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
	per_page = int(lrec)
	return (meteor_count - 1)//per_page + 1


def main() -> None:
	# get url with proper search options
	url = get_url(sea=sea, sfor=sfor, valids=valids, stype=stype, lrec=lrec, map=map)

	# need page count to know how many websites to scrape
	page_count: int = get_page_count()
	# function return -1 if no match was found
	if page_count == -1:
		print(f"Could not find number of pages. Aborting!")
		return

	print(f"Found {page_count} pages, starting HTML download...")

	pages: dict[str, str] = {f"page{i}": url + f"&page={i}" for i in range(1, page_count + 1)}

	# we want to see how long the downloading took
	start_time = time.time()

	# start the actual scraping with all the pages
	scraper: MultiScraper = MultiScraper(pages, headers=headers)
	files_success: dict[HTMLFile, Literal[0, 1, 2]] = scraper.init_scrapers(html_data_dir, args.threads, force=args.force)

	end_time = time.time()
	print(f"Downloading finished, took about: {round(end_time - start_time, 5)}s", "\n", sep = "")

	file: HTMLFile
	for file in files_success.keys():
		print_save_success(files_success[file], file)


if __name__ == "__main__":
	main()
