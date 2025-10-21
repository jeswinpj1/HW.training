import requests
from lxml import html
import logging
from time import sleep

# -------------------- CONFIGURATION --------------------
INPUT_FILE = "product_urls.txt"        # File containing list of URLs (one per line)
ERROR_LOG_FILE = "error_log.txt"       # File to log errors
REQUEST_TIMEOUT = 10                   # Seconds
DELAY_BETWEEN_REQUESTS = 0.5           # Seconds (to avoid blocking)
# --------------------------------------------------------

# Configure logging
logging.basicConfig(filename=ERROR_LOG_FILE,
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Counters
total_requests = 0
success = 0
failure = 0


def get_page_title(response_text):
    """Extracts <title> text using XPath."""
    try:
        tree = html.fromstring(response_text)
        title = tree.xpath('//title/text()')
        return title[0].strip() if title else None
    except Exception:
        return None


def check_url(url):
    """Checks status code and title of a given URL."""
    global success, failure

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        status_code = response.status_code
        title = get_page_title(response.text)

        # Print results
        print(f"URL: {url}")
        print(f"Status Code: {status_code}")
        print(f"Title: {title}\n")

        # Handle conditions for errors
        if status_code != 200 or not title:
            failure += 1
            logging.error(f"URL: {url} | Status: {status_code} | Title: {title}")
        else:
            success += 1

    except requests.exceptions.RequestException as e:
        failure += 1
        logging.error(f"URL: {url} | ERROR: {e}")


def main():
    global total_requests

    try:
        with open(INPUT_FILE, "r") as file:
            urls = [line.strip() for line in file if line.strip()]

        total_requests = len(urls)
        print(f"Total URLs to check: {total_requests}\n")

        for url in urls:
            check_url(url)
            sleep(DELAY_BETWEEN_REQUESTS)

        # Summary
        success_rate = (success / total_requests) * 100 if total_requests else 0
        failure_rate = (failure / total_requests) * 100 if total_requests else 0

        print("\n-------- SUMMARY --------")
        print(f"Total Requests: {total_requests}")
        print(f"Success: {success}")
        print(f"Failure: {failure}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Failure Rate: {failure_rate:.2f}%")
        print("--------------------------")

    except FileNotFoundError:
        print(f"Error: File '{INPUT_FILE}' not found.")
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()