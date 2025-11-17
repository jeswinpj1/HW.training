import requests
from lxml import html
import urllib.parse
import time

# --- Configuration ---
BASE_URL = "https://www.sephora.sg"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
POLITE_DELAY = 2  # Wait 2 seconds between pages to be safe

# --- XPaths (The "Map" to find elements in the HTML) ---
MAIN_CATEGORY_BLOCKS_XPATH = '//div[contains(@class, "menu-dropdown")][.//div[contains(@class, "categories-dropdown-container")]]'
MAIN_CATEGORY_NAME_XPATH = './/div[contains(@class, "dropdown-trigger")]//div[contains(@class, "text-container")]/text()'
SUB_CATEGORY_LINKS_XPATH = './/div[contains(@class, "categories-dropdown-container")]//a[starts-with(@href, "/categories/")]'
PRODUCT_URL_XPATH = '//a[contains(@class, "product-card-description")]/@href'
NEXT_PAGE_XPATH = '//a[contains(@class, "pagination-item") and contains(@class, "next-page")]/@href'


def get_all_product_links(category_url):
    """
    This function visits a Category page (e.g., "Hair > Shampoo").
    It finds product links, then clicks "Next Page" and repeats until done.
    """
    # Use a set to avoid saving duplicate product links
    collected_links = set()
    current_page_to_scrape = category_url

    # LOOP: Keep going as long as we have a URL to scrape
    while current_page_to_scrape != None:
        print(f"    -> Scraping page: {current_page_to_scrape}")
        
        # 1. Download the page
        time.sleep(POLITE_DELAY) # Wait a bit
        response = requests.get(current_page_to_scrape, headers=HEADERS)

        # 2. Check if the download was successful
        if response.status_code == 200:
            tree = html.fromstring(response.content)

            # 3. Extract Product URLs on this page
            product_paths = tree.xpath(PRODUCT_URL_XPATH)
            
            if not product_paths:
                print("    -> WARNING: Found 0 product URLs on this page.")

            for path in product_paths:
                full_link = urllib.parse.urljoin(BASE_URL, path)
                collected_links.add(full_link) # Add to set

            # 4. Look for the "Next Page" button
            next_button = tree.xpath(NEXT_PAGE_XPATH)

            if len(next_button) > 0:
                next_extension = next_button[0]
                current_page_to_scrape = urllib.parse.urljoin(BASE_URL, next_extension)
            else:
                # No next page found.
                print("    -> Reached the last page for this sub-category.")
                current_page_to_scrape = None
        
        else:
            print(f"    Error: Page status was {response.status_code}. Stopping this sub-category.")
            current_page_to_scrape = None

    # Convert the set back to a list for the JSON file
    return list(collected_links)


def main():
    print("--- Starting Scraper ---")
    
    final_data = {}

    # 1. Get the Homepage
    response = requests.get(BASE_URL, headers=HEADERS)

    if response.status_code == 200:
        home_tree = html.fromstring(response.content)
        
        # 2. Find all Main Categories
        main_category_elements = home_tree.xpath(MAIN_CATEGORY_BLOCKS_XPATH)
        print(f"Found {len(main_category_elements)} main categories.")

        # LOOP: Go through every Main Category
        for main_element in main_category_elements:
            
            # Extract the name (e.g., "Hair")
            name_list = main_element.xpath(MAIN_CATEGORY_NAME_XPATH)
            
            if len(name_list) > 0:
                main_cat_name = name_list[0].strip()
                if not main_cat_name:
                    continue 

                print(f"\n[ Main Category: {main_cat_name} ]")
                final_data[main_cat_name] = {}

                # 3. Find Sub-Categories inside this Main Category
                sub_cat_links = main_element.xpath(SUB_CATEGORY_LINKS_XPATH)

                # LOOP: Go through every Sub-Category
                for link in sub_cat_links:
                    sub_name = link.text_content().strip()
                    sub_href = link.get('href')

                    # Filter: We only want deep links (e.g. /categories/makeup/face)
                    if sub_href and sub_href.count('/') >= 3:
                        full_sub_url = urllib.parse.urljoin(BASE_URL, sub_href)
                        print(f"  * Found Sub-Category: {sub_name}")

                        # 4. Go get the products for this sub-category!
                        product_list = get_all_product_links(full_sub_url)

                        final_data[main_cat_name][sub_name] = product_list
                        print(f"  * Saved {len(product_list)} products from '{sub_name}'.")
                        
                        # [DEBUG] BREAK REMOVED
            
            # [DEBUG] BREAK REMOVED

    else:
        print(f"Error: Could not load homepage. Status: {response.status_code}")

# Start the program
if __name__ == "__main__":
    main()