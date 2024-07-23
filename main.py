import re
import argparse # command-line arguments

from utils.webscraping import MultiScraper # locally sourced module


# command-line argument setup
parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("--threads", "-t", help="number of threads used for saving the HTML files", type=int, default=8)
args: argparse.Namespace = parser.parse_args()


# save time and space by making a dedicated function for save feedback
def print_save_success(return_type: int, name: str, data_dir: str) -> None:
	path = data_dir + f"{name}.html"
	match return_type:
		case 0:
			print(f"Page `{name}` failed to be saved to `{path}`.")
		case 1:
			print(f"Page `{name}` already has an html file at `{path}`, using that instead.")
		case 2:
			print(f"Page {name} saved successfully to `{path}`.") 


def main() -> None:
	# website URL with preset search options:
	#
	# sea - search string (%2A = *)
	# sfor - search for (names, text, places, classes, years)
	# valids - only approved meteorites
	# stype - type of search (contains, startswith, exact, soundslike)
	# lrec - lines per page (20, 50, 100, 200, 500, 1000, 2000, 5000, 50000)
	# map - display decimal degrees location
	# page - page number inof search
	url: str = "https://www.lpi.usra.edu/meteor/metbull.php?sea=%2A&sfor=names&valids=yes&stype=contains&lrec=5000&map=ll&page="

	# trick website into thinking its a request from a real browser
	headers: dict[str, str] = {
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
		"Dnt": "1",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
	}

	pages: dict[str, str] = {
		"page1": url + "1",
		"page2": url + "2",
		"page3": url + "3",
		"page4": url + "4",
		"page5": url + "5",
		"page6": url + "6",
		"page7": url + "7",
		"page8": url + "8",
		"page9": url + "9",
		"page10": url + "10",
		"page11": url + "11",
		"page12": url + "12",
		"page13": url + "13",
		"page14": url + "14",
		"page15": url + "15",
		"page16": url + "16"
	}

	scraper = MultiScraper(pages, headers=headers)
	data_dir = "data/"
	return_types = scraper.init_scrapers(data_dir, args.threads)

	for name in return_types.keys():
		print_save_success(return_types[name], name, data_dir)


if __name__ == "__main__":
	main()
