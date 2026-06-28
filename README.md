# Hybrid IT Job Intelligence Scraper

A production-grade, highly modular full-stack application and CLI scraper that crawls official company career pages and public job portals to extract, validate, deduplicate, filter, and normalize IT job postings in India, automatically writing personalized cold outreach emails.

---

## 🚀 Key Features

- **Applicant Tracking System (ATS) Detection**: Scans and auto-detects system backends (Greenhouse, Lever, Workday, SmartRecruiters, Ashby, BambooHR) to scrape structured job feeds directly via APIs.
- **Strict Role Filtration**: Strictly keeps relevant IT roles (Software Developers, AI Engineers, QA, SDET, Mobile, Cloud, DevOps) and filters out noise (Sales, Marketing, HR, BPO, Customer Support).
- **Strict Location Filters**: Only retains listings targeting core Indian tech centers: Pune, Bangalore, Hyderabad, Chennai, and Mumbai (plus India-wide Remote/Hybrid positions).
- **24-Hour Freshness Window**: Strictly filters out any postings older than 24 hours to guarantee high success rates.
- **4-Layer Deduplication Engine**:
  - *Layer 1*: Exact URL and unique job ID matching.
  - *Layer 2*: Exact body text MD5 hashing.
  - *Layer 3*: Exact composite matching (Company + Title + Location).
  - *Layer 4*: Fuzzy similarity calculation of titles at the same company using `rapidfuzz`.
- **Automated Cold Email Writer**: Integrates with the **Gemini 3.5 Flash** model to craft highly specific, professional, and personalized cold outreach emails + recruiter contact strategies for each job.
- **Professional Styled Excel Exporter**: Outputs structured, auto-fitted, freeze-paned, filterable worksheets grouped by work mode and city.

---

## 📁 Project Structure

```text
/project                     # Standard Python Codebase
  ├── config.py              # Configuration rules (Locations, Keywords, Career URLs)
  ├── utils.py               # Headers, session retries, User-Agent rotation, logging
  ├── ats_detector.py        # Sniffs domains and HTML signatures for active ATS
  ├── crawler.py             # Spawns thread pools for parallel crawler processing
  ├── portal_scrapers.py     # Crawlers targeting public job platforms
  ├── extractor.py           # Custom heuristic text extractors for tech stacks & skills
  ├── filters.py             # Rules evaluating title tech-relevance and posting age
  ├── validators.py          # Verifies URL links (HTTP 200 checks)
  ├── dedupe.py              # Exact, Composite, and Fuzzy deduplication engine
  ├── normalizer.py          # Standardizes locations, seniority levels, and work modes
  ├── cold_mail_generator.py # Formats personalized emails (using Gemini or local rules)
  ├── exporters.py           # Openpyxl styled Excel sheet writer
  └── scraper.py             # Command line wrapper running the entire pipeline
/parsers                     # Core ATS Parsers
  ├── greenhouse.py          # Greenhouse Board API and HTML scraper
  ├── lever.py               # Lever API and HTML scraping engine
  ├── workday.py             # Workday CXS Tenant REST request scraper
  ├── smartrecruiters.py     # SmartRecruiters board posting API
  ├── ashby.py               # Ashby embedded page state reader
  ├── bamboohr.py            # BambooHR list feed scraper
  └── generic.py             # Heuristics & JSON-LD (Schema.org) structured fallback
requirements.txt             # Python libraries
README.md                    # Setup and guide documentation
```

---

## 🛠️ Python Installation & CLI Execution

### 1. Prerequisite Setup
Ensure you have Python 3.9+ installed. Clone or copy the folder contents.

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Run Python Scraper Pipeline
```bash
# Run pipeline with fallback rules-based email generator (No API key required)
python -m project.scraper

# Run pipeline with Google Gemini AI cold email writer
python -m project.scraper --ai --apikey YOUR_GEMINI_API_KEY
```
This processes crawls, filters, verifies links, deduplicates listings, writes emails, and produces `jobs.xlsx` locally.

---

## ⚙️ Configuration Customization (`config.py`)

Open `project/config.py` in your favorite editor to edit settings directly:
- **`ALLOWED_CITIES`**: Customize targeted hubs (e.g. Pune, Bangalore, Chennai).
- **`ALLOWED_KEYWORDS`**: Define valid technical titles.
- **`EXCLUDED_KEYWORDS`**: Extend non-tech exclusions.
- **`CAREER_PAGES`**: Provide your list of 100-300+ company careers pages.
- **`SENDER_NAME` / `GITHUB_URL` / etc**: Configure your personal portfolio values to fill in the custom cold outreach email variables.
