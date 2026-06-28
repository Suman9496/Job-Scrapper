# -*- coding: utf-8 -*-
"""
Main Crawler Orchestrator.
Spawns thread pools for high-throughput career page parsing, manages host-specific rate-limits,
auto-detects ATS platforms, and delegates to the appropriate parser.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import time
from .ats_detector import ATSDetector
from .utils import logger, random_delay
from .parsers.greenhouse import GreenhouseParser
from .parsers.lever import LeverParser
from .parsers.workday import WorkdayParser
from .parsers.smartrecruiters import SmartRecruitersParser
from .parsers.ashby import AshbyParser
from .parsers.bamboohr import BambooHRParser
from .parsers.generic import GenericParser

class CareerCrawler:
    def __init__(self, urls, max_workers=10):
        self.urls = urls
        self.max_workers = max_workers
        self.parsers = {
            "greenhouse": GreenhouseParser,
            "lever": LeverParser,
            "workday": WorkdayParser,
            "smartrecruiters": SmartRecruitersParser,
            "ashby": AshbyParser,
            "bamboohr": BambooHRParser,
            "custom": GenericParser
        }

    def _crawl_single_url(self, url):
        """Processes a single career URL: auto-detects its ATS, retrieves jobs, and normalizes them."""
        try:
            logger.info(f"Orchestrator: Initiating crawl on career page: {url}")
            
            # Detect Applicant Tracking System
            ats_type = ATSDetector.detect_ats(url)
            logger.info(f"Orchestrator: Detected ATS '{ats_type}' for {url}")
            
            # Fetch corresponding parser
            parser = self.parsers.get(ats_type, GenericParser)
            
            # Run parser and retrieve initial job list
            jobs = parser.parse(url)
            logger.info(f"Orchestrator: Extracted {len(jobs)} jobs from {url} using '{ats_type}' parser.")
            
            # Label source career page URL for transparency
            for job in jobs:
                job["source_career_page"] = url
                if "source" not in job or not job["source"]:
                    job["source"] = f"{ats_type.capitalize()} ATS"
                    
            return jobs
        except Exception as e:
            logger.error(f"Orchestrator: Fatal error scraping {url}: {e}")
            return []

    def run(self):
        """Runs the concurrent career page crawling pipeline."""
        logger.info(f"Orchestrator: Spawning ThreadPoolExecutor with {self.max_workers} workers.")
        all_jobs = []
        
        # Guard against empty lists
        if not self.urls:
            logger.warning("Orchestrator: No career URLs provided in configuration.")
            return []
            
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self._crawl_single_url, url): url for url in self.urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                except Exception as exc:
                    logger.error(f"Orchestrator: Thread execution failed for URL {url}: {exc}")
                    
        logger.info(f"Orchestrator: Crawling completed. Aggregated {len(all_jobs)} raw jobs from career pages.")
        return all_jobs
