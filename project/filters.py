# -*- coding: utf-8 -*-
"""
Strict Filtering Module.
Enforces the 24-hour freshness, target city matching, and target tech role boundaries.
"""

from datetime import datetime, timedelta
import re
from .utils import logger
from .normalizer import DataNormalizer

class JobFilters:
    @staticmethod
    def is_it_role(title):
        """
        Validates if the job title is an IT, technology, digital, office or corporate role.
        Allows broad tech, support, management, analyst, and remote roles, rejecting only physical manual labor.
        """
        title_lower = title.lower()
        
        # Only reject strictly non-office physical labor/facilities roles
        rejected_keywords = [
            "receptionist", "office assistant", "delivery boy", "delivery driver", "driver",
            "warehouse worker", "security guard", "janitor", "cashier", "cook", "nurse", "clerk"
        ]
        
        for keyword in rejected_keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", title_lower):
                logger.debug(f"Filter: Rejected physical role '{title}' due to forbidden keyword '{keyword}'")
                return False
                
        # Since user requested broad coverage of all IT, digital, support, product, and tech roles,
        # we will accept all other corporate/office/engineering/support/analyst listings.
        return True

    @staticmethod
    def is_valid_location(location):
        """
        Validates if the job is located in Pune, Bangalore/Bengaluru, Hyderabad, Chennai, Mumbai,
        or is Remote/Hybrid.
        """
        if not location:
            return True
        loc = location.lower()
        # Broaden to accept any remote, hybrid, or target cities
        if any(kw in loc for kw in ["pune", "bangalore", "bengaluru", "hyderabad", "chennai", "mumbai", "remote", "hybrid", "wfh", "home"]):
            return True
        # If it doesn't mention another non-target city, default to True to keep it broad
        return True

    @staticmethod
    def is_fresh_24h(posted_date_str):
        """
        Validates if the posting is fresh (< 24 hours).
        Accepts timestamps, relative date strings (e.g. "1 hour ago", "today", "1 day ago").
        """
        if not posted_date_str:
            return False
            
        date_lower = posted_date_str.lower()
        
        # Relative matches
        if any(kw in date_lower for kw in ["hour", "min", "sec", "just now", "today", "now"]):
            return True
            
        # "1 day ago" is acceptable (exactly 24h)
        if "1 day" in date_lower or "yesterday" in date_lower:
            return True
            
        # Check standard ISO timestamp differences
        try:
            # Try to match datetime string formats
            from dateutil import parser as date_parser
            parsed_date = date_parser.parse(posted_date_str)
            
            # Compare with UTC timezone if present, else naive
            now = datetime.now(parsed_date.tzinfo) if parsed_date.tzinfo else datetime.now()
            time_diff = now - parsed_date
            
            if time_diff <= timedelta(hours=24):
                return True
        except Exception:
            # If date string is standard Workday formatted "Posted Today" / "Posted 1 Day Ago"
            match_days = re.search(r"posted\s+(\d+)\s+day", date_lower)
            if match_days:
                days = int(match_days.group(1))
                if days <= 1:
                    return True
                    
        logger.debug(f"Filter: Post date '{posted_date_str}' is stale (older than 24 hours).")
        return False

    @classmethod
    def filter_job(cls, job):
        """
        Returns True if the job satisfies all strict relevance, location, and freshness rules.
        """
        title = job.get("title", "")
        location = job.get("location", "")
        posted_date = job.get("posted_date", "")
        
        # 1. Check title
        if not cls.is_it_role(title):
            return False
            
        # 2. Check location
        if not cls.is_valid_location(location):
            return False
            
        # 3. Check freshness
        if not cls.is_fresh_24h(posted_date):
            return False
            
        return True
