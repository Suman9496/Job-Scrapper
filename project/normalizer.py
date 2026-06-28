# -*- coding: utf-8 -*-
"""
Data Normalization Module.
Cleans and standardizes raw fields such as locations, work modes, and seniority.
"""

import re
from .utils import logger

class DataNormalizer:
    @staticmethod
    def normalize_city(location_str):
        """
        Maps raw location strings to target cities or Remote.
        All locations are considered valid to make the search extremely broad and include all IT jobs.
        """
        if not location_str:
            return "Remote", True
            
        loc = location_str.lower()
        
        # Remote checks first
        if any(kw in loc for kw in ["remote", "wfh", "work from home", "anywhere", "home"]):
            return "Remote", True
            
        # Mapping aliases
        if "bangalore" in loc or "bengaluru" in loc:
            return "Bangalore", True
        if "pune" in loc:
            return "Pune", True
        if "hyderabad" in loc:
            return "Hyderabad", True
        if "chennai" in loc:
            return "Chennai", True
        if "mumbai" in loc or "bombay" in loc:
            return "Mumbai", True
            
        return location_str.title(), True

    @staticmethod
    def determine_work_mode(title_str, location_str, description_str=""):
        """
        Determines if a job is Onsite, Hybrid, or Remote based on text indicators.
        """
        text = f"{title_str} {location_str} {description_str}".lower()
        
        if "hybrid" in text or "work from home/office" in text:
            return "Hybrid"
        if "remote" in text or "work from home" in text or "wfh" in text or "anywhere in india" in text:
            return "Remote"
            
        return "Onsite"

    @staticmethod
    def normalize_seniority(title):
        """Standardizes seniority level from the job title."""
        title_lower = title.lower()
        if any(w in title_lower for w in ["lead", "principal", "architect", "staff"]):
            return "Lead / Architect"
        if any(w in title_lower for w in ["sr", "senior", "sr."]):
            return "Senior"
        if any(w in title_lower for w in ["jr", "junior", "associate", "entry", "intern", "fresh"]):
            return "Junior / Entry-level"
        return "Mid-Level"

    @classmethod
    def normalize_job(cls, job):
        """Runs full normalization on a job record in-place."""
        title = job.get("title", "")
        location = job.get("location", "")
        desc = job.get("description", "")
        
        # 1. Normalize city
        city, is_valid_city = cls.normalize_city(location)
        job["city"] = city
        
        # 2. Work Mode
        job["work_mode"] = cls.determine_work_mode(title, location, desc)
        
        # 3. Seniority
        job["seniority_level"] = cls.normalize_seniority(title)
        
        # 4. Clean Experience / Salary placeholders
        if "experience_required" not in job or not job["experience_required"]:
            # Heuristics extraction from title
            years_match = re.search(r"(\d+)\+?\s*(?:years|yrs)", title.lower())
            job["experience_required"] = f"{years_match.group(1)}+ years" if years_match else "1-3 years (standard)"
            
        if "salary" not in job or not job["salary"]:
            job["salary"] = "Not Disclosed"
            
        # Standardize Source Career Page / Source Platform
        if "source_career_page" in job and job["source_career_page"]:
            job["source_platform"] = "Company Career Page"
        else:
            job["source_platform"] = job.get("source", "Job Portal")
            
        return job
