# -*- coding: utf-8 -*-
"""
BambooHR ATS Parser.
Parses jobs from company pages hosted on BambooHR.
"""

from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from ..utils import safe_request, logger

class BambooHRParser:
    @staticmethod
    def parse(url):
        """
        Parses jobs from a BambooHR board using the XML feed API or HTML fallback.
        """
        parsed = urlparse(url)
        subdomain = parsed.netloc.split(".")[0]
        
        if not subdomain or subdomain in ["www", "jobs"]:
            # Try to grab company from path or search queries
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                subdomain = path_parts[0]
                
        if not subdomain:
            return []
            
        # Try BambooHR public XML feed (extremely stable and accurate)
        feed_url = f"https://{subdomain}.bamboohr.com/jobs/list.php"
        logger.info(f"BambooHR Parser: Requesting XML list from {feed_url}")
        
        response = safe_request(feed_url)
        if response and response.status_code == 200:
            try:
                # BambooHR can output clean HTML/JSON or XML.
                # Let's parse with BeautifulSoup to be safe since list.php can output HTML or custom structured data
                soup = BeautifulSoup(response.text, "lxml")
                jobs = []
                
                # Check for standard BambooHR list selectors
                job_links = soup.find_all("a", href=True)
                for link in job_links:
                    if "/jobs/view.php" in link["href"]:
                        job_url = link["href"]
                        if job_url.startswith("/"):
                            job_url = f"https://{subdomain}.bamboohr.com" + job_url
                            
                        job_id = job_url.split("id=")[-1].split("&")[0]
                        jobs.append({
                            "id": str(job_id),
                            "title": link.get_text(strip=True),
                            "company": subdomain.capitalize(),
                            "url": job_url,
                            "source": "BambooHR",
                            "location": "India",
                            "description": "",
                            "posted_date": ""
                        })
                if jobs:
                    return jobs
            except Exception as e:
                logger.warning(f"BambooHR parser parsing error: {e}")

        # Fallback to HTML scrape on the direct URL
        logger.info(f"BambooHR Parser: Falling back to scraping {url}")
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        jobs = []
        for a_tag in soup.find_all("a", href=True):
            if "bamboohr.com/jobs" in a_tag["href"] or "/view.php" in a_tag["href"]:
                title = a_tag.get_text(strip=True)
                if title:
                    job_url = a_tag["href"]
                    if job_url.startswith("/"):
                        job_url = f"https://{subdomain}.bamboohr.com" + job_url
                    job_id = job_url.split("id=")[-1].split("&")[0] if "id=" in job_url else "unknown"
                    jobs.append({
                        "id": str(job_id),
                        "title": title,
                        "company": subdomain.capitalize(),
                        "url": job_url,
                        "source": "BambooHR",
                        "location": "India",
                        "description": "",
                        "posted_date": ""
                    })
        return jobs
