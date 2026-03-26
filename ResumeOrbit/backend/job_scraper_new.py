"""
Job Scraper Module - Using requests and BeautifulSoup
Scrapes job listings from LinkedIn's public guest API (no auth required)
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import random
import re


class JobScraper:
    """Scrape jobs from job websites using BeautifulSoup"""

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

    def get_headers(self):
        """Get headers with random user agent"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }

    def scrape_linkedin(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from LinkedIn's public guest API.
        This endpoint doesn't require authentication.
        """
        jobs = []

        try:
            for page in range(pages):
                try:
                    url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
                    params = {
                        'keywords': keywords,
                        'location': location or '',
                        'start': page * 25,
                    }

                    print(f"🔍 Scraping LinkedIn page {page + 1}...")
                    response = requests.get(url, params=params, headers=self.get_headers(), timeout=15)

                    if response.status_code != 200:
                        print(f"⚠️ LinkedIn returned status {response.status_code}")
                        continue

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find all job cards
                    job_cards = soup.find_all('div', class_='base-card')

                    if not job_cards:
                        print("⚠️ No jobs found on LinkedIn")
                        continue

                    print(f"✅ Found {len(job_cards)} jobs on LinkedIn page {page + 1}")

                    for idx, card in enumerate(job_cards):
                        try:
                            # Extract title
                            title_elem = card.find('h3', class_='base-search-card__title')
                            if not title_elem:
                                continue
                            title = title_elem.text.strip()

                            # Extract company
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            company = company_elem.text.strip() if company_elem else 'Unknown'

                            # Extract location
                            location_elem = card.find('span', class_='job-search-card__location')
                            loc = location_elem.text.strip() if location_elem else location

                            # Extract job URL
                            link_elem = card.find('a', class_='base-card__full-link')
                            job_url = ''
                            if link_elem and link_elem.get('href'):
                                job_url = link_elem['href'].split('?')[0]  # Clean URL

                            # Extract date posted
                            date_elem = card.find('time', class_='job-search-card__listdate')
                            if not date_elem:
                                date_elem = card.find('time', class_='job-search-card__listdate--new')
                            posted_date = date_elem.text.strip() if date_elem else ''

                            job = {
                                'id': f"linkedin-{page}-{idx}",
                                'title': title,
                                'company': company,
                                'location': loc,
                                'description': f"{title} at {company}. Location: {loc}",
                                'url': job_url,
                                'source': 'LinkedIn',
                                'salary': '',
                                'posted_date': posted_date
                            }

                            jobs.append(job)

                        except Exception as e:
                            print(f"❌ Error parsing job card: {e}")
                            continue

                    # Be respectful - add delay between pages
                    if page < pages - 1:
                        time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"❌ Error scraping LinkedIn page {page + 1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error with LinkedIn scraper: {e}")

        return jobs

    def scrape_indeed(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from Indeed.
        Note: Indeed has anti-scraping measures, results may vary.
        """
        jobs = []

        try:
            for page in range(pages):
                try:
                    url = 'https://www.indeed.com/jobs'
                    params = {
                        'q': keywords,
                        'l': location,
                        'start': page * 10
                    }

                    print(f"🔍 Scraping Indeed page {page + 1}...")
                    response = requests.get(url, params=params, headers=self.get_headers(), timeout=15)

                    if response.status_code != 200:
                        print(f"⚠️ Indeed returned status {response.status_code}")
                        continue

                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Try multiple selectors for job cards
                    job_cards = soup.find_all('div', class_='job_seen_beacon')
                    if not job_cards:
                        job_cards = soup.find_all('div', {'data-jk': True})
                    if not job_cards:
                        job_cards = soup.find_all('div', class_='jobsearch-ResultsList')

                    if not job_cards:
                        print("⚠️ No jobs found on Indeed (may be blocked)")
                        continue

                    for idx, card in enumerate(job_cards[:10]):
                        try:
                            title_elem = card.find('h2', class_='jobTitle') or card.find('a', class_='jobtitle')
                            if not title_elem:
                                continue

                            title = title_elem.get_text(strip=True)

                            company_elem = card.find('span', {'data-testid': 'company-name'}) or card.find('span', class_='company')
                            company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                            location_elem = card.find('div', {'data-testid': 'text-location'}) or card.find('div', class_='companyLocation')
                            loc = location_elem.get_text(strip=True) if location_elem else location

                            # Get URL
                            link_elem = card.find('a', {'href': True})
                            job_url = ''
                            if link_elem:
                                href = link_elem.get('href', '')
                                if not href.startswith('http'):
                                    href = 'https://www.indeed.com' + href
                                job_url = href

                            desc_elem = card.find('div', class_='job-snippet') or card.find('div', class_='summary')
                            description = desc_elem.get_text(strip=True) if desc_elem else ''

                            job = {
                                'id': f"indeed-{page}-{idx}",
                                'title': title,
                                'company': company,
                                'location': loc,
                                'description': description,
                                'url': job_url,
                                'source': 'Indeed',
                                'salary': ''
                            }

                            jobs.append(job)

                        except Exception:
                            continue

                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"❌ Error scraping Indeed page {page + 1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error with Indeed scraper: {e}")

        return jobs


def scrape_jobs(keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
    """
    Main function to scrape jobs from multiple sources.

    Args:
        keywords: Job search keywords
        location: Job location (optional)
        pages: Number of pages to scrape

    Returns:
        List of job dictionaries
    """
    scraper = JobScraper()
    all_jobs = []

    print(f"\n🚀 Starting job search for '{keywords}' in '{location or 'All locations'}'")
    print("=" * 60)

    # Scrape LinkedIn (most reliable - public guest API)
    print("\n📊 Scraping LinkedIn.com...")
    try:
        linkedin_jobs = scraper.scrape_linkedin(keywords, location, pages)
        all_jobs.extend(linkedin_jobs)
        print(f"✅ Found {len(linkedin_jobs)} jobs from LinkedIn")
    except Exception as e:
        print(f"❌ Error with LinkedIn: {e}")

    time.sleep(1)

    # Scrape Indeed (may be blocked)
    print("\n📊 Scraping Indeed.com...")
    try:
        indeed_jobs = scraper.scrape_indeed(keywords, location, pages)
        all_jobs.extend(indeed_jobs)
        print(f"✅ Found {len(indeed_jobs)} jobs from Indeed")
    except Exception as e:
        print(f"❌ Error with Indeed: {e}")

    print("\n" + "=" * 60)
    print(f"🎯 Total jobs found: {len(all_jobs)}")

    # Remove duplicates
    unique_jobs = []
    seen = set()

    for job in all_jobs:
        key = (job.get('title', '').lower(), job.get('company', '').lower())
        if key not in seen and job.get('title') and job.get('title') != 'N/A':
            seen.add(key)
            unique_jobs.append(job)

    if len(unique_jobs) < len(all_jobs):
        print(f"🧹 After removing duplicates: {len(unique_jobs)} unique jobs\n")

    return unique_jobs
