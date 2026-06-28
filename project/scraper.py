# -*- coding: utf-8 -*-
"""
Hybrid IT Job Intelligence Scraper - Main CLI Entrypoint.
Coordinates crawler, filters, validators, deduplication, cold email generator, and Excel exporter.
"""

import argparse
from .utils import logger
from .config import CAREER_PAGES, MAX_WORKERS, FRESHNESS_HOURS, PORTALS_TO_SCRAPE
from .crawler import CareerCrawler
from .portal_scrapers import PortalScraper
from .normalizer import DataNormalizer
from .extractor import InfoExtractor
from .filters import JobFilters
from .validators import JobValidator
from .dedupe import JobDeduplicator
from .cold_mail_generator import ColdEmailGenerator
from .exporters import ExcelExporter

class ITJobScraperPipeline:
    def __init__(self, use_ai=False, gemini_api_key=None):
        self.use_ai = use_ai
        self.gemini_client = None
        
        if use_ai and gemini_api_key:
            try:
                from google.genai import GoogleGenAI
                self.gemini_client = GoogleGenAI(
                    apiKey=gemini_api_key,
                    httpOptions={"headers": {"User-Agent": "aistudio-build"}}
                )
                logger.info("Pipeline: Initialized Gemini client for automated cold email generation.")
            except ImportError:
                logger.warning("Pipeline: '@google/genai' SDK is missing. Falling back to rules-based template writer.")

    def run_pipeline(self, output_file="jobs.xlsx"):
        logger.info("==============================================")
        logger.info("IT JOB INTELLIGENCE SCRAPER PIPELINE INITIATED")
        logger.info("==============================================")
        
        raw_jobs = []
        
        # 1. Crawl Official Career Pages (Source 1)
        if CAREER_PAGES:
            logger.info(f"Pipeline: Preparing to crawl {len(CAREER_PAGES)} official company career pages.")
            crawler = CareerCrawler(CAREER_PAGES, max_workers=MAX_WORKERS)
            career_jobs = crawler.run()
            raw_jobs.extend(career_jobs)
        
        # 2. Crawl Public Job Portals (Source 2)
        any_portal_active = any(PORTALS_TO_SCRAPE.values())
        if any_portal_active:
            logger.info("Pipeline: Initiating public portal scraping engine.")
            portal_scrapper = PortalScraper()
            portal_jobs = portal_scrapper.scrape_all()
            raw_jobs.extend(portal_jobs)
            
        logger.info(f"Pipeline: Collated {len(raw_jobs)} candidates from all streams. Initiating filter layer.")
        
        # 3. Normalize + Filter + Extract
        filtered_jobs = []
        for raw_job in raw_jobs:
            # Clean structure first
            norm_job = DataNormalizer.normalize_job(raw_job)
            
            # Run Strict filters (Freshness, Role Keywords, Cities)
            if not JobFilters.filter_job(norm_job):
                continue
                
            # Perform text feature extraction (Tech stack, skills, split summary)
            enriched_job = InfoExtractor.populate_extraction_fields(norm_job)
            
            filtered_jobs.append(enriched_job)
            
        logger.info(f"Pipeline: Post-filtering retained {len(filtered_jobs)} matching IT jobs.")
        
        # 4. Strict Deduplication (Layers 1-4)
        deduped_jobs = JobDeduplicator.deduplicate(filtered_jobs)
        
        # 5. Live Link Validation
        validated_jobs = []
        for idx, job in enumerate(deduped_jobs):
            logger.info(f"Pipeline: Deep-checking link {idx+1}/{len(deduped_jobs)}: {job.get('title')} at {job.get('company')}")
            if JobValidator.validate_job_fields(job):
                validated_jobs.append(job)
                
        logger.info(f"Pipeline: Successfully validated {len(validated_jobs)} high-relevance jobs.")
        
        # 6. Automated Cold Email and Strategy Generation
        logger.info("Pipeline: Triggering automated cold email generator.")
        final_jobs = []
        for job in validated_jobs:
            processed_job = ColdEmailGenerator.generate_all(job, self.gemini_client)
            final_jobs.append(processed_job)
            
        # 7. Write and Style Excel Report
        ExcelExporter.export_to_excel(final_jobs, filename=output_file)
        
        logger.info("==============================================")
        logger.info(f"PIPELINE COMPLETED. EXCEL REPORT SAVED TO: {output_file}")
        logger.info(f"METRICS: Crawled={len(raw_jobs)} -> Filtered={len(filtered_jobs)} -> Deduped={len(deduped_jobs)} -> Validated={len(validated_jobs)}")
        logger.info("==============================================")
        
        return final_jobs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hybrid IT Job Intelligence Scraper")
    parser.add_argument("--output", default="jobs.xlsx", help="Filename of the generated Excel workbook")
    parser.add_argument("--ai", action="store_true", help="Enable Gemini API for premium cold email writing")
    parser.add_argument("--apikey", default=None, help="Gemini API Key")
    
    args = parser.parse_args()
    
    pipeline = ITJobScraperPipeline(use_ai=args.ai, gemini_api_key=args.apikey)
    pipeline.run_pipeline(args.output)
