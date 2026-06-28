# -*- coding: utf-8 -*-
"""
Generic/Custom Career Page Parser.
Utilizes Schema.org JSON-LD parsing, semantic HTML anchors, and CSS patterns for non-standard career pages.
"""

import json
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from ..utils import safe_request, logger

class GenericParser:
    @staticmethod
    def parse(url):
        """
        Attempts to find jobs on any custom website using metadata, JSON-LD, or clean anchor extraction.
        """
        logger.info(f"Generic Fallback Parser: Reading custom page {url}")
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        jobs = []
        
        # 1. Search for JSON-LD (Schema.org / JobPosting) - extremely accurate for custom blogs/sites
        json_ld_tags = soup.find_all("script", type="application/ld+json")
        for tag in json_ld_tags:
            if tag.string:
                try:
                    data = json.loads(tag.string)
                    # Support single object or list of objects
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") == "JobPosting" or "JobPosting" in str(item.get("@context", "")):
                            job_id = item.get("identifier", {}).get("value") if isinstance(item.get("identifier"), dict) else item.get("identifier") or "generic-ld"
                            jobs.append({
                                "id": str(job_id),
                                "title": item.get("title"),
                                "company": item.get("hiringOrganization", {}).get("name") if isinstance(item.get("hiringOrganization"), dict) else "Company",
                                "url": item.get("url") or url,
                                "source": "Custom Website",
                                "location": item.get("jobLocation", {}).get("address", {}).get("addressLocality") if isinstance(item.get("jobLocation"), dict) else "India",
                                "description": item.get("description") or "",
                                "posted_date": item.get("datePosted") or ""
                            })
                    if jobs:
                        logger.info(f"Generic Parser: Successfully extracted {len(jobs)} jobs via JSON-LD Schema!")
                        return jobs
                except Exception as e:
                    logger.debug(f"JSON-LD extraction failed: {e}")

        # 2. Heuristics fallback: find semantic career links
        parsed_origin = urlparse(url)
        base_url = f"{parsed_origin.scheme}://{parsed_origin.netloc}"
        
        links = soup.find_all("a", href=True)
        job_pattern = re.compile(r"(careers|jobs|positions|openings|careers|opportunity|apply|vacancy|job/|detail/|vacancy/)", re.IGNORECASE)
        title_pattern = re.compile(r"(engineer|developer|architect|designer|scripter|coder|programmer|tester|analyst|administrator|manager)", re.IGNORECASE)
        
        for idx, link in enumerate(links):
            href = link["href"]
            text = link.get_text(strip=True)
            
            # Combine link href and text analysis
            is_job_link = job_pattern.search(href) or job_pattern.search(text)
            has_tech_title = title_pattern.search(text)
            
            if is_job_link and has_tech_title and len(text) > 5 and len(text) < 80:
                absolute_url = urljoin(url, href)
                job_id = f"gen-{hash(absolute_url) % 1000000}"
                
                # Check for location parent
                parent = link.find_parent(["div", "tr", "li"])
                location = "India"
                if parent:
                    # Sniff location keywords
                    parent_text = parent.get_text(strip=True)
                    for loc in ["Pune", "Bangalore", "Bengaluru", "Hyderabad", "Chennai", "Mumbai", "Remote"]:
                        if loc.lower() in parent_text.lower():
                            location = loc
                            break
                            
                jobs.append({
                    "id": str(job_id),
                    "title": text,
                    "company": parsed_origin.netloc.replace("www.", "").split(".")[0].capitalize(),
                    "url": absolute_url,
                    "source": "Custom Website",
                    "location": location,
                    "description": "",
                    "posted_date": ""
                })
                
        return jobs
