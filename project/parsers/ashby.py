# -*- coding: utf-8 -*-
"""
Ashby ATS Parser.
Parses jobs from Ashby career pages.
"""

import json
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ..utils import safe_request, logger

class AshbyParser:
    @staticmethod
    def parse(url):
        """
        Parses Ashby boards. Queries Ashby's public API or scrapes web pages.
        """
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        company_token = None
        if path_parts:
            company_token = path_parts[-1]
            
        if not company_token:
            return []
            
        # Ashby uses standard GraphQL or script tag injections
        # Try fetching Ashby web page and look for JSON data in script tags
        logger.info(f"Ashby Parser: Fetching HTML for {url}")
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        jobs = []
        
        # Ashby pages typically inject window.__ASHBY_STATE__ or have JSON embedded
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "__ASHBY_STATE__" in script.string:
                try:
                    # Parse out JSON state
                    match = re.search(r"__ASHBY_STATE__\s*=\s*({.*?});", script.string)
                    if match:
                        state = json.loads(match.group(1))
                        # Ashby has standard structure
                        for job in state.get("jobBoard", {}).get("jobs", []):
                            jobs.append({
                                "id": str(job.get("id")),
                                "title": job.get("title"),
                                "company": company_token.capitalize(),
                                "url": f"https://ashbyhq.com/{company_token}/jobs/{job.get('id')}",
                                "source": "Ashby",
                                "location": job.get("location") or "India",
                                "description": job.get("descriptionHtml") or "",
                                "posted_date": job.get("publishedAt") or ""
                            })
                        if jobs:
                            return jobs
                except Exception as e:
                    logger.warning(f"Failed to parse Ashby embedded state: {e}")
                    
        # Fallback manual DOM scrape
        logger.info(f"Ashby Parser: Attempting DOM fall-back scrape.")
        for a_tag in soup.find_all("a", href=True):
            if "/jobs/" in a_tag["href"]:
                job_url = a_tag["href"]
                if job_url.startswith("/"):
                    job_url = f"https://ashbyhq.com/{company_token}{job_url}"
                job_id = job_url.split("/")[-1]
                title_tag = a_tag.find(["h3", "h4", "span"])
                title = title_tag.get_text(strip=True) if title_tag else a_tag.get_text(strip=True)
                
                jobs.append({
                    "id": str(job_id),
                    "title": title,
                    "company": company_token.capitalize(),
                    "url": job_url,
                    "source": "Ashby",
                    "location": "India",
                    "description": "",
                    "posted_date": ""
                })
        return jobs
