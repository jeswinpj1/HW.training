#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
class ExampleSiteParser:
    """
    Example parser for a website that extracts and cleans data.
    """

    def __init__(self, base_url: str, output_file: str = "output.txt") -> None:
        """
        Initialize parser with base URL and output file.
        """
        self.base_url = base_url.strip()
        self.output_file = Path(output_file)
        self.session = requests.Session()

        