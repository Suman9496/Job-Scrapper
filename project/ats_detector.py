# -*- coding: utf-8 -*-
"""
ATS Auto-Detection Engine.
Identifies the Applicant Tracking System (ATS) of a career URL via string analysis and HTML sniffing.
"""

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .utils import safe_request, logger

class ATSDetector:
    @staticmethod
    def detect_ats(url, html_content=None):
        """
        Auto-detect the ATS used by a company based on the URL and optionally the HTML body.
        
        Returns:
            str: One of ['greenhouse', 'lever', 'workday', 'smartrecruiters', 'ashby', 'bamboohr', 'successfactors', 'taleo', 'custom']
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        
        # 1. URL string matching (highest confidence)
        if "lever.co" in domain:
            return "lever"
        if "greenhouse.io" in domain or "boards.greenhouse.io" in domain:
            return "greenhouse"
        if "smartrecruiters.com" in domain or "careers.smartrecruiters.com" in domain:
            return "smartrecruiters"
        if "ashbyhq.com" in domain:
            return "ashby"
        if "bamboohr.com" in domain:
            return "bamboohr"
        if "myworkdayjobs.com" in domain:
            return "workday"
        if "successfactors" in domain or "successfactors" in path:
            return "successfactors"
        if "taleo.net" in domain or "taleo" in path:
            return "taleo"
            
        # 2. Sniff HTML if content is not pre-provided
        if html_content is None:
            response = safe_request(url)
            if response and response.status_code == 200:
                html_content = response.text
            else:
                # If page is unretrievable, fallback to custom generic
                return "custom"
                
        soup = BeautifulSoup(html_content, "lxml")
        html_str = str(soup).lower()
        
        # Sniff scripts and CSS class names
        if "lever-job" in html_str or "jobs.lever.co" in html_str:
            return "lever"
        if "greenhouse" in html_str or "boards-api.greenhouse.io" in html_str:
            return "greenhouse"
        if "smartrecruiters" in html_str or "smart_widget" in html_str:
            return "smartrecruiters"
        if "ashbyhq" in html_str or "ashby-job" in html_str:
            return "ashby"
        if "bamboohr" in html_str or "embed-js" in html_str:
            return "bamboohr"
        if "workday" in html_str or "myworkdayjobs" in html_str:
            return "workday"
        if "successfactors" in html_str:
            return "successfactors"
        if "taleo" in html_str:
            return "taleo"
            
        # Default fallback
        logger.info(f"No specific ATS fingerprint detected for {url}. Routing to Generic Parser.")
        return "custom"
