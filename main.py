import re
import time
import argparse # command-line arguments

from utils.webscraping import MultiScraper, PageScraper # locally sourced module


# command-line argument setup
parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("--threads", "-t", help="number of threads used for saving the HTML files", type=int, default=8)
args: argparse.Namespace = parser.parse_args()


# save time and space by making a dedicated function for file saving feedback
def print_save_success(return_type: int, name: str, data_dir: str) -> None:
	path = data_dir + f"{name}.html"
	match return_type:
		case 0:
			print(f"Page '{name}' failed to be saved to '{path}'.")
		case 1:
			print(f"Page '{name}' already has an html file at '{path}', using that instead.")
		case 2:
			print(f"Page '{name}' saved successfully to '{path}'.") 


# get page count from number of valid meteors on homepage to save time
# this improves execution speed from previous method of getting pagecount from first page (no need to load that much data)
def get_page_count(homepage_url: str, per_page: int, headers: dict[str, str]) -> int:
	homepage_scraper: PageScraper = PageScraper("https://www.lpi.usra.edu/meteor/metbull.php", headers=headers)
	pattern: str = r"<b>Database stats:<\/b> (\d+) valid meteorite names"
	match: re.Match[str] | None = re.search(pattern, homepage_scraper.get_html())

	if match is None:
		return -1

	valid_meteor_count: int = int(match.group(1))

	# kind of a hack to get rounding up
	return (valid_meteor_count - 1)//per_page + 1


def main() -> None:
	#===================VARIABLES====================#
	sea = "%2A" # sea - search string (%2A = *)
	sfor = "names" # sfor - search for (names, text, places, classes, years)
	valids = "yes" # valids - only approved meteorites
	stype = "contains" # stype - type of search (contains, startswith, exact, soundslike)
	lrec = 5000 # lrec - lines per page (20, 50, 100, 200, 500, 1000, 2000, 5000, 50000)
	map = "ll" # map - display decimal degrees location

	# Example URL: https://www.lpi.usra.edu/meteor/metbull.php?sea=%2A&sfor=names&ants=&nwas=&falls=&valids=yes&stype=contains&lrec=50&map=ll&browse=&country=All&srt=name&categ=All&mblist=All&rect=&phot=&strewn=&snew=0&pnt=Normal%20table&dr=&page=1
	# website URL with preset search options
	homepage_url = "https://www.lpi.usra.edu/meteor/metbull.php"
	url: str = homepage_url + f"?sea={sea}&sfor={sfor}&valids={valids}&stype={stype}&lrec={lrec}&map={map}"

	# trick website into thinking its a request from a real browser
	headers: dict[str, str] = {
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
		"Dnt": "1",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
	}

	# directory where to save HTML files and csv/json files
	data_dir: str = "data/"
	#================================================#

	# need page count to know how many websites to scrape
	page_count: int = get_page_count(homepage_url, lrec, headers)
	# function return -1 if no match was found
	if page_count == -1:
		print(f"Could not find meteor count on '{homepage_url}'. Aborting!")
		return

	print(f"Found {page_count} pages, starting HTML download...")

	pages: dict[str, str] = {f"page{i}": url + f"&page={i}" for i in range(1, page_count + 1)}

	# we want to see how long the downloading took
	start_time = time.time()

	# start the actual scraping with all the pages
	scraper: MultiScraper = MultiScraper(pages, headers=headers)
	return_types: dict[str, int] = scraper.init_scrapers(data_dir + "html/", args.threads)

	end_time = time.time()
	print(f"Downloading finished, took about: {round(end_time - start_time, 5)}s", "\n", sep = "")

	name: str
	for name in return_types.keys():
		print_save_success(return_types[name], name, data_dir + "html/")
	
	


if __name__ == "__main__":
	main()
