#google_search.py
import time
import requests
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, FACT_CHECK_SITES, is_trusted_url

def google_search(claim: str, api_key=GOOGLE_API_KEY, cse_id=GOOGLE_CSE_ID, delay=2):
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": claim,
        "num": 5
    }

    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
        response.raise_for_status()
        items = response.json().get("items", [])

        filtered_results = []
        for item in items:
            link = item.get("link", "")
            if is_trusted_url(link) and not any(site in link for site in FACT_CHECK_SITES):
                filtered_results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": link,
                    "displayLink": item.get("displayLink", "")
                })

        # optional: small delay for API quota friendliness
        time.sleep(delay)

        return filtered_results

    except Exception as e:
        print(f"Google Search failed: {e}")
        return []
