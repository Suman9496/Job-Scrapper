# -*- coding: utf-8 -*-
"""
Greenhouse ATS Parser.
Parses jobs from boards.greenhouse.io board URLs or via Greenhouse's public API.
"""

import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ..utils import safe_request, logger

class GreenhouseParser:
    @staticmethod
    def parse(url):
        """
        Extracts jobs from a Greenhouse career board.
        Handles both public board API (faster, cleaner) and HTML fallback.
        """
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        # Try to extract company token from path (e.g. /github or /embed/job_board?board_by_id=github)
        company_token = None
        if path_parts:
            company_token = path_parts[0]
            if company_token == "embed" and "board_by_id" in parsed.query:
                company_token = parsed.query.split("board_by_id=")[-1].split("&")[0]
        
        if not company_token:
            company_token = "generic"
            
        # Try JSON API first
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs?content=true"
        logger.info(f"Greenhouse Parser: Attempting API extraction from {api_url}")
        
        response = safe_request(api_url)
        if response and response.status_code == 200:
            try:
                data = response.json()
                jobs = []
                for item in data.get("jobs", []):
                    jobs.append({
                        "id": str(item.get("id")),
                        "title": item.get("title"),
                        "company": data.get("meta", {}).get("name", company_token.capitalize()),
                        "url": item.get("absolute_url"),
                        "source": "Greenhouse",
                        "location": item.get("location", {}).get("name") if item.get("location") else "Remote/Onsite",
                        "description": item.get("content", ""),
                        "posted_date": item.get("updated_at") or ""
                    })
                return jobs
            except Exception as e:
                logger.warning(f"Greenhouse JSON API failed for {company_token}: {e}. Retrying with HTML scrape.")

        # HTML Fallback Scrape
        logger.info(f"Greenhouse Parser: Attempting HTML fallback scraping for {url}")
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        jobs = []
        
        # Try finding standard Greenhouse job links
        sections = soup.find_all("div", class_="opening")
        for sec in sections:
            link_tag = sec.find("a")
            loc_tag = sec.find("span", class_="location")
            if link_tag:
                job_url = "https://boards.greenhouse.io" + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"]
                job_id = job_url.split("/")[-1].split("?")[0]
                jobs.append({
                    "id": str(job_id),
                    "title": link_tag.get_text(strip=True),
                    "company": company_token.capitalize(),
                    "url": job_url,
                    "source": "Greenhouse",
                    "location": loc_tag.get_text(strip=True) if loc_tag else "India",
                    "description": "",  # To be crawled in deep crawl
                    "posted_date": ""
                })
        return jobs
