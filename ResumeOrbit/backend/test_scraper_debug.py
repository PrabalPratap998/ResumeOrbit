import sys
import os
sys.path.insert(0, r"c:\Users\New\OneDrive\Desktop\ResumeOrbit\backend")
from job_scraper_new import scrape_jobs

jobs = scrape_jobs("python developer", "remote", 1)
print(f"Found {len(jobs)} jobs")
for i, j in enumerate(jobs[:2]):
    print(f"{i+1}. {j['title']} at {j['company']} - {j['url']}")
