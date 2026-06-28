# -*- coding: utf-8 -*-
"""
Multi-Layered Deduplication Module.
Includes URL/ID lookups, composite keys, description hashes, and fuzzy matching via RapidFuzz.
"""

import hashlib
from rapidfuzz import fuzz
from .utils import logger

class JobDeduplicator:
    @staticmethod
    def compute_description_hash(desc_text):
        """Computes MD5 hash of clean description text to deduplicate reposted texts."""
        if not desc_text:
            return ""
        # Remove whitespace to stabilize hash
        cleaned = "".join(desc_text.split()).lower()
        return hashlib.md5(cleaned.encode("utf-8")).hexdigest()

    @staticmethod
    def get_source_priority(source_str):
        """
        Calculates priority rank. Smaller is higher priority.
        Company Career Page > ATS > Job Portals
        """
        src = source_str.lower()
        if "career page" in src:
            return 1
        if "ats" in src or "greenhouse" in src or "lever" in src or "workday" in src or "ashby" in src:
            return 2
        return 3

    @classmethod
    def deduplicate(cls, jobs):
        """
        Performs four-layer strict deduplication.
        Selects best-source records and removes duplicates.
        """
        logger.info(f"Deduplicator: Commencing deduplication on {len(jobs)} jobs.")
        
        seen_urls = set()
        seen_ids = set()
        seen_composites = {} # (company, location) -> list of titles
        seen_hashes = set()
        
        unique_jobs = []
        
        # Sort jobs by source priority so better sources are processed first!
        sorted_jobs = sorted(jobs, key=lambda j: cls.get_source_priority(j.get("source_platform", "Job Portal")))
        
        for job in sorted_jobs:
            url = job.get("url", "")
            job_id = job.get("id", "")
            company = job.get("company", "").strip().lower()
            title = job.get("title", "").strip().lower()
            location = job.get("location", "").strip().lower()
            description = job.get("description", "")
            
            # Layer 1: Exact URL and ID deduplication
            if url in seen_urls or (job_id and job_id in seen_ids):
                logger.debug(f"Dedupe Layer 1: Filtered duplicate URL/ID for '{job.get('title')}'")
                continue
                
            # Layer 2: Description Hash check
            desc_hash = cls.compute_description_hash(description)
            if desc_hash and desc_hash in seen_hashes:
                logger.debug(f"Dedupe Layer 2: Filtered duplicate description hash for '{job.get('title')}'")
                continue
                
            # Layer 3: Composite (Company + Title + Location) Exact Match
            composite_key = (company, location)
            if composite_key in seen_composites:
                # Same company and location - check if this title exact matches
                if title in seen_composites[composite_key]:
                    logger.debug(f"Dedupe Layer 3: Filtered exact composite key match for '{job.get('title')}'")
                    continue
                    
                # Layer 4: Fuzzy Title Similarity check within same company
                is_fuzzy_duplicate = False
                for existing_title in seen_composites[composite_key]:
                    similarity = fuzz.ratio(title, existing_title)
                    if similarity > 82.0:  # Matches closely, e.g. "software engineer" vs "software engineer i"
                        logger.debug(f"Dedupe Layer 4: Filtered fuzzy title match '{job.get('title')}' vs '{existing_title}' ({similarity:.1f}% match)")
                        is_fuzzy_duplicate = True
                        break
                        
                if is_fuzzy_duplicate:
                    continue
                    
                seen_composites[composite_key].append(title)
            else:
                seen_composites[composite_key] = [title]
                
            # Mark as processed
            seen_urls.add(url)
            if job_id:
                seen_ids.add(job_id)
            if desc_hash:
                seen_hashes.add(desc_hash)
                
            unique_jobs.append(job)
            
        logger.info(f"Deduplicator: Deduplication completed. Retained {len(unique_jobs)} / {len(jobs)} jobs (Removed {len(jobs) - len(unique_jobs)} duplicates).")
        return unique_jobs
