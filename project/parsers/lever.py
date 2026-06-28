# -*- coding: utf-8 -*-
"""
Lever ATS Parser.
Parses jobs from jobs.lever.co company pages or via Lever's public API.
"""

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ..utils import safe_request, logger

class LeverParser:
    @staticmethod
    def parse(url):
        """
        Extracts jobs from a Lever career board.
        Queries the official Lever public API or falls back to scraping.
        """
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        company_token = None
        if path_parts:
            company_token = path_parts[0]
            
        if not company_token:
            return []
            
        # Try JSON API first
        api_url = f"https://api.lever.co/v0/postings/{company_token}?mode=json"
        logger.info(f"Lever Parser: Requesting JSON from {api_url}")
        
        response = safe_request(api_url)
        if response and response.status_code == 200:
            try:
                data = response.json()
                jobs = []
                for item in data:
                    jobs.append({
                        "id": str(item.get("id")),
                        "title": item.get("text"),
                        "company": company_token.capitalize(),
                        "url": item.get("hostedUrl"),
                        "source": "Lever",
                        "location": item.get("categories", {}).get("location") or "India",
                        "description": item.get("description", "") + "\n" + "\n".join([sec.get("title") + "\n" + sec.get("text") for sec in item.get("lists", [])]),
                        "posted_date": str(item.get("createdAt")) if item.get("createdAt") else ""
                    })
                return jobs
            except Exception as e:
                logger.warning(f"Lever API extraction failed for {company_token}: {e}. Retrying with HTML.")

        # HTML Scraping Fallback
        logger.info(f"Lever Parser: Scraping HTML fallback for {url}")
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        jobs = []
        
        postings = soup.find_all("div", class_="posting")
        for post in postings:
            title_tag = post.find("a", class_="posting-title")
            meta_tag = post.find("div", class_="posting-metadata")
            if title_tag:
                job_url = title_tag["href"]
                job_id = job_url.split("/")[-1]
                title = title_tag.find("h5").get_text(strip=True) if title_tag.find("h5") else title_tag.get_text(strip=True)
                
                location = "India"
                if meta_tag:
                    loc_span = meta_tag.find("span", class_="location")
                    if loc_span:
                        location = loc_span.get_text(strip=True)
                        
                jobs.append({
                    "id": str(job_id),
                    "title": title,
                    "company": company_token.capitalize(),
                    "url": job_url,
                    "source": "Lever",
                    "location": location,
                    "description": "",  # Crawled on deep parse
                    "posted_date": ""
                })
        return jobs
