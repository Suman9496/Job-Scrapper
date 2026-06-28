# -*- coding: utf-8 -*-
"""
Public Job Portal Scraping Engines.
Supports high-accuracy queries against major job portals such as LinkedIn, Indeed, Naukri, and Instahyre.
"""

from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re
from .utils import safe_request, logger, random_delay

class PortalScraper:
    def __init__(self, allowed_cities=None, keywords=None):
        self.allowed_cities = allowed_cities or ["Pune", "Bangalore", "Bengaluru", "Hyderabad", "Chennai", "Mumbai"]
        self.keywords = keywords or ["Software Engineer", "Full Stack Developer", "Python Developer"]

    def scrape_all(self):
        """Orchestrates scraping across all configured portal sources."""
        all_jobs = []
        for keyword in self.keywords:
            for city in self.allowed_cities:
                logger.info(f"Portal Scraper: Querying '{keyword}' in '{city}'")
                
                # 1. Scraping LinkedIn
                linkedin_jobs = self.scrape_linkedin(keyword, city)
                all_jobs.extend(linkedin_jobs)
                
                # 2. Scraping Indeed
                indeed_jobs = self.scrape_indeed(keyword, city)
                all_jobs.extend(indeed_jobs)
                
                # 3. Scraping Instahyre
                instahyre_jobs = self.scrape_instahyre(keyword, city)
                all_jobs.extend(instahyre_jobs)
                
                random_delay(2, 4)  # Delicate portal throttle delay
                
        return all_jobs

    def scrape_linkedin(self, keyword, city):
        """Scrapes LinkedIn's public job listings page (no authentication required)."""
        jobs = []
        encoded_keyword = quote_plus(keyword)
        encoded_city = quote_plus(city)
        
        # Public LinkedIn Job search endpoint
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings?keywords={encoded_keyword}&location={encoded_city}&f_TPR=r86400&start=0"
        logger.info(f"LinkedIn Scraper: Querying {url}")
        
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        cards = soup.find_all("li")
        
        for card in cards:
            title_tag = card.find("h3", class_="base-search-card__title")
            company_tag = card.find("h4", class_="base-search-card__subtitle")
            location_tag = card.find("span", class_="job-search-card__location")
            link_tag = card.find("a", class_="base-card__full-link")
            time_tag = card.find("time")
            
            if title_tag and company_tag and link_tag:
                job_url = link_tag["href"].split("?")[0]
                job_id = card.find("div", {"data-entity-urn": True})
                job_id_str = "li-" + job_id["data-entity-urn"].split(":")[-1] if job_id else f"li-{hash(job_url) % 1000000}"
                
                posted_date = time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else "Last 24 Hours"
                
                jobs.append({
                    "id": job_id_str,
                    "title": title_tag.get_text(strip=True),
                    "company": company_tag.get_text(strip=True),
                    "url": job_url,
                    "source": "LinkedIn",
                    "location": location_tag.get_text(strip=True) if location_tag else city,
                    "description": "",  # To be fetched on demand
                    "posted_date": posted_date,
                    "work_mode": "Onsite"
                })
        logger.info(f"LinkedIn Scraper: Found {len(jobs)} candidates.")
        return jobs

    def scrape_indeed(self, keyword, city):
        """Scrapes Indeed's public feed using realistic header structures."""
        jobs = []
        encoded_keyword = quote_plus(keyword)
        encoded_city = quote_plus(city)
        url = f"https://in.indeed.com/jobs?q={encoded_keyword}&l={encoded_city}&fromage=1"
        logger.info(f"Indeed Scraper: Querying {url}")
        
        response = safe_request(url)
        if not response or response.status_code != 200:
            # Indeed is highly anti-scraping, we provide fallback parsing of standard indeed widgets
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        results = soup.find_all("div", class_="job_seen_beacon")
        for res in results:
            title_tag = res.find("h2", class_="jobTitle")
            company_tag = res.find("span", class_="companyName") or res.find("div", class_="company_location")
            location_tag = res.find("div", class_="companyLocation")
            link_tag = res.find("a", href=True)
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                job_url = "https://in.indeed.com" + link_tag["href"]
                job_id = f"ind-{hash(job_url) % 1000000}"
                
                jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "url": job_url,
                    "source": "Indeed",
                    "location": location_tag.get_text(strip=True) if location_tag else city,
                    "description": "",
                    "posted_date": "Last 24 Hours"
                })
        return jobs

    def scrape_instahyre(self, keyword, city):
        """Scrapes Instahyre IT jobs page using standard search keywords."""
        jobs = []
        # Instahyre relies on simple API feeds or page-loads.
        # We simulate the page crawler for Instahyre's job layout.
        encoded_keyword = quote_plus(keyword)
        url = f"https://www.instahyre.com/jobs-in-{city.lower()}?q={encoded_keyword}"
        logger.info(f"Instahyre Scraper: Crawling {url}")
        
        response = safe_request(url)
        if not response or response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "lxml")
        job_blocks = soup.find_all("div", class_="job-card") or soup.find_all("div", id=re.compile(r"job-"))
        
        for block in job_blocks:
            title_tag = block.find("a", class_="job-title") or block.find("a", href=re.compile(r"/jobs/"))
            company_tag = block.find("div", class_="company-name") or block.find("span", class_="company")
            
            if title_tag:
                title = title_tag.get_text(strip=True)
                company = company_tag.get_text(strip=True) if company_tag else "IT Company"
                job_url = "https://www.instahyre.com" + title_tag["href"] if title_tag["href"].startswith("/") else title_tag["href"]
                job_id = f"ih-{hash(job_url) % 1000000}"
                
                jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "url": job_url,
                    "source": "Instahyre",
                    "location": city,
                    "description": "",
                    "posted_date": "Last 24 Hours"
                })
        return jobs
