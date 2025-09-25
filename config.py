# config.py

import os
from urllib.parse import urlparse
from openai import OpenAI

# === API Keys ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# === OpenAI API KEYS ===
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# === Trusted fact-checking sites ===
FACT_CHECK_SITES = [
    "snopes.com", "factcheck.org", "politifact.com", "skepticalscience.com",
    "factcheck.afp.com", "reuters.com", "apnews.com", "hoaxeye.com",
    "ici.radio-canada.ca/decrypteurs", "climatefeedback.org", "ipcc.ch",
    "ncei.noaa.gov", "wmo.int", "carbonbrief.org", "climate.nasa.gov"
]

# === Untrusted sources to exclude ===
UNTRUSTED_SOURCES = {
    "reddit.com", "twitter.com", "x.com", "tiktok.com", "instagram.com",
    "facebook.com", "pinterest.com", "youtube.com", "amazon.com", "ebay.com",
    "breitbart.com", "zerohedge.com", "rt.com", "bitchute.com"
}

def is_trusted_url(url: str) -> bool:
    """Check if a URL is trusted (not in untrusted list)."""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return (
            url.startswith("http://") or url.startswith("https://")
        ) and not any(domain == bad or domain.endswith("." + bad) for bad in UNTRUSTED_SOURCES)
    except Exception:
        return False