import re
import argparse # command-line arguments
from concurrent.futures import ThreadPoolExecutor, as_completed # multithreading

from utils.webscraping import WebPage # locally sourced module


# command-line argument setup
parser = argparse.ArgumentParser()
parser.add_argument("--threads", "-t", help="number of threads used for saving the HTML files", type=int, default=8)
args = parser.parse_args()


# save time and space by making a dedicated function for save feedback
def print_save_success(return_type: int, page_num: int, path: str) -> None:
	match return_type:
		case 0:
			print(f"Page {page_num} failed to be saved to `{path}`.")
		case 1:
			print(f"Page {page_num} already has `{path}`, using that instead.")
		case 2:
			print(f"Page {page_num} saved successfully to `{path}`.") 


# get a list of NON-INITIALISED WebPage elements (this is to reduce memory usage and processing time)
def get_saved_pages(url: str, start_page:int, end_page: int, force: bool=False) -> list[WebPage]:
	pages: list[WebPages] = []

	page_num: int
	for page_num in range(start_page, end_page + 1):
		page: WebPage = WebPage(url + str(page_num))
		path = f"data/page{page_num}.html"
		return_type: int = page.save_html(path, force=force)

		print_save_success(return_type, page_num, path)

		pages.append(page)

	return pages


def get_saved_page(url: str, page_num: int) -> WebPage:
	page: WebPage = WebPage(url + str(page_num))

	path: str = f"data/page{page_num}.html"
	return_type: int = page.save_html(path)

	print_save_success(return_type, page_num, path)

	return page


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
	
	# add "1", representing the first page, which should always exist
	page1: WebPage = WebPage(url + "1")

	# save page 1 first, the rest come later
	return_type: int = page1.save_html("data/page1.html")

	print_save_success(return_type, 1, "data/page1.html")

	# we need page 1 to find how many pages there are
	if return_type == 0:
		print("Aborting, page 1 needs to be saved properly!")
		return
	
	page1.init_parser()

	# we do not initialise BeautifulSoup for a simple page count search (save memory and processing time)
	# template <h4> text containing page number count: "Showing data for page 1 of 1514: records 1 - 50"
	page_count: int = int(re.search(r"page \d+ of (\d+)", page1.h4.text).group(1)) # match the second number and add it to group #1 then save result of group #1 match

	pages: list[WebPage] = [page1]

	# make `args.threads` many threads to perform the downloading
	with ThreadPoolExecutor(max_workers=args.threads) as executor:
		i: int # index
		futures = [executor.submit(get_saved_page, url, i) for i in range(2, page_count + 1)]

	for future in as_completed(futures):
		pages.append(future.result())

	print(*pages, sep="\n")


if __name__ == "__main__":
    main()
