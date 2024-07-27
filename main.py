import re
import unicodedata # dealing with unicode
import time
import argparse # command-line arguments

# locally sourced modules
from utils.webscraping import PageScraper, MultiScraper
from utils.datafiles import Directory, File, CSVFile, JSONFile

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
parser.add_argument("--no-force", help="will not download HTML files again if they already exist", action="store_false", dest="force")
args: argparse.Namespace = parser.parse_args()


# mypy type checking requires use of --enable-incomplete-feature=NewGenericSyntax
# custom types used later on to shorten typing annotations - REQUIRES PYTHON 3.12+!!!
type MeteoriteValue = str | int | float | tuple[float, float]
type MeteoriteDict = dict[str, MeteoriteValue]


# typing for **kwargs ignored due to annoyance and complexity
# make the url with valid options
def get_url(**kwargs) -> str:
	# preset the valid options we can change and a lambda function to validate the input with
	options: dict[str, Callable[[str], bool]] = {
		"sea": lambda s: type(s) is str,
		"sfor": lambda s: s in ["names", "text", "places", "classes", "years"],
		"valids": lambda s: s in ["yes", ""],
		"stype": lambda s: s in ["contains", "starts", "exact", "sounds"],
		"lrec": lambda s: type(s) is str and s.isnumeric(), # lrec can be any number positive number represented as a string
		"map": lambda s: s in ["gg", "ge", "ww", "ll", "dm", "none"]
	}
	url: str = homepage_url

	arg_name: str
	for arg_name in kwargs:
		value: str = kwargs[arg_name] # have to do it like this to avoid mypy complaints

		if arg_name in options.keys():

			if options[arg_name](value):
				url += f"&{arg_name}={value}"

	return url


# TODO: find a faster way of getting page count
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


def transform_year(data: str) -> int | float | str:
	# grab the first number and ignore the rest and possibly a unit (some meteorites have years like "1967 or 1927")
	# not statistically the best, it would be better to drop them
	match_year: re.Match[str] | None = re.match(r"^.*?(?P<first_number>\d+\.?\d*).*?(?P<unit>(?:[a-zA-Z]?a)?)$", data)

	if not match_year is None:
		conversion: dict[str, int] = {
			"ma": 1_000_000,
			"ka": 1_000,
			"a": 1,
			"": 1 # if no unit found also just multiply by one
		}

		unit: str = match_year.groupdict()["unit"].lower()
		number_match: str = match_year.groupdict()["first_number"]
		first_number: int | float = int(number_match) if unit == "" and number_match.isdecimal() else float(number_match)

		return conversion[unit]*first_number

	# if no match, delete the field
	return ""


def transform_mass(data: str) -> float | str:
	match_mass: re.Match[str] | None = re.match(r"^(?P<amount>\d+\.?\d*)\s+(?P<unit>t|T|(?:[a-zA-Z]?g))$", data)

	if not match_mass is None:
		conversion: dict[str, float] = {
			"t": 1_000_000.0,
			"kg": 1_000.0,
			"g": 1.0,
			"mg": 0.001
		}
		
		unit: str = match_mass.groupdict()["unit"].lower()
		amount: float = float(match_mass.groupdict()["amount"])

		return conversion[unit]*amount

	# if no match, delete the field
	return ""


def transform_ll(data: str) -> tuple[float, float] | str:
	match_ll: re.Match[str] | None = re.match(r"\(([-|+]?\d+\.\d+),\s+([-|+]?\d+\.\d+)\)", data)

	# will match if value is (Lat, Long), then convert it into tuple of floats
	if not match_ll is None:
		return (float(match_ll.group(1)), float(match_ll.group(2)))

	# if no match, delete the field
	return ""


def transform_data(data: str, data_variable: str) -> MeteoriteValue:
	# replace non-breaking space with normal whitespace
	data = unicodedata.normalize("NFKC", data)
	# remove any other unicode character
	data = data.encode("ascii", "ignore").decode().strip()

	# if field is empty or unknown, we want to skip transforming
	match_unknown: re.Match[str] | None = re.match(r"^\(?unknown\)?$", data, flags=re.IGNORECASE)
	if data == "" or not match_unknown is None:
		return ""

	which_transform: dict[str, Callable[[str], MeteoriteValue]] = {
		"Year": transform_year,
		# "Place": transform_place,
		"Mass": transform_mass,
		"(Lat,Long)": transform_ll
	}

	# return valid numbers right away
	if data.lstrip("-").isdecimal():
		return int(data)

	# use approprite transform based on column type
	if data_variable in which_transform.keys():
		return which_transform[data_variable](data)

	# remaining data needs to be stripped of special characters like "*" and "#"
	return data.rstrip(" *#")


def parse_page(page_scraper: PageScraper, page_name: str) -> dict[str, MeteoriteDict]:
	# skipping typing for BeautifulSoup due to annoying None type
	table = page_scraper.parser.find("table", { "id": "maintable" }) # type: ignore
	table_rows = table.find_all("tr") # type: ignore

	table_head = table_rows[0] # type: ignore
	thead_variables: list[str] = [th.text.strip() for th in table_head.find_all("th", { "class": "insidehead" })]

	result_dict: dict[str, MeteoriteDict] = {}

	i: int
	for i in range(1, len(table_rows)):
		row = table_rows[i] # type: ignore
		data: list[MeteoriteValue] = [transform_data(td.text, thead_variables[j]) for j, td in enumerate(row.find_all("td"))]

		# zip the variables and data, filter the empty data then make a dictionary
		meteorite_dict: MeteoriteDict = dict(filter(lambda t: t[1] != "", zip(thead_variables, data)))
		result_dict[f"{page_name}-{i}"] = meteorite_dict

	return result_dict


def parse_all_pages(scraper: MultiScraper, json_file: JSONFile) -> None:
	json_dict: dict[str, MeteoriteDict] = {}

	page_name: str
	for page_name in scraper.pages.keys():
		page_scraper: PageScraper = scraper.get_scraper(page_name)

		print("\n", f"Starting parsing for '{page_name}'...", sep="")
		start_time: float = time.time()

		page_scraper.start_parser()
		json_dict.update(parse_page(page_scraper, page_name))
		page_scraper.stop_parser()

		end_time: float = time.time()
		print(f"Finished parsing '{page_name}'! Time taken: {round(end_time - start_time, 5)}s")

	json_file.write_json(json_dict, force=True)


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

	# start HTML parsing and save to JSON file
	json_file = JSONFile(data_dir, "output")
	parse_all_pages(scraper, json_file)


if __name__ == "__main__":
	main()
