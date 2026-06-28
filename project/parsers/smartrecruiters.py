# -*- coding: utf-8 -*-
"""
SmartRecruiters ATS Parser.
Parses jobs from SmartRecruiters boards.
"""

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ..utils import safe_request, logger

class SmartRecruitersParser:
    @staticmethod
    def parse(url):
        """
        Extracts jobs from a SmartRecruiters board using official API endpoints.
        """
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        company_token = None
        if path_parts:
            company_token = path_parts[-1]  # E.g. careers.smartrecruiters.com/deliveryhero -> deliveryhero
            
        if not company_token:
            return []
            
        api_url = f"https://api.smartrecruiters.com/v1/companies/{company_token}/postings"
        logger.info(f"SmartRecruiters Parser: Fetching API from {api_url}")
        
        response = safe_request(api_url)
        if response and response.status_code == 200:
            try:
                data = response.json()
                jobs = []
                for item in data.get("content", []):
                    jobs.append({
                        "id": str(item.get("id")),
                        "title": item.get("name"),
                        "company": company_token.capitalize(),
                        "url": f"https://jobs.smartrecruiters.com/{company_token}/{item.get('id')}",
                        "source": "SmartRecruiters",
                        "location": f"{item.get('location', {}).get('city', '')}, {item.get('location', {}).get('country', '')}",
                        "description": "", # Loaded dynamically during deep validation
                        "posted_date": item.get("releasedDate") or ""
                    })
                return jobs
            except Exception as e:
                logger.warning(f"SmartRecruiters API failed for {company_token}: {e}")

        # HTML fallback
        logger.info(f"SmartRecruiters Parser: HTML fallback scraping for {url}")
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        jobs = []
        for a_tag in soup.find_all("a", href=True):
            if "jobs.smartrecruiters.com" in a_tag["href"]:
                title_tag = a_tag.find("h4")
                if title_tag:
                    job_url = a_tag["href"]
                    job_id = job_url.split("/")[-1]
                    jobs.append({
                        "id": str(job_id),
                        "title": title_tag.get_text(strip=True),
                        "company": company_token.capitalize(),
                        "url": job_url,
                        "source": "SmartRecruiters",
                        "location": "India",
                        "description": "",
                        "posted_date": ""
                    })
        return jobs
