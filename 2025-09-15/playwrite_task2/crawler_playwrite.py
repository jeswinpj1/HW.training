# import random
# from playwright.sync_api import sync_playwright

# BASE = "https://www.dubizzle.com.bh/en"
# USER_AGENTS_FILE = "/home/user/HW.training/2025-09-12/user_agents.txt"


# def load_user_agents():
#     """Read user agents from file"""
#     with open(USER_AGENTS_FILE, "r") as f:
#         agents = [line.strip() for line in f if line.strip()]
#     return agents


# def get_random_user_agent():
#     agents = load_user_agents()
#     return random.choice(agents) if agents else None


# def crawl_categories():
#     with sync_playwright() as p:
#         # pick random user agent
#         ua = get_random_user_agent()
#         print(f"Using User-Agent: {ua}")

#         browser = p.firefox.launch(headless=False)
#         context = browser.new_context(user_agent=ua)
#         page = context.new_page()

#         print("Visiting:", BASE)
#         page.goto(BASE, timeout=60000)
#         page.wait_for_load_state("networkidle")

#         # scroll to load all categories
#         page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#         page.wait_for_timeout(2000)

#         categories = {}

#         # main categories (example: Vehicles, Property, Jobs...)
#         main_cats = page.query_selector_all("//div[contains(., 'Popular Categories')]//h2")
#         for main_cat in main_cats:
#             main_text = main_cat.inner_text().strip()
#             print(f"\nMain Category: {main_text}")

#             # find subcategories under each main category
#             sub_xpath = f"//div[contains(., '{main_text}')]//a"
#             sub_links = page.query_selector_all(sub_xpath)

#             subs = []
#             for sub in sub_links:
#                 sub_text = sub.inner_text().strip()
#                 sub_href = sub.get_attribute("href")
#                 if sub_text and sub_href:
#                     subs.append({"text": sub_text, "url": sub_href})
#                     print(f"   └── {sub_text} → {sub_href}")

#             categories[main_text] = subs

#         browser.close()
#         return categories


# if __name__ == "__main__":
#     data = crawl_categories()
#     print("\n Final Data:", data)



# import os
# import json
# import random
# import time
# from urllib.parse import urljoin
# from playwright.sync_api import sync_playwright
# from playwright_stealth import stealth_sync

# # ---------- Config (edit these) ----------
# BASE = "https://www.dubizzle.com.bh/en"
# USER_AGENTS_FILE = "/home/user/HW.training/2025-09-12/user_agents.txt"
# OUTPUT_DIR = "output"
# CATEGORIES_FILE = os.path.join(OUTPUT_DIR, "categories.json")
# ERROR_SCREEN = os.path.join(OUTPUT_DIR, "error_screenshot.png")
# ERROR_HTML = os.path.join(OUTPUT_DIR, "error_page.html")

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # ---------- Helper functions ----------
# def load_user_agents(path):
#     """Read user agents from file."""
#     if not os.path.exists(path):
#         return []
#     with open(path, "r", encoding="utf-8") as f:
#         return [line.strip() for line in f if line.strip()]

# def pick_random(seq, default=None):
#     """Picks a random item from a sequence."""
#     return random.choice(seq) if seq else default

# def absolute(url):
#     """Converts a relative URL to an absolute one."""
#     if not url:
#         return url
#     if url.startswith("http://") or url.startswith("https://"):
#         return url
#     return urljoin(BASE, url)

# # ---------- Main Crawler Logic ----------
# def crawl(user_agent=None):
#     """
#     Performs a single crawl attempt to get categories.
#     Returns a list of dictionaries if successful, otherwise an empty list.
#     """
#     print(f"Attempting to crawl with UA: {user_agent[:50]}...")
    
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
        
#         context_args = {
#             "user_agent": user_agent,
#             "viewport": {"width": 1280, "height": 720},
#             "locale": "en-US",
#         }
        
#         context = browser.new_context(**context_args)
        
#         # Apply playwright-stealth to the context
#         stealth_sync(context)
        
#         page = context.new_page()

#         try:
#             page.goto(BASE, timeout=60000, wait_until="domcontentloaded")
            
#             if "error" in page.url() or not page.content():
#                 print(" Detected error page or blank content. Aborting this attempt.")
#                 return []
            
#             page.wait_for_selector(
#                 "//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'popular categories')]",
#                 timeout=20000
#             )

#             page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#             time.sleep(random.uniform(2.0, 4.0))
            
#             # Extract data
#             results = []
#             container = page.query_selector("//div[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'popular categories')]")
#             if container:
#                 blocks = container.query_selector_all(".//div")
#                 for block in blocks:
#                     heading_el = block.query_selector(".//h1 | .//h2 | .//h3")
#                     if not heading_el: continue
#                     main_text = (heading_el.inner_text() or "").strip()
#                     if not main_text: continue
                    
#                     subs = []
#                     anchors = block.query_selector_all(".//a")
#                     for a in anchors:
#                         text = (a.inner_text() or "").strip()
#                         href = a.get_attribute("href")
#                         href = absolute(href)
#                         if text and href and "/en/" in href:
#                             subs.append({"text": text, "url": href})
                    
#                     if subs:
#                         results.append({"main_category": main_text, "sub_categories": subs})
            
#             return results

#         except Exception as e:
#             print(f"An error occurred during crawl: {e}")
#             try:
#                 page.screenshot(path=ERROR_SCREEN, full_page=True)
#                 with open(ERROR_HTML, "w", encoding="utf-8") as fh:
#                     fh.write(page.content() or "")
#             except Exception as se:
#                 print(f"Failed to save debug files: {se}")
#             return []
#         finally:
#             browser.close()

# def main():
#     """Manages the crawl attempts with user-agent rotation."""
#     user_agents = load_user_agents(USER_AGENTS_FILE)
    
#     for i in range(3):
#         ua = pick_random(user_agents)
#         result = crawl(user_agent=ua)
#         if result:
#             print(" Successfully found categories. Saving now.")
#             with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
#                 json.dump(result, f, ensure_ascii=False, indent=2)
#             print("Saved categories to", CATEGORIES_FILE)
#             return
#         else:
#             print(f"No data this attempt. Trying next... (Attempt {i+1}/3)")
#             time.sleep(random.uniform(3, 5))

#     print("No categories found after all attempts. See error files for clues.")

# if __name__ == "__main__":
#     main()



# import asyncio
# from playwright.async_api import async_playwright
# import json
# import random
# from playwright_stealth import stealth_async

# async def scrape_dubizzle():
#     data = {}
#     async with async_playwright() as p:
#         # Launch a new browser instance in headful mode (visible)
#         browser = await p.chromium.launch(headless=False)
        
#         # List of user agents to rotate
#         user_agents = [
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
#             "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
#         ]
#         user_agent = random.choice(user_agents)

#         # Create a new browser context with a random user agent and a standard viewport size
#         context = await browser.new_context(
#             user_agent=user_agent,
#             viewport={'width': 1920, 'height': 1080}
#         )
#         page = await context.new_page()

#         # Apply the stealth features to the page to hide bot fingerprints
#         await stealth_async(page)
        
#         try:
#             print("Navigating to the Dubizzle homepage...")
#             await page.goto("https://www.dubizzle.com.bh/en/")
            
#             # Add a random, human-like delay
#             await asyncio.sleep(random.uniform(3, 7))

#             try:
#                 print("Looking for main categories...")
#                 # Increase timeout as the site might be slow for suspected bots
#                 await page.wait_for_selector('//div[contains(@class, "CategoryTile_container__")]', timeout=30000)
#                 category_tiles = await page.locator('//div[contains(@class, "CategoryTile_container__")]').all()
#                 print(f"Found {len(category_tiles)} main categories.")
#             except Exception as e:
#                 print(f"Error: Could not find main categories. The site might be blocking us. Error details: {e}")
#                 return

#             # Loop through each main category tile
#             for tile in category_tiles:
#                 try:
#                     category_name_element = tile.locator('//span')
#                     category_name = await category_name_element.inner_text()
#                     category_link_element = tile.locator('a')
#                     category_url = await category_link_element.get_attribute('href')

#                     if category_name and category_url:
#                         print(f"\nScraping category: {category_name}")
#                         data[category_name] = {}
                        
#                         # Navigate to the category page
#                         await page.goto(f"https://www.dubizzle.com.bh{category_url}")
#                         await page.wait_for_load_state('domcontentloaded')
#                         await asyncio.sleep(random.uniform(2, 5)) # Add a delay

#                         # Use another try-except block for subcategories
#                         try:
#                             await page.wait_for_selector('//div[contains(@class, "SubCategoryTile_container__")]', timeout=20000)
#                             sub_category_tiles = await page.locator('//div[contains(@class, "SubCategoryTile_container__")]').all()
#                             print(f"  Found {len(sub_category_tiles)} sub-categories.")
#                         except Exception:
#                             print(f"  Warning: No sub-categories found for {category_name}.")
#                             continue

#                         # Loop through subcategories
#                         for sub_tile in sub_category_tiles:
#                             try:
#                                 sub_category_name = await sub_tile.locator('span').inner_text()
#                                 sub_category_link_element = sub_tile.locator('a')
#                                 sub_category_url = await sub_category_link_element.get_attribute('href')

#                                 if sub_category_name and sub_category_url:
#                                     print(f"    Scraping sub-category: {sub_category_name}")
#                                     data[category_name][sub_category_name] = []

#                                     # Navigate to the product listing page
#                                     await page.goto(f"https://www.dubizzle.com.bh{sub_category_url}")
#                                     await page.wait_for_load_state('domcontentloaded')
#                                     await asyncio.sleep(random.uniform(2, 5))

#                                     try:
#                                         product_locators = await page.locator('//a[contains(@class, "ListingCard_listingCard__")]').all()
                                        
#                                         urls = [await locator.get_attribute('href') for locator in product_locators]
#                                         data[category_name][sub_category_name].extend(urls)
#                                         print(f"      Found {len(urls)} product URLs.")
#                                     except Exception:
#                                         print("      Warning: No product listings found on this page.")

#                             except Exception as e:
#                                 print(f"      Error while processing a sub-category: {e}")

#                 except Exception as e:
#                     print(f"Error while processing main category: {e}")

#         except Exception as e:
#             print(f"A major error occurred during the scraping process: {e}")
#         finally:
#             await browser.close()
#             print("\nBrowser closed.")
    
#     with open('dubizzle_data_simple.json', 'w') as f:
#         json.dump(data, f, indent=4)
#         print("Scraping complete. Data saved to 'dubizzle_data_simple.json'")

# if __name__ == "__main__":
#     asyncio.run(scrape_dubizzle())





import asyncio
from playwright.async_api import async_playwright
import json
import random
from playwright_stealth import stealth_async

async def scrape_dubizzle():
    data = {}
    async with async_playwright() as p:
        # Launch a new browser instance in headful mode (visible)
        browser = await p.chromium.launch(headless=False)
        
        # A list of user agents to rotate
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        ]
        user_agent = random.choice(user_agents)

        # Create a new browser context with a random user agent, a standard viewport size, and geolocation
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            geolocation={'latitude': 26.0667, 'longitude': 50.5577}, # Example: Manama, Bahrain
            permissions=['geolocation']
        )
        page = await context.new_page()

        # Apply the stealth features to the page to hide bot fingerprints
        await stealth_async(page)
        
        try:
            print("Navigating to the Dubizzle homepage...")
            await page.goto("https://www.dubizzle.com.bh/en/")
            
            # Add a random, human-like delay
            await asyncio.sleep(random.uniform(3, 7))

            # Correct way to simulate a brief, natural scroll down the page
            scroll_by = random.randint(100, 300)
            await page.evaluate(f"window.scrollBy(0, {scroll_by})")
            await asyncio.sleep(random.uniform(1, 2))

            try:
                print("Looking for main categories...")
                await page.wait_for_selector('//div[contains(@class, "CategoryTile_container__")]', timeout=90000)
                category_tiles = await page.locator('//div[contains(@class, "CategoryTile_container__")]').all()
                print(f"Found {len(category_tiles)} main categories.")
            except Exception as e:
                print(f"Error: Could not find main categories. The site might be blocking us. Error details: {e}")
                return

            # Loop through each main category tile
            for tile in category_tiles:
                try:
                    category_name_element = tile.locator('//span')
                    category_name = await category_name_element.inner_text()
                    category_link_element = tile.locator('a')
                    category_url = await category_link_element.get_attribute('href')

                    if category_name and category_url:
                        print(f"\nScraping category: {category_name}")
                        data[category_name] = {}
                        
                        # Simulate human-like mouse movement and click
                        await page.locator(f'a[href="{category_url}"]').click()
                        
                        await page.wait_for_load_state('domcontentloaded')
                        await asyncio.sleep(random.uniform(2, 5))

                        try:
                            # Scroll to make sure all elements are visible
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(random.uniform(1, 2))

                            await page.wait_for_selector('//div[contains(@class, "SubCategoryTile_container__")]', timeout=20000)
                            sub_category_tiles = await page.locator('//div[contains(@class, "SubCategoryTile_container__")]').all()
                            print(f"  Found {len(sub_category_tiles)} sub-categories.")
                        except Exception:
                            print(f"  Warning: No sub-categories found for {category_name}.")
                            continue

                        # Loop through subcategories
                        for sub_tile in sub_category_tiles:
                            try:
                                sub_category_name = await sub_tile.locator('span').inner_text()
                                sub_category_link_element = sub_tile.locator('a')
                                sub_category_url = await sub_category_link_element.get_attribute('href')

                                if sub_category_name and sub_category_url:
                                    print(f"    Scraping sub-category: {sub_category_name}")
                                    data[category_name][sub_category_name] = []

                                    # Navigate to the product listing page with a human-like click
                                    await page.locator(f'a[href="{sub_category_url}"]').click()
                                    await page.wait_for_load_state('domcontentloaded')
                                    await asyncio.sleep(random.uniform(2, 5))

                                    try:
                                        # Scroll to load all products on the page
                                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                        await asyncio.sleep(random.uniform(1, 2))
                                        
                                        product_locators = await page.locator('//a[contains(@class, "ListingCard_listingCard__")]').all()
                                        
                                        urls = [await locator.get_attribute('href') for locator in product_locators]
                                        data[category_name][sub_category_name].extend(urls)
                                        print(f"      Found {len(urls)} product URLs.")
                                    except Exception:
                                        print("      Warning: No product listings found on this page.")

                            except Exception as e:
                                print(f"      Error while processing a sub-category: {e}")

                except Exception as e:
                    print(f"Error while processing main category: {e}")

        except Exception as e:
            print(f"A major error occurred during the scraping process: {e}")
        finally:
            await browser.close()
            print("\nBrowser closed.")
    
    with open('dubizzle_data_simple.json', 'w') as f:
        json.dump(data, f, indent=4)
        print("Scraping complete. Data saved to 'dubizzle_data_simple.json'")

if __name__ == "__main__":
    asyncio.run(scrape_dubizzle())