# config.py

import os
from urllib.parse import urlparse
from openai import OpenAI

# === API Keys ===
GOOGLE_API_KEY = "AIzaSyDIzrfF98CteJ6pT2-otIJGvrN-B7m3724"
GOOGLE_CSE_ID = "c785a893227be4578"

# === OpenAI API KEYS ===
client = OpenAI(api_key="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")

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