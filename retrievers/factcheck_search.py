#factcheck_search.py
import time
import requests
from urllib.parse import urlparse
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, FACT_CHECK_SITES

def search_fact_check(claim: str, api_key=GOOGLE_API_KEY, cse_id=GOOGLE_CSE_ID, delay=2):
    # Build query restricted to fact-check domains
    site_filter = " OR site:".join(FACT_CHECK_SITES)
    query = f"{claim} site:{site_filter}"

    filtered_results = []

    # Search first 2 pages (max 10 results)
    for start_index in [1, 11]:
        if len(filtered_results) >= 5:  # cap at 5 results
            break

        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": 5,
            "start": start_index
        }

        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
            response.raise_for_status()
            items = response.json().get("items", [])

            for item in items:
                if len(filtered_results) >= 5:
                    break

                link = item.get("link", "")
                domain = urlparse(link).netloc.split(":")[0].replace("www.", "")
                if any(site in domain for site in FACT_CHECK_SITES):
                    filtered_results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": link,
                        "displayLink": item.get("displayLink", "")
                    })

        except Exception as e:
            print(f"Fact-check search failed on page {start_index}: {e}")
            continue

        time.sleep(delay)

    return filtered_results