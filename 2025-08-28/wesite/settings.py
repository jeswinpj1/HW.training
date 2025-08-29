import logging

BASE_URL = "https://www.quickerala.com"
START_URL = "https://www.quickerala.com/thrissur/real-estate/real-estate-agents/sbct-5996-dt-13"
USER_AGENT = "Mozilla/5.0"
RAW_HTML_FILE = "raw.html"
LINKS_FILE = "links.txt"
CLEANED_DATA_FILE = "cleaned_data.txt"
LOG_FILE = "scraper.log"


class DataMiningError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        if self.code is not None:
            return f"[Error code {self.code}] {self.message}"
        return self.message


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        filemode='a',
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )