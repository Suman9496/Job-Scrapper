# -*- coding: utf-8 -*-
"""
Post-Crawl Validation Module.
Performs deep link checks (HTTP 200) and structure health testing on extracted job entries.
"""

from .utils import safe_request, logger

class JobValidator:
    @staticmethod
    def is_link_alive(url):
        """Checks if the job post URL is valid and reachable (returns status 200)."""
        if not url:
            return False
            
        try:
            # Send a fast HEAD request first to verify link health, fallback to GET if disallowed
            response = safe_request(url, method="HEAD", timeout=8)
            if response is not None:
                if response.status_code in [200, 301, 302]:
                    return True
                    
            response_get = safe_request(url, method="GET", timeout=8)
            if response_get is not None:
                return response_get.status_code == 200
        except Exception as e:
            logger.warning(f"Validator: Link check failed for {url}: {e}")
            
        return False

    @classmethod
    def validate_job_fields(cls, job):
        """
        Validates the semantic completeness of the job.
        Rejects job objects missing critical attributes or having unresolvable dead links.
        """
        title = job.get("title", "").strip()
        company = job.get("company", "").strip()
        url = job.get("url", "").strip()
        
        # 1. Structure completeness check
        if not title or not company or not url:
            logger.debug(f"Validator: Rejected job record with incomplete core structure: Title: '{title}', Company: '{company}'")
            return False
            
        # 2. Prevent dummy/broken postings
        if len(title) < 4 or len(company) < 2:
            return False
            
        # 3. Live URL validation (Layer 1 check)
        if not cls.is_link_alive(url):
            logger.info(f"Validator: Rejected job '{title}' @ '{company}' due to dead or unreachable link: {url}")
            return False
            
        return True
