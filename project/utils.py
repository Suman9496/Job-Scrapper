# -*- coding: utf-8 -*-
"""
Helper utilities including logger initialization, user-agent rotation, and request retries.
"""

import logging
import random
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def setup_logger():
    """Initializes and returns a standardized logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("ITJobScraper")
    return logger

logger = setup_logger()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

def get_random_headers():
    """Returns random headers to mimic standard browser profiles."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def get_session():
    """Returns a requests session configured with retries and timeout backoffs."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def safe_request(url, method="GET", timeout=15, **kwargs):
    """Safely executes HTTP request with headers, logging, and error handling."""
    session = get_session()
    headers = get_random_headers()
    if "headers" in kwargs:
        headers.update(kwargs["headers"])
        del kwargs["headers"]
    
    try:
        # Introduce a minor rate limiting random delay
        time.sleep(random.uniform(0.5, 1.5))
        
        response = session.request(method, url, headers=headers, timeout=timeout, **kwargs)
        return response
    except Exception as e:
        logger.warning(f"Failed to request {url}: {e}")
        return None

def random_delay(min_delay=1, max_delay=3):
    """Introduces a random sleep delay to avoid anti-scraping systems."""
    time.sleep(random.uniform(min_delay, max_delay))
