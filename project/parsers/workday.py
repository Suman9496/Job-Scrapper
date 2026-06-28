# -*- coding: utf-8 -*-
"""
Workday ATS Parser.
Queries internal Workday JSON endpoints for reliable extraction of dynamic postings.
"""

from urllib.parse import urlparse
import json
from ..utils import safe_request, logger

class WorkdayParser:
    @staticmethod
    def parse(url):
        """
        Parses Workday career sites.
        Translates human-facing URL to Workday CXS (Tenant Search) API endpoint and performs a REST query.
        """
        parsed = urlparse(url)
        # Workday URLs follow: https://<company>.myworkdayjobs.com/<tenant_id>
        tenant = parsed.path.strip("/")
        if "/" in tenant:
            tenant = tenant.split("/")[0]
            
        company_host = parsed.netloc
        if not company_host or "workdayjobs.com" not in company_host:
            return []
            
        # REST API for Workday CXS Search
        api_url = f"https://{company_host}/wday/cxs/v1/{tenant}/jobs"
        logger.info(f"Workday Parser: Post request to CXS API: {api_url}")
        
        payload = {
            "appliedFacets": {},
            "limit": 20,
            "offset": 0,
            "searchText": ""
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*"
        }
        
        response = safe_request(api_url, method="POST", json=payload, headers=headers)
        if response and response.status_code == 200:
            try:
                data = response.json()
                jobs = []
                for item in data.get("jobPostings", []):
                    # Extract ID and URL
                    external_path = item.get("externalPath")
                    job_url = f"https://{company_host}{external_path}"
                    job_id = external_path.split("/")[-1] if external_path else "unknown"
                    
                    jobs.append({
                        "id": str(job_id),
                        "title": item.get("title"),
                        "company": tenant.replace("-", " ").title(),
                        "url": job_url,
                        "source": "Workday",
                        "location": item.get("locationsText") or "India",
                        "description": "",  # Crawled on deep parse
                        "posted_date": item.get("postedOn") or ""
                    })
                return jobs
            except Exception as e:
                logger.warning(f"Workday API parsing failed: {e}")
                
        return []
