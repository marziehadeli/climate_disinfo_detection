#google_reverse_image.py

import os
from time import sleep
import requests
from pathlib import Path
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

from urllib.parse import urlparse
from config import is_trusted_url

# === Setup WebDriver ===
options = webdriver.ChromeOptions()
options.add_argument("--lang=en")
options.add_argument("--disable-blink-features=AutomationControlled") #hides automation flags in Chrome.
options.add_experimental_option("excludeSwitches", ["enable-automation"]) #prevents the “Chrome is being controlled by automated software” banner.
options.add_experimental_option('useAutomationExtension', False) #disables Selenium’s automation extension.
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options) # Launch Chrome browser with Selenium using ChromeDriverManager
                                                                                             # Ensures the correct ChromeDriver version is installed automatically
                                                                                             # Makes the browser appear less automated to reduce CAPTCHA triggers



# === CAPTCHA Check ===
def human_verification():
    driver.get('https://www.google.com/search?q=chrome')
    print("Please complete the CAPTCHA in the browser if shown...")
    for i in range(300):
        if not driver.current_url.startswith('https://www.google.com/sorry/'):
            return
        sleep(1)
    raise TimeoutError("CAPTCHA not completed in time.")


def open_about_this_image(driver):
    try:
        about_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='About this image']"))
        )
        about_element.click()
        sleep(3)
        return True
    except Exception as e:
        print(f"Failed to click 'About this image': {e}")
        return False

def extract_about_this_image_results(driver, max_items=4):
    results = []
    seen_links = set()

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'OMbcR')]"))
        )
        date_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'OMbcR')]")
        print(f"Found {len(date_blocks)} About panel date blocks")

        for date_block in date_blocks:
            try:
                # Go up to the parent container div (usually several levels up)
                container_div = date_block.find_element(By.XPATH, "./ancestor::div[contains(@class, 'GbFjhd') or contains(@class, 'UioT6b')]")

                # Find the <a> tag inside this container
                try:
                    anchor = container_div.find_element(By.XPATH, ".//a")
                    link = anchor.get_attribute("href")
                    if not link or link in seen_links:
                        continue
                    seen_links.add(link)
                except:
                    continue  # skip if no anchor

                # Title
                try:
                    title_el = container_div.find_element(By.XPATH, ".//h3")
                    title = title_el.text.strip()
                except:
                    title = container_div.text.strip().split('\n')[0] or "[No title]"

                # Thumbnail
                #try:
                    #thumbnail = container_div.find_element(By.TAG_NAME, "img").get_attribute("src")
                #except:
                    #thumbnail = None

                # Parse date
                date_text = date_block.text.strip().replace("—", "").strip()
                try:
                    parsed_date = datetime.strptime(date_text, "%b %d, %Y")
                    date = parsed_date.isoformat()
                except:
                    date = date_text

                results.append({
                    "date": date,
                    "link": link,
                    #"thumbnail": thumbnail,
                    "text": title
                })

            except Exception as e:
                print(f"! Failed to process date block: {e}")
                continue

        # Sort and return top N
        results = sorted(
            results,
            key=lambda r: r["date"] if isinstance(r["date"], str) and re.match(r"\d{4}-\d{2}-\d{2}", r["date"]) else "9999-12-31"
        )

        return results[:max_items]

    except Exception as e:
        #driver.save_screenshot(f"error_about_image_{int(time.time())}.png")
        print(f"Failed to extract About entries: {e}")
        return []



# === Scraper Function ===
def scraper(url, max_chars=2000, retries=2):
    headers = {"User-Agent": "Mozilla/5.0"}

    # Skip known image file extensions
    if url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")):
        return {"title": "", "text": "[Image file — no article content]"}

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"title": "", "text": f"[HTTP error {response.status_code}]"}
            
            # Skip if the content-type is an image (e.g., a CDN link)
            if "image" in response.headers.get("Content-Type", ""):
                return {"title": "", "text": "[Image content — no text found]"}

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove common non-content tags
            for tag in soup(["script", "style", "header", "footer", "nav", "aside", "noscript"]):
                tag.decompose()

            # Extract page title
            title = soup.title.string.strip() if soup.title and soup.title.string else ""

            # Extract body text
            text = soup.get_text(separator=' ', strip=True)
            text = text[:max_chars].strip()

            if not text or len(text) < 30:
                return {"title": title, "text": "[No usable content found]"}

            return {"title": title, "text": text}

        except Exception as e:
            if attempt == retries:
                print(f"! Scraper failed for {url}: {e}")
                return {"title": "", "text": f"[Scraper failed: {str(e)}]"}
            
# === Main Function Google Reverse Image Serach ===
def google_reverse_image(image_path_or_folder, max_items=5):
    input_path = Path(image_path_or_folder)
    if not input_path.exists():
        raise FileNotFoundError(f"Path does not exist: {input_path}")
    
    human_verification()

    # Prepare list of images
    if input_path.is_file():
        if input_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise ValueError(f"Unsupported file type: {input_path.suffix}")
        image_paths = [input_path]
    elif input_path.is_dir():
        image_paths = sorted([
            p for p in input_path.iterdir()
            if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
        ], key=lambda x: int(x.stem) if x.stem.isdigit() else x.stem)
        #image_paths = image_paths[:3]                      #  ⬅️ for quick test, only process the first 3 images
        #image_paths = [p for p in image_paths if p.stem in {"19", "43", "102", "379", "410", "472", "480", "483"}]      
    else:
        raise ValueError("Input must be a valid image file or a folder containing images.")

    all_results = []

    for image_path in tqdm(image_paths, desc=f"Reverse image search for ({len(image_paths)} images)", unit="img"):
        try:
            #print(f"Processing: {image_path.name}")
            image_id = image_path.stem
            driver.get('https://www.google.com/imghp')
            sleep(1)
            driver.find_element(By.CSS_SELECTOR, "div.nDcEnd").click()
            sleep(1)
            driver.find_element(By.XPATH, "//input[@type='file']").send_keys(os.path.abspath(image_path))
            sleep(5)

            original_page_source = driver.page_source  # Save to return if needed
            original_url = driver.current_url
            search_results = []

            # === Try to locate "Exact matches"
            try:
                list_div = driver.find_elements(By.XPATH, "//a[.//*[contains(text(), 'Exact matches')]]")
            except Exception as e:
                print(f"Failed to locate exact match section: {e}")
                list_div = []

            if list_div:
                try:
                    exact_match_url = list_div[0].get_attribute('href')
                    driver.get(exact_match_url)
                    sleep(3)

                    result_links = driver.find_elements(By.CSS_SELECTOR, "div#search a")
                    exact_match_data = []

                    for result in result_links:
                        try:
                            link = result.get_attribute("href")
                            if not link or "google.com" in link:
                                continue
                            if not is_trusted_url(link):
                                continue

                            parent = result.find_element(By.XPATH, "./..")

                            try:
                                image_el = parent.find_element(By.XPATH, ".//img")
                                image_src = image_el.get_attribute("src") or image_el.get_attribute("data-src") or ""
                            except:
                                image_src = ""

                            try:
                                snippet_el = parent.find_element(By.XPATH, ".//div[contains(@class,'VwiC3b')]")
                                snippet = snippet_el.text.strip()
                            except:
                                snippet = ""

                            exact_match_data.append({
                                "link": link,
                                "domain": urlparse(link).netloc.lower(),
                                #"image_src": image_src,
                                "snippet": snippet,
                                "fallback_title": result.text.strip()
                            })
                        except Exception as e:
                            print(f"Failed to extract exact match link: {e}")

                    for i, item in enumerate(exact_match_data):
                        if len(search_results) >= max_items:
                            break
                        try:
                            scraped = scraper(item["link"], max_chars=2000)
                            title = scraped.get("title", "").strip() or item["fallback_title"]
                            body = scraped.get("text", "").strip()
                            if len(body) < 30:
                                body = item["snippet"] or "[No content extracted]"

                            result = {
                                "label": "[Exact match]",
                                "title": title,
                                "href": item["link"],
                                "domain": item["domain"],
                                #"image": item["image_src"],
                                "body": body
                            }

                            search_results.append(result)
                        except Exception as e:
                            print(f"! Error while scraping exact match: {e}")

                except Exception as e:
                    print(f"! Error while processing exact matches: {e}")

            # === Visual Matches Fallback (only if no exacted results) ===
            if not search_results:
                print("There is no exact match for this image, move to visual similarities...")
                try:
                    # Go back to the original result page
                    driver.get(original_url)
                    sleep(2)
                    
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Visual matches')]"))
                    )
                    print("Visual matches section found.") 
                    for _ in range(6):
                        driver.execute_script("window.scrollBy(0, window.innerHeight);")
                        sleep(2.5)

                    visual_links = driver.find_elements(By.XPATH, "//a[.//img and not(contains(@href,'google.com'))]")

                    if not visual_links:
                        raise Exception("Visual matches section present, but no image links found.")

                    for i, el in enumerate(visual_links[:max_items]):
                        try:
                            href = el.get_attribute("href")
                            if not href:
                                continue
                            if not is_trusted_url(href):
                                #print(f"! Skipping untrusted domain: {href}")
                                continue
                            try:
                                image_el = el.find_element(By.TAG_NAME, "img")
                                image_src = image_el.get_attribute("src") or image_el.get_attribute("data-src") or ""
                            except:
                                image_src = ""

                            #print(f"! Scraping visual match {i+1}: {href}")
                            scraped = scraper(href, max_chars=2000)
                            title = (scraped.get("title") or el.text or "[No title]").strip()

                            body = scraped.get("text", "").strip()
                            if len(body) < 30:
                                body = "[No article content — visual match only]"

                            result = {
                                "label": "[Visual match]",
                                "title": title,
                                "href": href,
                                "domain": urlparse(href).netloc.lower(),
                                #"image": image_src,
                                "body": body
                            }

                            search_results.append(result)
                        except Exception as e:
                            print(f"! Failed to process visual match {i+1}: {e}")
                            continue

                except Exception as e:
                    print(f"! No visual matches found: {e}")

            
            # === Date Stamp ===
            about_entries = []
            try:
                if open_about_this_image(driver):
                    # Try to locate and scroll the About panel
                    try:
                        # Try to find the about panel explicitly
                        about_panel = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//div[@role='region' and @jscontroller and @jsaction]")
                            )
                        )
                    except:
                        about_panel = None  # Fallback if not found

                    try:
                        for _ in range(5):  # Scroll either the panel or main window
                            if about_panel:
                                driver.execute_script("arguments[0].scrollBy(0, arguments[0].scrollHeight);", about_panel)
                            else:
                                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                            time.sleep(2)
                    except Exception as e:
                        print(f"! Scroll failed: {e}")
                        driver.save_screenshot(f"scroll_fail_{int(time.time())}.png")
                        with open("scroll_fail.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)

                    # Extract top 4 sorted oldest entries directly
                    about_entries = extract_about_this_image_results(driver, max_items=4)

                    print(f"Retrieved {len(about_entries)} About panel entries (oldest first)")
                    for entry in about_entries:
                        if not entry["link"] or not is_trusted_url(entry["link"]):
                            continue
                        try:
                            scraped = scraper(entry["link"], max_chars=2000)
                            title = scraped.get("title", "").strip()
                            body = scraped.get("text", "").strip()
                            if len(body) < 30:
                                body = entry["text"]

                            search_results.append({
                                "label": "[About this image]",
                                "about_image_date": entry["date"],
                                "about_image_label": "About panel",
                                "title": title or "[No title]",
                                "href": entry["link"],
                                "domain": urlparse(entry["link"]).netloc.lower(),
                                #"image": entry["thumbnail"],
                                "body": body
                            })
                        except Exception as e:
                            print(f"! Error scraping 'About this image' entry: {e}")
            except Exception as e:
                print(f"! Failed to extract 'About this image' results: {e}")

            # Append result to list
            if not search_results and not about_entries:
                print(f"{image_id}: 0 results saved.")
                all_results.append({
                    "id": image_id,
                    "status": "not_found",
                    "trusted_results": [],
                    "about_this_image": []
                })
            else:
                tqdm.write(f"{image_id}: {len(search_results[:max_items])} result(s) saved.")
                all_results.append({
                    "id": image_id,
                    "status": "success",
                    "trusted_results": search_results[:max_items],
                    "about_this_image": about_entries
                })

        except Exception as e:
            print(f"Error processing {image_path.name}: {e}")
            all_results.append({
                "id": image_path.stem,
                "status": "error",
                "trusted_results": [],
                "error": str(e)
            })

    successes = sum(1 for r in all_results if r["status"] == "success")
    print(f"Completed reverse image search for {len(image_paths)} image(s), {successes} successful.")
    return all_results