# import time
# import pandas as pd
# import re
# import concurrent.futures
# import logging
# import os
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# from webdriver_manager.chrome import ChromeDriverManager
# import requests

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class GoogleMapsScraper:
#     def __init__(self, headless=True, num_threads=1):
#         """Initialize the Google Maps scraper with browser settings."""
#         self.num_threads = num_threads
#         self.chrome_options = Options()
        
#         if headless:
#             self.chrome_options.add_argument("--headless=new")
        
#         # Basic Chrome options
#         self.chrome_options.add_argument("--disable-notifications")
#         self.chrome_options.add_argument("--disable-popup-blocking")
#         self.chrome_options.add_argument("--start-maximized")
#         self.chrome_options.add_argument("--no-sandbox")
#         self.chrome_options.add_argument("--disable-dev-shm-usage")
        
#         # Updated selectors for better compatibility with current Google Maps layout
#         self.selectors = {
#             'Name': ['h1.DUwDvf', 'h1.fontHeadlineLarge', 'h1[jsan*="fontHeadlineLarge"]'],
#             'address': ['button[data-item-id="address"] div.fontBodyMedium', 'button[data-item-id*="address"] span', 'div[jsan*="address"] span'],
#             'Website': ['a[data-item-id="authority"] div.fontBodyMedium', 'a[data-item-id*="website"] span', 'a[jsan*="website"] span'],
#             'Phone': ['button[data-item-id^="phone:tel:"] div.fontBodyMedium', 'button[data-item-id*="phone"] span', 'button[jsan*="phone"] span'],
#             'Reviews': ['div.F7nice span[aria-label$="reviews"]', 'span[aria-label*="reviews"]', 'span[jsan*="reviewCount"]'],
#             'Rating': ['div.F7nice span[aria-hidden="true"]', 'span[aria-hidden="true"][role="text"]', 'span[aria-label*="stars"]'],
#             'hours': ['div.t39EBf table.eK4R0e tbody', 'table.eK4R0e tbody', 'div[jsan*="hours"] table tbody'],
#             'Category': ['button.DkEaL', 'span.DkEaL', 'button[jsan*="categoryText"]'],
#             'Description': ['div.WeS02d div.PYvSYb', 'div.PYvSYb', 'div[data-attrid="description"]'],
#             'Status': ['div.o0Svhf span.ZDu9vd', 'span.ZDu9vd', 'span[jsan*="operationStatus"]'],
#         }
        
#         # The driver is initialized in open_browser() method
#         self.driver = None
    
#     def open_browser(self):
#         """Open a new browser instance with automatic driver installation."""
#         try:
#             # Use webdriver-manager to automatically download the correct driver version
#             service = Service(ChromeDriverManager().install())
#             driver = webdriver.Chrome(service=service, options=self.chrome_options)
#             driver.set_page_load_timeout(30)  # Increased timeout for better reliability
#             return driver
#         except Exception as e:
#             logger.error(f"Failed to initialize browser: {e}")
#             raise
    
#     def navigate_to_google_maps(self, driver):
#         """Navigate to Google Maps website with better error handling."""
#         try:
#             driver.get("https://www.google.com/maps")
            
#             # Use a longer wait time for reliability
#             WebDriverWait(driver, 15).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "input#searchboxinput"))
#             )
            
#             # Handle potential cookie consent dialog
#             try:
#                 # Try multiple possible selectors for cookie buttons
#                 cookie_selectors = [
#                     "//button[contains(., 'Accept')]",
#                     "//button[contains(., 'I agree')]",
#                     "//button[contains(., 'Agree')]",
#                     "//button[contains(@aria-label, 'Accept')]",
#                     "//button[contains(@aria-label, 'Accept all')]"
#                 ]
                
#                 for selector in cookie_selectors:
#                     buttons = driver.find_elements(By.XPATH, selector)
#                     if buttons:
#                         buttons[0].click()
#                         logger.info("Clicked on cookie consent button")
#                         time.sleep(1)
#                         break
#             except Exception as e:
#                 logger.debug(f"No cookie dialog or couldn't handle it: {e}")
            
#             return True
#         except Exception as e:
#             logger.error(f"Error navigating to Google Maps: {e}")
#             # Save screenshot for debugging
#             self.save_screenshot(driver, "navigation_error")
#             return False
    
#     def search_place(self, driver, query):
#         """Search for a specific place on Google Maps with better error handling."""
#         try:
#             logger.info(f"Searching for: {query}")
            
#             # Find the search box and enter the query
#             search_box = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "input#searchboxinput"))
#             )
            
#             # Clear the search box and enter the new query
#             search_box.clear()
#             search_box.send_keys(query)
#             search_box.send_keys(Keys.ENTER)
            
#             # Wait for search results - longer wait time
#             time.sleep(5)
            
#             # Check for "No results found" message
#             try:
#                 no_results = driver.find_elements(By.XPATH, "//div[contains(text(), 'No results found')]")
#                 if no_results:
#                     logger.warning(f"No results found for query: {query}")
#                     return False
#             except:
#                 pass
                
#             # See if we're in list view (multiple results)
#             result_items = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
#             if result_items:
#                 logger.info(f"Found search results list with {len(result_items)} items")
#                 return True
#             else:
#                 # Check if we're already in detail view (single result)
#                 detail_indicators = [
#                     "h1.DUwDvf",
#                     "h1.fontHeadlineLarge",
#                     "button[data-item-id='address']"
#                 ]
                
#                 for selector in detail_indicators:
#                     elements = driver.find_elements(By.CSS_SELECTOR, selector)
#                     if elements:
#                         logger.info("Direct navigation to single result")
#                         return True
                
#                 logger.warning(f"Could not find search results for query: {query}")
#                 return False
            
#         except Exception as e:
#             logger.error(f"Error searching for place '{query}': {e}")
#             self.save_screenshot(driver, f"search_error_{query.replace(' ', '_')}")
#             return False
    
#     def extract_listing_urls(self, driver, total_desired=10):
#         """Extract URLs of listings from the search results page."""
#         listing_urls = []
#         previously_found = 0
#         stuck_count = 0
#         max_stuck_count = 5
#         max_attempts = 15
        
#         logger.info(f"Attempting to extract {total_desired} listing URLs")
        
#         for attempt in range(max_attempts):
#             if len(listing_urls) >= total_desired:
#                 break
                
#             # Extract all visible listing URLs
#             listing_elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            
#             # Add new unique URLs
#             for element in listing_elements:
#                 try:
#                     url = element.get_attribute("href")
#                     if url and url not in listing_urls:
#                         listing_urls.append(url)
#                 except Exception as e:
#                     logger.debug(f"Error extracting URL: {e}")
            
#             current_count = len(listing_urls)
#             logger.debug(f"Found {current_count} unique listing URLs (attempt {attempt+1})")
            
#             if current_count >= total_desired:
#                 break

#             if current_count == previously_found:
#                 stuck_count += 1
#                 if stuck_count >= max_stuck_count:
#                     logger.info(f"Stopped at {current_count} listings after {stuck_count} attempts with no new results")
#                     break
#             else:
#                 stuck_count = 0

#             # Scroll to load more results
#             try:
#                 # Find the results container and scroll
#                 scroll_targets = [
#                     "div[role='feed']",  # Main results feed
#                     ".m6QErb[aria-label]",  # Alternative results container
#                     ".m6QErb.DxyBCb"  # Another variation
#                 ]
                
#                 for target in scroll_targets:
#                     elements = driver.find_elements(By.CSS_SELECTOR, target)
#                     if elements:
#                         # JavaScript scroll within the container
#                         driver.execute_script(
#                             "arguments[0].scrollTo({top: arguments[0].scrollHeight, behavior: 'smooth'});", 
#                             elements[0]
#                         )
#                         break
#                 else:
#                     # If no specific container found, try general page scroll
#                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
#                 # Wait for new results to load
#                 time.sleep(2)
#             except Exception as e:
#                 logger.debug(f"Error while scrolling: {e}")
#                 break  # Break on scroll error

#             previously_found = current_count

#         logger.info(f"Extracted {len(listing_urls)} listing URLs (requested {total_desired})")
        
#         # Return only the requested number of URLs
#         return listing_urls[:total_desired]
    
#     def format_phone_number(self, phone):
#         """Format phone number by removing unwanted characters."""
#         if not phone:
#             return ""
#         # Keep only digits and some special characters
#         return phone.strip()
    
#     def parse_address(self, address_text):
#         """Parse address into components."""
#         if not address_text:
#             return {
#                 "Street": "",
#                 "City": "",
#                 "State": "",
#                 "Zip": "",
#                 "Country": ""
#             }
        
#         try:
#             # Simple parsing - would need refinement for different countries
#             parts = address_text.split(',')
            
#             address_components = {
#                 "Street": parts[0].strip() if len(parts) > 0 else "",
#                 "City": parts[1].strip() if len(parts) > 1 else "",
#                 "State": "",
#                 "Zip": "",
#                 "Country": parts[-1].strip() if len(parts) > 2 else ""
#             }
            
#             # Try to extract state and zip from the third part if available
#             if len(parts) > 2:
#                 state_zip = parts[2].strip().split()
#                 address_components["State"] = state_zip[0] if len(state_zip) > 0 else ""
#                 address_components["Zip"] = state_zip[1] if len(state_zip) > 1 else ""
                
#             return address_components
            
#         except Exception as e:
#             logger.debug(f"Error parsing address '{address_text}': {e}")
#             return {
#                 "Street": address_text,
#                 "City": "",
#                 "State": "",
#                 "Zip": "",
#                 "Country": ""
#             }
    
#     def format_time(self, time_str):
#         """Format time string."""
#         if not time_str:
#             return ""
#         return time_str.strip()
    
#     def parse_hours(self, hours_text):
#         """Parse hours information into day-specific fields."""
#         days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#         hours_data = {day: "" for day in days}
        
#         if not hours_text:
#             return hours_data
        
#         try:
#             day_patterns = [
#                 rf"{day}:\s*(.*?)(?=;|$)" for day in days
#             ]
            
#             for i, pattern in enumerate(day_patterns):
#                 match = re.search(pattern, hours_text)
#                 if match:
#                     hours_data[days[i]] = match.group(1).strip()
            
#             return hours_data
            
#         except Exception as e:
#             logger.debug(f"Error parsing hours '{hours_text}': {e}")
#             return hours_data
    
#     def extract_image_url(self, driver):
#         """Extract main image URL for the listing."""
#         try:
#             # Look for main image in the interface
#             image_elements = driver.find_elements(By.CSS_SELECTOR, "button[jsaction*='pane.heroHeaderImage'] img")
#             if image_elements:
#                 return image_elements[0].get_attribute("src")
            
#             # Alternative image selectors
#             alt_selectors = [
#                 "div.ZKCDEc img",
#                 "div.RZ66Rb img",
#                 "img.Liguzb"
#             ]
            
#             for selector in alt_selectors:
#                 elements = driver.find_elements(By.CSS_SELECTOR, selector)
#                 if elements:
#                     return elements[0].get_attribute("src")
            
#             return ""
#         except Exception as e:
#             logger.debug(f"Error extracting image URL: {e}")
#             return ""
    
#     def check_internet_connection(self):
#         """Check if internet connection is available."""
#         try:
#             # Try to connect to Google's DNS server
#             requests.get("https://8.8.8.8", timeout=3)
#             return True
#         except:
#             return False
    
#     def extract_services_and_attributes(self, driver):
#         """Extract additional services and attributes from the listing."""
#         additional_data = {}
        
#         try:
#             # Look for service options sections
#             service_sections = driver.find_elements(
#                 By.XPATH, 
#                 "//h2[contains(text(), 'Service options') or contains(text(), 'Amenities') or contains(text(), 'Highlights')]/following-sibling::div[1]"
#             )
            
#             services = []
#             for section in service_sections:
#                 service_items = section.find_elements(By.CSS_SELECTOR, "span.mgr77e")
#                 for item in service_items:
#                     services.append(item.text.strip())
            
#             additional_data["Services"] = "; ".join(services) if services else ""
            
#             return additional_data
            
#         except Exception as e:
#             logger.debug(f"Error extracting services: {e}")
#             return {"Services": ""}
    
#     def scrape_single_listing(self, driver, url):
#         """Scrape data from a single listing URL."""
#         try:
#             logger.info(f"Processing listing URL: {url}")
            
#             # Navigate to the listing URL
#             driver.get(url)
#             time.sleep(3)  # Wait for page to load
            
#             # Try to detect if we're on a valid details page
#             valid_page = False
#             for name_selector in self.selectors['Name']:
#                 elements = driver.find_elements(By.CSS_SELECTOR, name_selector)
#                 if elements:
#                     valid_page = True
#                     break
            
#             if not valid_page:
#                 logger.warning(f"Not a valid listing page: {url}")
#                 self.save_screenshot(driver, "invalid_listing_page")
#                 return None
                
#             # Initialize item dictionary
#             item = {}
            
#             # Extract data for each field
#             for field, selector_list in self.selectors.items():
#                 value = None
                
#                 for selector in selector_list:
#                     if value:  # If we already found a value, break
#                         break
                        
#                     elements = driver.find_elements(By.CSS_SELECTOR, selector)
#                     if elements:
#                         if field == 'hours':
#                             # Special handling for hours
#                             hours_rows = elements[0].find_elements(By.CSS_SELECTOR, "tr")
#                             hours_data = []
                            
#                             for row in hours_rows:
#                                 day_elements = row.find_elements(By.CSS_SELECTOR, "th")
#                                 time_elements = row.find_elements(By.CSS_SELECTOR, "td")
                                
#                                 if day_elements and time_elements:
#                                     day = day_elements[0].text.strip()
#                                     time_text = time_elements[0].text.strip()
#                                     hours_data.append(f"{day}: {time_text}")
                            
#                             value = "; ".join(hours_data) if hours_data else None
#                         else:
#                             value = elements[0].text.strip()
                
#                 item[field] = value if value else ""
            
#             # Store the listing URL
#             item['URL'] = url
            
#             # Extract services and attributes
#             services_data = self.extract_services_and_attributes(driver)
#             item.update(services_data)
            
#             # Parse address components
#             address_components = self.parse_address(item.pop('address', ""))
#             item.update(address_components)
            
#             # Process phone number
#             item['Phone'] = self.format_phone_number(item.get('Phone', ""))
            
#             # Parse and format hours
#             hours_data = self.parse_hours(item.pop('hours', ""))
#             item.update(hours_data)
            
#             # Format review count
#             if item.get('Reviews'):
#                 item['Reviews'] = ''.join(filter(str.isdigit, item['Reviews']))
#                 try:
#                     item['Reviews'] = int(item['Reviews'])
#                 except ValueError:
#                     item['Reviews'] = 0
            
#             # Format rating
#             if item.get('Rating'):
#                 try:
#                     item['Rating'] = float(item['Rating'].replace(',', '.'))
#                 except ValueError:
#                     item['Rating'] = 0.0
            
#             # Extract image URL
#             item['Image_URL'] = self.extract_image_url(driver)
            
#             logger.info(f"Successfully scraped listing: {item.get('Name', url)}")
#             return item
            
#         except Exception as e:
#             logger.error(f"Error scraping listing {url}: {e}")
#             self.save_screenshot(driver, f"listing_error_{url.split('/')[-1]}")
#             return None
    
#     def save_screenshot(self, driver, filename):
#         """Save a screenshot for debugging purposes."""
#         try:
#             if not os.path.exists("debug_screenshots"):
#                 os.makedirs("debug_screenshots")
            
#             screenshot_path = f"debug_screenshots/{filename}_{int(time.time())}.png"
#             driver.save_screenshot(screenshot_path)
#             logger.info(f"Screenshot saved to {screenshot_path}")
#         except Exception as e:
#             logger.error(f"Failed to save screenshot: {e}")
    
#     def extract_details(self, driver, fields=None):
#         """Extract details about the place with improved selector handling."""
#         # If no specific fields are requested, extract all available fields
#         if fields is None:
#             fields = list(self.selectors.keys())
        
#         # Create a dictionary to store results
#         results = {}
        
#         # Save a screenshot before extraction for debugging
#         self.save_screenshot(driver, "before_extraction")
        
#         # Get the page source and create a BeautifulSoup object
#         page_source = driver.page_source
        
#         # Log a small portion of the page source for debugging
#         logger.debug(f"Page source preview: {page_source[:500]}...")
        
#         # Try both parsers for better compatibility
#         try:
#             soup = BeautifulSoup(page_source, 'lxml')
#         except:
#             soup = BeautifulSoup(page_source, 'html.parser')
        
#         # Sometimes we need to expand sections to see all data
#         try:
#             # Try to expand "About" section if it exists
#             about_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'About')]")
#             if about_buttons:
#                 about_buttons[0].click()
#                 time.sleep(1)
#                 logger.info("Expanded 'About' section")
                
#             # Try to expand hours if collapsed
#             hours_buttons = driver.find_elements(By.XPATH, 
#                 "//button[contains(., 'hours') or contains(@aria-label, 'hours') or contains(., 'Hours')]")
#             if hours_buttons:
#                 hours_buttons[0].click()
#                 time.sleep(1)
#                 logger.info("Expanded hours section")
                
#         except Exception as e:
#             logger.debug(f"Error expanding sections: {e}")
        
#         # Extract details for each requested field
#         for field in fields:
#             if field in self.selectors:
#                 # Try each selector for this field
#                 field_selectors = self.selectors[field]
#                 value_found = False
                
#                 for selector in field_selectors:
#                     if value_found:
#                         break
                        
#                     try:
#                         # First try with selenium for dynamic content
#                         elements = driver.find_elements(By.CSS_SELECTOR, selector)
#                         if elements:
#                             if field == 'hours':
#                                 # Special handling for hours
#                                 hours_data = []
#                                 rows = driver.find_elements(By.CSS_SELECTOR, f"{selector} tr")
#                                 for row in rows:
#                                     day_elements = row.find_elements(By.CSS_SELECTOR, "th")
#                                     hour_elements = row.find_elements(By.CSS_SELECTOR, "td")
                                    
#                                     day = day_elements[0].text.strip() if day_elements else ""
#                                     hours = hour_elements[0].text.strip() if hour_elements else ""
                                    
#                                     if day and hours:
#                                         hours_data.append(f"{day}: {hours}")
                                
#                                 if hours_data:
#                                     results[field] = "; ".join(hours_data)
#                                     value_found = True
#                             else:
#                                 # For other fields, just get the text
#                                 text = elements[0].text.strip()
#                                 if text:
#                                     results[field] = text
#                                     value_found = True
#                                     logger.debug(f"Found {field} using selector: {selector}")
#                     except Exception as e:
#                         logger.debug(f"Error with Selenium extraction for {field} using {selector}: {e}")
                
#                 # If selenium didn't find anything, try with BeautifulSoup
#                 if not value_found:
#                     for selector in field_selectors:
#                         try:
#                             element = soup.select_one(selector)
#                             if element:
#                                 if field == 'hours':
#                                     # Special handling for hours
#                                     hours_data = []
#                                     rows = element.select('tr')
#                                     for row in rows:
#                                         day = row.select_one('th').text.strip() if row.select_one('th') else ""
#                                         hours = row.select_one('td').text.strip() if row.select_one('td') else ""
#                                         if day and hours:
#                                             hours_data.append(f"{day}: {hours}")
                                    
#                                     if hours_data:
#                                         results[field] = "; ".join(hours_data)
#                                         value_found = True
#                                 else:
#                                     # For other fields, just get the text
#                                     text = element.text.strip()
#                                     if text:
#                                         results[field] = text
#                                         value_found = True
#                                         logger.debug(f"Found {field} using BS4 selector: {selector}")
#                                         break
#                         except Exception as e:
#                             logger.debug(f"Error with BS4 extraction for {field} using {selector}: {e}")
                
#                 # If we still couldn't find a value, try a more aggressive approach with XPath
#                 if not value_found and field in ['Name', 'address', 'Phone', 'Website']:
#                     try:
#                         # Use more generic XPath expressions for common fields
#                         xpath_patterns = {
#                             'Name': "//h1",
#                             'address': "//*[contains(text(), 'Address') or contains(@aria-label, 'address')]/following::*[1]",
#                             'Phone': "//*[contains(text(), 'Phone') or contains(@aria-label, 'phone')]/following::*[1]",
#                             'Website': "//*[contains(text(), 'Website') or contains(@aria-label, 'website')]/following::*[1]"
#                         }
                        
#                         if field in xpath_patterns:
#                             elements = driver.find_elements(By.XPATH, xpath_patterns[field])
#                             if elements:
#                                 text = elements[0].text.strip()
#                                 if text:
#                                     results[field] = text
#                                     value_found = True
#                                     logger.debug(f"Found {field} using XPath fallback")
#                     except Exception as e:
#                         logger.debug(f"Error with XPath fallback for {field}: {e}")
                
#                 # If still no value found, set to None
#                 if not value_found:
#                     results[field] = None
#                     logger.debug(f"No value found for {field}")
#             else:
#                 results[field] = None
        
#         # Check if we got any actual data
#         data_found = any(v for v in results.values() if v is not None)
        
#         if not data_found:
#             logger.warning("No data was extracted from the page")
#             self.save_screenshot(driver, "no_data_extracted")
#         else:
#             logger.info(f"Successfully extracted data: {', '.join(k for k, v in results.items() if v is not None)}")
        
#         return results
    
#     def process_query_listings(self, driver, query, max_listings=5, fields=None):
#         """Process multiple listing results for a search query."""
#         results = []
        
#         try:
#             # Search for the query
#             if not self.search_place(driver, query):
#                 logger.warning(f"No search results found for '{query}'")
#                 return results
            
#             # Check if we got redirected to a single business page
#             # This happens when Google Maps finds an exact match
#             single_result = False
#             for name_selector in self.selectors['Name']:
#                 elements = driver.find_elements(By.CSS_SELECTOR, name_selector)
#                 if elements:
#                     single_result = True
#                     break
            
#             if single_result:
#                 logger.info(f"Direct match found for '{query}', extracting single result")
#                 details = self.extract_details(driver, fields)
#                 if details:
#                     details["Search Query"] = query
#                     results.append(details)
#             else:
#                 # We're in search results view, extract multiple listings
#                 logger.info(f"Extracting up to {max_listings} listings for '{query}'")
                
#                 # Extract listing URLs
#                 listing_urls = self.extract_listing_urls(driver, max_listings)
                
#                 if not listing_urls:
#                     logger.warning(f"No listing URLs found for '{query}'")
#                     return results
                
#                 # Process each listing URL
#                 for i, url in enumerate(listing_urls):
#                     logger.info(f"Processing listing {i+1}/{len(listing_urls)}: {url}")
                    
#                     # For each listing we need to open a new tab
#                     # Opening in same tab would make it hard to go back to results
#                     driver.execute_script("window.open('');")
#                     driver.switch_to.window(driver.window_handles[-1])
                    
#                     try:
#                         # Extract details from this listing
#                         listing_data = self.scrape_single_listing(driver, url)
                        
#                         if listing_data:
#                             listing_data["Search Query"] = query
#                             results.append(listing_data)
#                     except Exception as e:
#                         logger.error(f"Error processing listing {url}: {e}")
                    
#                     # Close this tab and return to the original tab
#                     driver.close()
#                     driver.switch_to.window(driver.window_handles[0])
            
#             return results
            
#         except Exception as e:
#             logger.error(f"Error processing query listings for '{query}': {e}")
#             self.save_screenshot(driver, f"process_error_{query.replace(' ', '_')}")
#             return results
    
#     def scrape_multiple_queries_with_listings(self, queries, max_listings_per_query=5, fields=None):
#         """
#         Scrape multiple queries, each with multiple listings.
        
#         Args:
#             queries (list): List of search queries.
#             max_listings_per_query (int): Maximum listings to extract per query.
#             fields (list): Fields to extract for each listing.
            
#         Returns:
#             pandas.DataFrame: DataFrame with all extracted listings.
#         """
#         all_results = []
        
#         # Multi-threaded approach
#         if self.num_threads > 1:
#             # Define a worker function for thread pool
#             def process_query(query):
#                 try:
#                     driver = self.open_browser()
                    
#                     if not self.navigate_to_google_maps(driver):
#                         logger.error(f"Failed to navigate to Google Maps for '{query}'")
#                         return []
                    
#                     results = self.process_query_listings(driver, query, max_listings_per_query, fields)
#                     return results
#                 except Exception as e:
#                     logger.error(f"Thread error processing '{query}': {e}")
#                     return []
#                 finally:
#                     if driver:
#                         driver.quit()
            
#             # Use ThreadPoolExecutor for parallel processing
#             with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
#                 # Submit all queries to the executor
#                 future_results = list(executor.map(process_query, queries))
                
#                 # Flatten the list of results
#                 for results in future_results:
#                     all_results.extend(results)
        
#         # Single-threaded approach
#         else:
#             driver = None
#             try:
#                 driver = self.open_browser()
                
#                 if not self.navigate_to_google_maps(driver):
#                     logger.error("Failed to navigate to Google Maps, aborting all queries")
#                     return pd.DataFrame()
                
#                 # Process each query
#                 for query in queries:
#                     logger.info(f"Processing query: {query}")
                    
#                     # Check internet connection before each query
#                     if not self.check_internet_connection():
#                         logger.error("Internet connection lost, retrying...")
#                         time.sleep(10)  # Wait and try again
#                         if not self.check_internet_connection():
#                             logger.error("Internet connection still unavailable, skipping query")
#                             continue
                    
#                     # Get results for this query
#                     query_results = self.process_query_listings(driver, query, max_listings_per_query, fields)
#                     all_results.extend(query_results)
                    
#                     # Add a delay between queries to avoid rate limiting
#                     time.sleep(3)
            
#             except Exception as e:
#                 logger.error(f"Error in scraping process: {e}")
#             finally:
#                 if driver:
#                     driver.quit()
        
#         # Convert results to DataFrame
#         if all_results:
#             df = pd.DataFrame(all_results)
#             logger.info(f"Successfully scraped {len(df)} listings across {len(queries)} queries")
#             return df
#         else:
#             logger.warning("No results found for any query")
#             return pd.DataFrame()
    
#     def scrape_to_csv(self, queries, output_file, max_listings_per_query=5, fields=None):
#         """
#         Scrape data and save directly to CSV file.
        
#         Args:
#             queries (list): List of search queries.
#             output_file (str): Path to output CSV file.
#             max_listings_per_query (int): Maximum listings to extract per query.
#             fields (list): Fields to extract for each listing.
#         """
#         try:
#             # Scrape data
#             df = self.scrape_multiple_queries_with_listings(queries, max_listings_per_query, fields)
            
#             if not df.empty:
#                 # Save to CSV
#                 df.to_csv(output_file, index=False, encoding='utf-8-sig')
#                 logger.info(f"Data successfully saved to {output_file}")
#                 return True
#             else:
#                 logger.warning(f"No data to save to {output_file}")
#                 return False
                
#         except Exception as e:
#             logger.error(f"Error saving data to CSV: {e}")
#             return False

# # Main execution block for the Google Maps Scraper
# if __name__ == "__main__":
#     import argparse
    
#     # Set up command line argument parsing
#     parser = argparse.ArgumentParser(description='Google Maps Scraper')
#     parser.add_argument('--queries', '-q', type=str, nargs='+', required=True, help='Search queries to scrape')
#     parser.add_argument('--output', '-o', type=str, default='google_maps_results.csv', help='Output CSV file name')
#     parser.add_argument('--max-listings', '-m', type=int, default=5, help='Maximum listings per query')
#     parser.add_argument('--headless', action='store_true', help='Run in headless mode')
#     parser.add_argument('--threads', '-t', type=int, default=1, help='Number of threads to use')
    
#     args = parser.parse_args()
    
#     # Initialize the scraper
#     scraper = GoogleMapsScraper(headless=args.headless, num_threads=args.threads)
    
#     # Log the start of scraping
#     logger.info(f"Starting scraping with {args.threads} thread(s), headless mode: {args.headless}")
#     logger.info(f"Scraping {len(args.queries)} queries with up to {args.max_listings} listings per query")
#     logger.info(f"Output will be saved to: {args.output}")
    
#     # Define the fields to extract
#     fields = [
#         'Name', 'Street', 'City', 'State', 'Zip', 'Country',
#         'Phone', 'Website', 'Rating', 'Reviews', 'Category',
#         'Status', 'Description', 'Services', 'Image_URL',
#         'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
#     ]
    
#     try:
#         # Start scraping
#         success = scraper.scrape_to_csv(args.queries, args.output, args.max_listings, fields)
        
#         if success:
#             logger.info(f"Scraping completed successfully. Results saved to {args.output}")
#         else:
#             logger.error("Scraping completed with errors. Check the logs for details.")
    
#     except KeyboardInterrupt:
#         logger.info("Scraping interrupted by user.")
#     except Exception as e:
#         logger.error(f"An error occurred during scraping: {e}")
#     finally:
#         logger.info("Scraping process finished.")
import time
import pandas as pd
import re
import concurrent.futures
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    def __init__(self, headless=True, num_threads=1):
        """Initialize the Google Maps scraper with browser settings."""
        self.num_threads = num_threads
        self.chrome_options = Options()
        
        if headless:
            self.chrome_options.add_argument("--headless=new")
        
        # Basic Chrome options
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("--disable-popup-blocking")
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Updated selectors for better compatibility with current Google Maps layout
        self.selectors = {
            'Name': ['h1.DUwDvf', 'h1.fontHeadlineLarge', 'h1[jsan*="fontHeadlineLarge"]'],
            'address': ['button[data-item-id="address"] div.fontBodyMedium', 'button[data-item-id*="address"] span', 'div[jsan*="address"] span'],
            'Website': ['a[data-item-id="authority"] div.fontBodyMedium', 'a[data-item-id*="website"] span', 'a[jsan*="website"] span'],
            'Phone': ['button[data-item-id^="phone:tel:"] div.fontBodyMedium', 'button[data-item-id*="phone"] span', 'button[jsan*="phone"] span'],
            'Reviews': ['div.F7nice span[aria-label$="reviews"]', 'span[aria-label*="reviews"]', 'span[jsan*="reviewCount"]'],
            'Rating': ['div.F7nice span[aria-hidden="true"]', 'span[aria-hidden="true"][role="text"]', 'span[aria-label*="stars"]'],
            'hours': ['div.t39EBf table.eK4R0e tbody', 'table.eK4R0e tbody', 'div[jsan*="hours"] table tbody'],
            'Category': ['button.DkEaL', 'span.DkEaL', 'button[jsan*="categoryText"]'],
            'Description': ['div.WeS02d div.PYvSYb', 'div.PYvSYb', 'div[data-attrid="description"]'],
            'Status': ['div.o0Svhf span.ZDu9vd', 'span.ZDu9vd', 'span[jsan*="operationStatus"]'],
        }
        
        # The driver is initialized in open_browser() method
        self.driver = None
    
    def open_browser(self):
        """Open a new browser instance with automatic driver installation."""
        try:
            # Use webdriver-manager to automatically download the correct driver version
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            driver.set_page_load_timeout(30)  # Increased timeout for better reliability
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    def navigate_to_google_maps(self, driver):
        """Navigate to Google Maps website with better error handling."""
        try:
            driver.get("https://www.google.com/maps")
            
            # Use a longer wait time for reliability
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#searchboxinput"))
            )
            
            # Handle potential cookie consent dialog
            try:
                # Try multiple possible selectors for cookie buttons
                cookie_selectors = [
                    "//button[contains(., 'Accept')]",
                    "//button[contains(., 'I agree')]",
                    "//button[contains(., 'Agree')]",
                    "//button[contains(@aria-label, 'Accept')]",
                    "//button[contains(@aria-label, 'Accept all')]"
                ]
                
                for selector in cookie_selectors:
                    buttons = driver.find_elements(By.XPATH, selector)
                    if buttons:
                        buttons[0].click()
                        logger.info("Clicked on cookie consent button")
                        time.sleep(1)
                        break
            except Exception as e:
                logger.debug(f"No cookie dialog or couldn't handle it: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error navigating to Google Maps: {e}")
            # Save screenshot for debugging
            self.save_screenshot(driver, "navigation_error")
            return False
    
    def search_place(self, driver, query):
        """Search for a specific place on Google Maps with better error handling."""
        try:
            logger.info(f"Searching for: {query}")
            
            # Find the search box and enter the query
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#searchboxinput"))
            )
            
            # Clear the search box and enter the new query
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.ENTER)
            
            # Wait for search results - longer wait time
            time.sleep(5)
            
            # Check for "No results found" message
            try:
                no_results = driver.find_elements(By.XPATH, "//div[contains(text(), 'No results found')]")
                if no_results:
                    logger.warning(f"No results found for query: {query}")
                    return False
            except:
                pass
                
            # See if we're in list view (multiple results)
            result_items = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK")
            if result_items:
                logger.info(f"Found search results list with {len(result_items)} items")
                return True
            else:
                # Check if we're already in detail view (single result)
                detail_indicators = [
                    "h1.DUwDvf",
                    "h1.fontHeadlineLarge",
                    "button[data-item-id='address']"
                ]
                
                for selector in detail_indicators:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info("Direct navigation to single result")
                        return True
                
                logger.warning(f"Could not find search results for query: {query}")
                return False
            
        except Exception as e:
            logger.error(f"Error searching for place '{query}': {e}")
            self.save_screenshot(driver, f"search_error_{query.replace(' ', '_')}")
            return False
    
    def extract_listing_urls(self, driver, total_desired=10):
        """Extract URLs of listings from the search results page."""
        listing_urls = []
        previously_found = 0
        stuck_count = 0
        max_stuck_count = 5
        max_attempts = 15
        
        logger.info(f"Attempting to extract {total_desired} listing URLs")
        
        for attempt in range(max_attempts):
            if len(listing_urls) >= total_desired:
                break
                
            # Extract all visible listing URLs
            listing_elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            
            # Add new unique URLs
            for element in listing_elements:
                try:
                    url = element.get_attribute("href")
                    if url and url not in listing_urls:
                        listing_urls.append(url)
                except Exception as e:
                    logger.debug(f"Error extracting URL: {e}")
            
            current_count = len(listing_urls)
            logger.debug(f"Found {current_count} unique listing URLs (attempt {attempt+1})")
            
            if current_count >= total_desired:
                break

            if current_count == previously_found:
                stuck_count += 1
                if stuck_count >= max_stuck_count:
                    logger.info(f"Stopped at {current_count} listings after {stuck_count} attempts with no new results")
                    break
            else:
                stuck_count = 0

            # Scroll to load more results
            try:
                # Find the results container and scroll
                scroll_targets = [
                    "div[role='feed']",  # Main results feed
                    ".m6QErb[aria-label]",  # Alternative results container
                    ".m6QErb.DxyBCb"  # Another variation
                ]
                
                for target in scroll_targets:
                    elements = driver.find_elements(By.CSS_SELECTOR, target)
                    if elements:
                        # JavaScript scroll within the container
                        driver.execute_script(
                            "arguments[0].scrollTo({top: arguments[0].scrollHeight, behavior: 'smooth'});", 
                            elements[0]
                        )
                        break
                else:
                    # If no specific container found, try general page scroll
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new results to load
                time.sleep(2)
            except Exception as e:
                logger.debug(f"Error while scrolling: {e}")
                break  # Break on scroll error

            previously_found = current_count

        logger.info(f"Extracted {len(listing_urls)} listing URLs (requested {total_desired})")
        
        # Return only the requested number of URLs
        return listing_urls[:total_desired]
    
    def format_phone_number(self, phone):
        """Format phone number by removing unwanted characters."""
        if not phone:
            return ""
        # Keep only digits and some special characters
        return phone.strip()
    
    def parse_address(self, address_text):
        """Parse address into components."""
        if not address_text:
            return {
                "Street": "",
                "City": "",
                "State": "",
                "Zip": "",
                "Country": ""
            }
        
        try:
            # Simple parsing - would need refinement for different countries
            parts = address_text.split(',')
            
            address_components = {
                "Street": parts[0].strip() if len(parts) > 0 else "",
                "City": parts[1].strip() if len(parts) > 1 else "",
                "State": "",
                "Zip": "",
                "Country": parts[-1].strip() if len(parts) > 2 else ""
            }
            
            # Try to extract state and zip from the third part if available
            if len(parts) > 2:
                state_zip = parts[2].strip().split()
                address_components["State"] = state_zip[0] if len(state_zip) > 0 else ""
                address_components["Zip"] = state_zip[1] if len(state_zip) > 1 else ""
                
            return address_components
            
        except Exception as e:
            logger.debug(f"Error parsing address '{address_text}': {e}")
            return {
                "Street": address_text,
                "City": "",
                "State": "",
                "Zip": "",
                "Country": ""
            }
    
    def format_time(self, time_str):
        """Format time string."""
        if not time_str:
            return ""
        return time_str.strip()
    
    def parse_hours(self, hours_text):
        """Parse hours information into day-specific fields."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hours_data = {day: "" for day in days}
        
        if not hours_text:
            return hours_data
        
        try:
            day_patterns = [
                rf"{day}:\s*(.*?)(?=;|$)" for day in days
            ]
            
            for i, pattern in enumerate(day_patterns):
                match = re.search(pattern, hours_text)
                if match:
                    hours_data[days[i]] = match.group(1).strip()
            
            return hours_data
            
        except Exception as e:
            logger.debug(f"Error parsing hours '{hours_text}': {e}")
            return hours_data
    
    def extract_image_url(self, driver):
        """Extract main image URL for the listing."""
        try:
            # Look for main image in the interface
            image_elements = driver.find_elements(By.CSS_SELECTOR, "button[jsaction*='pane.heroHeaderImage'] img")
            if image_elements:
                return image_elements[0].get_attribute("src")
            
            # Alternative image selectors
            alt_selectors = [
                "div.ZKCDEc img",
                "div.RZ66Rb img",
                "img.Liguzb"
            ]
            
            for selector in alt_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements[0].get_attribute("src")
            
            return ""
        except Exception as e:
            logger.debug(f"Error extracting image URL: {e}")
            return ""
    
    def check_internet_connection(self):
        """Check if internet connection is available."""
        try:
            # Try to connect to Google's DNS server
            requests.get("https://8.8.8.8", timeout=3)
            return True
        except:
            return False
    
    def extract_services_and_attributes(self, driver):
        """Extract additional services and attributes from the listing."""
        additional_data = {}
        
        try:
            # Look for service options sections
            service_sections = driver.find_elements(
                By.XPATH, 
                "//h2[contains(text(), 'Service options') or contains(text(), 'Amenities') or contains(text(), 'Highlights')]/following-sibling::div[1]"
            )
            
            services = []
            for section in service_sections:
                service_items = section.find_elements(By.CSS_SELECTOR, "span.mgr77e")
                for item in service_items:
                    services.append(item.text.strip())
            
            additional_data["Services"] = "; ".join(services) if services else ""
            
            return additional_data
            
        except Exception as e:
            logger.debug(f"Error extracting services: {e}")
            return {"Services": ""}
    
    def scrape_single_listing(self, driver, url):
        """Scrape data from a single listing URL."""
        try:
            logger.info(f"Processing listing URL: {url}")
            
            # Navigate to the listing URL
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Try to detect if we're on a valid details page
            valid_page = False
            for name_selector in self.selectors['Name']:
                elements = driver.find_elements(By.CSS_SELECTOR, name_selector)
                if elements:
                    valid_page = True
                    break
            
            if not valid_page:
                logger.warning(f"Not a valid listing page: {url}")
                self.save_screenshot(driver, "invalid_listing_page")
                return None
                
            # Initialize item dictionary
            item = {}
            
            # Extract data for each field
            for field, selector_list in self.selectors.items():
                value = None
                
                for selector in selector_list:
                    if value:  # If we already found a value, break
                        break
                        
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        if field == 'hours':
                            # Special handling for hours
                            hours_rows = elements[0].find_elements(By.CSS_SELECTOR, "tr")
                            hours_data = []
                            
                            for row in hours_rows:
                                day_elements = row.find_elements(By.CSS_SELECTOR, "th")
                                time_elements = row.find_elements(By.CSS_SELECTOR, "td")
                                
                                if day_elements and time_elements:
                                    day = day_elements[0].text.strip()
                                    time_text = time_elements[0].text.strip()
                                    hours_data.append(f"{day}: {time_text}")
                            
                            value = "; ".join(hours_data) if hours_data else None
                        else:
                            value = elements[0].text.strip()
                
                item[field] = value if value else ""
            
            # Store the listing URL
            item['URL'] = url
            
            # Extract services and attributes
            services_data = self.extract_services_and_attributes(driver)
            item.update(services_data)
            
            # Parse address components
            address_components = self.parse_address(item.pop('address', ""))
            item.update(address_components)
            
            # Process phone number
            item['Phone'] = self.format_phone_number(item.get('Phone', ""))
            
            # Parse and format hours
            hours_data = self.parse_hours(item.pop('hours', ""))
            item.update(hours_data)
            
            # Format review count
            if item.get('Reviews'):
                item['Reviews'] = ''.join(filter(str.isdigit, item['Reviews']))
                try:
                    item['Reviews'] = int(item['Reviews'])
                except ValueError:
                    item['Reviews'] = 0
            
            # Format rating
            if item.get('Rating'):
                try:
                    item['Rating'] = float(item['Rating'].replace(',', '.'))
                except ValueError:
                    item['Rating'] = 0.0
            
            # Extract image URL
            item['Image_URL'] = self.extract_image_url(driver)
            
            logger.info(f"Successfully scraped listing: {item.get('Name', url)}")
            return item
            
        except Exception as e:
            logger.error(f"Error scraping listing {url}: {e}")
            self.save_screenshot(driver, f"listing_error_{url.split('/')[-1]}")
            return None
    
    def save_screenshot(self, driver, filename):
        """Save a screenshot for debugging purposes."""
        try:
            if not os.path.exists("debug_screenshots"):
                os.makedirs("debug_screenshots")
            
            screenshot_path = f"debug_screenshots/{filename}_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
    
    def extract_details(self, driver, fields=None):
        """Extract details about the place with improved selector handling."""
        # If no specific fields are requested, extract all available fields
        if fields is None:
            fields = list(self.selectors.keys())
        
        # Create a dictionary to store results
        results = {}
        
        # Save a screenshot before extraction for debugging
        self.save_screenshot(driver, "before_extraction")
        
        # Get the page source and create a BeautifulSoup object
        page_source = driver.page_source
        
        # Log a small portion of the page source for debugging
        logger.debug(f"Page source preview: {page_source[:500]}...")
        
        # Try both parsers for better compatibility
        try:
            soup = BeautifulSoup(page_source, 'lxml')
        except:
            soup = BeautifulSoup(page_source, 'html.parser')
        
        # Sometimes we need to expand sections to see all data
        try:
            # Try to expand "About" section if it exists
            about_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'About')]")
            if about_buttons:
                about_buttons[0].click()
                time.sleep(1)
                logger.info("Expanded 'About' section")
                
            # Try to expand hours if collapsed
            hours_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(., 'hours') or contains(@aria-label, 'hours') or contains(., 'Hours')]")
            if hours_buttons:
                hours_buttons[0].click()
                time.sleep(1)
                logger.info("Expanded hours section")
                
        except Exception as e:
            logger.debug(f"Error expanding sections: {e}")
        
        # Extract details for each requested field
        for field in fields:
            if field in self.selectors:
                # Try each selector for this field
                field_selectors = self.selectors[field]
                value_found = False
                
                for selector in field_selectors:
                    if value_found:
                        break
                        
                    try:
                        # First try with selenium for dynamic content
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            if field == 'hours':
                                # Special handling for hours
                                hours_data = []
                                rows = driver.find_elements(By.CSS_SELECTOR, f"{selector} tr")
                                for row in rows:
                                    day_elements = row.find_elements(By.CSS_SELECTOR, "th")
                                    hour_elements = row.find_elements(By.CSS_SELECTOR, "td")
                                    
                                    day = day_elements[0].text.strip() if day_elements else ""
                                    hours = hour_elements[0].text.strip() if hour_elements else ""
                                    
                                    if day and hours:
                                        hours_data.append(f"{day}: {hours}")
                                
                                if hours_data:
                                    results[field] = "; ".join(hours_data)
                                    value_found = True
                            else:
                                # For other fields, just get the text
                                text = elements[0].text.strip()
                                if text:
                                    results[field] = text
                                    value_found = True
                                    logger.debug(f"Found {field} using selector: {selector}")
                    except Exception as e:
                        logger.debug(f"Error with Selenium extraction for {field} using {selector}: {e}")
                
                # If selenium didn't find anything, try with BeautifulSoup
                if not value_found:
                    for selector in field_selectors:
                        try:
                            element = soup.select_one(selector)
                            if element:
                                if field == 'hours':
                                    # Special handling for hours
                                    hours_data = []
                                    rows = element.select('tr')
                                    for row in rows:
                                        day = row.select_one('th').text.strip() if row.select_one('th') else ""
                                        hours = row.select_one('td').text.strip() if row.select_one('td') else ""
                                        if day and hours:
                                            hours_data.append(f"{day}: {hours}")
                                    
                                    if hours_data:
                                        results[field] = "; ".join(hours_data)
                                        value_found = True
                                else:
                                    # For other fields, just get the text
                                    text = element.text.strip()
                                    if text:
                                        results[field] = text
                                        value_found = True
                                        logger.debug(f"Found {field} using BS4 selector: {selector}")
                                        break
                        except Exception as e:
                            logger.debug(f"Error with BS4 extraction for {field} using {selector}: {e}")
                
                # If we still couldn't find a value, try a more aggressive approach with XPath
                if not value_found and field in ['Name', 'address', 'Phone', 'Website']:
                    try:
                        # Use more generic XPath expressions for common fields
                        xpath_patterns = {
                            'Name': "//h1",
                            'address': "//*[contains(text(), 'Address') or contains(@aria-label, 'address')]/following::*[1]",
                            'Phone': "//*[contains(text(), 'Phone') or contains(@aria-label, 'phone')]/following::*[1]",
                            'Website': "//*[contains(text(), 'Website') or contains(@aria-label, 'website')]/following::*[1]"
                        }
                        
                        if field in xpath_patterns:
                            elements = driver.find_elements(By.XPATH, xpath_patterns[field])
                            if elements:
                                text = elements[0].text.strip()
                                if text:
                                    results[field] = text
                                    value_found = True
                                    logger.debug(f"Found {field} using XPath fallback")
                    except Exception as e:
                        logger.debug(f"Error with XPath fallback for {field}: {e}")
                
                # If still no value found, set to None
                if not value_found:
                    results[field] = None
                    logger.debug(f"No value found for {field}")
            else:
                results[field] = None
        
        # Check if we got any actual data
        data_found = any(v for v in results.values() if v is not None)
        
        if not data_found:
            logger.warning("No data was extracted from the page")
            self.save_screenshot(driver, "no_data_extracted")
        else:
            logger.info(f"Successfully extracted data: {', '.join(k for k, v in results.items() if v is not None)}")
        
        return results
    
    def process_query_listings(self, driver, query, max_listings=5, fields=None):
        """Process multiple listing results for a search query."""
        results = []
        
        try:
            # Search for the query
            if not self.search_place(driver, query):
                logger.warning(f"No search results found for '{query}'")
                return results
            
            # Check if we got redirected to a single business page
            # This happens when Google Maps finds an exact match
            single_result = False
            for name_selector in self.selectors['Name']:
                elements = driver.find_elements(By.CSS_SELECTOR, name_selector)
                if elements:
                    single_result = True
                    break
            
            if single_result:
                logger.info(f"Direct match found for '{query}', extracting single result")
                details = self.extract_details(driver, fields)
                if details:
                    details["Search Query"] = query
                    results.append(details)
            else:
                # We're in search results view, extract multiple listings
                logger.info(f"Extracting up to {max_listings} listings for '{query}'")
                
                # Extract listing URLs
                listing_urls = self.extract_listing_urls(driver, max_listings)
                
                if not listing_urls:
                    logger.warning(f"No listing URLs found for '{query}'")
                    return results
                
                # Process each listing URL
                for i, url in enumerate(listing_urls):
                    logger.info(f"Processing listing {i+1}/{len(listing_urls)}: {url}")
                    
                    # For each listing we need to open a new tab
                    # Opening in same tab would make it hard to go back to results
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    try:
                        # Extract details from this listing
                        listing_data = self.scrape_single_listing(driver, url)
                        
                        if listing_data:
                            listing_data["Search Query"] = query
                            results.append(listing_data)
                    except Exception as e:
                        logger.error(f"Error processing listing {url}: {e}")
                    
                    # Close this tab and return to the original tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing query listings for '{query}': {e}")
            self.save_screenshot(driver, f"process_error_{query.replace(' ', '_')}")
            return results
    
    def scrape_multiple_queries_with_listings(self, queries, max_listings_per_query=5, fields=None):
        """
        Scrape multiple queries, each with multiple listings.
        
        Args:
            queries (list): List of search queries.
            max_listings_per_query (int): Maximum listings to extract per query.
            fields (list): Fields to extract for each listing.
            
        Returns:
            pandas.DataFrame: DataFrame with all extracted listings.
        """
        all_results = []
        
        # Multi-threaded approach
        if self.num_threads > 1:
            # Define a worker function for thread pool
            def process_query(query):
                try:
                    driver = self.open_browser()
                    
                    if not self.navigate_to_google_maps(driver):
                        logger.error(f"Failed to navigate to Google Maps for '{query}'")
                        return []
                    
                    results = self.process_query_listings(driver, query, max_listings_per_query, fields)
                    return results
                except Exception as e:
                    logger.error(f"Thread error processing '{query}': {e}")
                    return []
                finally:
                    if driver:
                        driver.quit()
            
            # Use ThreadPoolExecutor for parallel processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                # Submit all queries to the executor
                future_results = list(executor.map(process_query, queries))
                
                # Flatten the list of results
                for results in future_results:
                    all_results.extend(results)
        
        # Single-threaded approach
        else:
            driver = None
            try:
                driver = self.open_browser()
                
                if not self.navigate_to_google_maps(driver):
                    logger.error("Failed to navigate to Google Maps, aborting all queries")
                    return pd.DataFrame()
                
                # Process each query
                for query in queries:
                    logger.info(f"Processing query: {query}")
                    
                    # Check internet connection before each query
                    if not self.check_internet_connection():
                        logger.error("Internet connection lost, retrying...")
                        time.sleep(10)  # Wait and try again
                        if not self.check_internet_connection():
                            logger.error("Internet connection still unavailable, skipping query")
                            continue
                    
                    # Get results for this query
                    query_results = self.process_query_listings(driver, query, max_listings_per_query, fields)
                    all_results.extend(query_results)
                    
                    # Add a delay between queries to avoid rate limiting
                    time.sleep(3)
            
            except Exception as e:
                logger.error(f"Error in scraping process: {e}")
            finally:
                if driver:
                    driver.quit()
        
        # Convert results to DataFrame
        if all_results:
            df = pd.DataFrame(all_results)
            logger.info(f"Successfully scraped {len(df)} listings across {len(queries)} queries")
            return df
        else:
            logger.warning("No results found for any query")
            return pd.DataFrame()
    
    def scrape_to_csv(self, queries, output_file, max_listings_per_query=5, fields=None):
        """
        Scrape data and save directly to CSV file.
        
        Args:
            queries (list): List of search queries.
            output_file (str): Path to output CSV file.
            max_listings_per_query (int): Maximum listings to extract per query.
            fields (list): Fields to extract for each listing.
        """
        try:
            # Scrape data
            df = self.scrape_multiple_queries_with_listings(queries, max_listings_per_query, fields)
            
            if not df.empty:
                # Save to CSV
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                logger.info(f"Data successfully saved to {output_file}")
                return True
            else:
                logger.warning(f"No data to save to {output_file}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")
            return False

# Main execution block for the Google Maps Scraper
if __name__ == "__main__":
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Google Maps Scraper')
    parser.add_argument('--queries', '-q', type=str, nargs='+', required=True, help='Search queries to scrape')
    parser.add_argument('--output', '-o', type=str, default='google_maps_results.csv', help='Output CSV file name')
    parser.add_argument('--max-listings', '-m', type=int, default=5, help='Maximum listings per query')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--threads', '-t', type=int, default=1, help='Number of threads to use')
    
    args = parser.parse_args()
    
    # Initialize the scraper
    scraper = GoogleMapsScraper(headless=args.headless, num_threads=args.threads)
    
    # Log the start of scraping
    logger.info(f"Starting scraping with {args.threads} thread(s), headless mode: {args.headless}")
    logger.info(f"Scraping {len(args.queries)} queries with up to {args.max_listings} listings per query")
    logger.info(f"Output will be saved to: {args.output}")
    
    # Define the fields to extract
    fields = [
        'Name', 'Street', 'City', 'State', 'Zip', 'Country',
        'Phone', 'Website', 'Rating', 'Reviews', 'Category',
        'Status', 'Description', 'Services', 'Image_URL',
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]
    
    try:
        # Start scraping
        success = scraper.scrape_to_csv(args.queries, args.output, args.max_listings, fields)
        
        if success:
            logger.info(f"Scraping completed successfully. Results saved to {args.output}")
        else:
            logger.error("Scraping completed with errors. Check the logs for details.")
    
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred during scraping: {e}")
    finally:
        logger.info("Scraping process finished.")