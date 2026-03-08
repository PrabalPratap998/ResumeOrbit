"""
Job Scraper Module
Scrapes job listings from various job websites
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import re


class JobScraper:
    """Scrape jobs from various job websites"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_indeed(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from Indeed.com
        """
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        try:
            for page in range(pages):
                params = {
                    'q': keywords,
                    'l': location,
                    'start': page * 10
                }
                
                response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-card-container')
                
                for job_card in job_cards:
                    try:
                        title_elem = job_card.find('a', class_='jobtitle')
                        company_elem = job_card.find('span', class_='company')
                        location_elem = job_card.find('div', class_='recJobLoc')
                        description_elem = job_card.find('div', class_='summary')
                        
                        # Extract job URL
                        job_url = title_elem.get('href', '') if title_elem else ''
                        if job_url and not job_url.startswith('http'):
                            job_url = 'https://www.indeed.com' + job_url
                        
                        job = {
                            'id': f"indeed-{page}-{len(jobs)}",
                            'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'location': location_elem.get_text(strip=True) if location_elem else location,
                            'description': description_elem.get_text(strip=True) if description_elem else '',
                            'url': job_url,
                            'source': 'Indeed'
                        }
                        jobs.append(job)
                    except Exception as e:
                        print(f"Error parsing Indeed job: {e}")
                        continue
                
                time.sleep(2)  # Be respectful to the server
        
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def scrape_linkedin(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from LinkedIn
        Note: LinkedIn has anti-scraping measures. This is a basic attempt.
        """
        jobs = []
        base_url = "https://www.linkedin.com/jobs/search"
        
        try:
            for page in range(pages):
                params = {
                    'keywords': keywords,
                    'location': location,
                    'start': page * 25
                }
                
                response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # LinkedIn structure varies, try multiple selectors
                job_cards = soup.find_all('div', class_='base-card')
                
                for job_card in job_cards:
                    try:
                        title_elem = job_card.find('h3', class_='base-search-card__title')
                        company_elem = job_card.find('h4', class_='base-search-card__subtitle')
                        location_elem = job_card.find('span', class_='job-search-card__location')
                        job_url_elem = job_card.find('a', class_='base-card__full-link')
                        
                        job = {
                            'id': f"linkedin-{page}-{len(jobs)}",
                            'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'location': location_elem.get_text(strip=True) if location_elem else location,
                            'description': '',
                            'url': job_url_elem.get('href', '') if job_url_elem else '',
                            'source': 'LinkedIn'
                        }
                        
                        if job['url']:
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error parsing LinkedIn job: {e}")
                        continue
                
                time.sleep(3)  # LinkedIn is strict with scraping
        
        except Exception as e:
            print(f"Error scraping LinkedIn: {e}")
        
        return jobs
    
    def scrape_glassdoor(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from Glassdoor
        """
        jobs = []
        base_url = "https://www.glassdoor.com/Job/jobs.htm"
        
        try:
            for page in range(pages):
                params = {
                    'sc.keyword': keywords,
                    'locT': 'C',
                    'locId': location or '1',
                    'fromage': 'any',
                    'pageNum': page + 1
                }
                
                response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('li', class_='jl')
                
                for job_item in job_items:
                    try:
                        title_elem = job_item.find('a', class_='jobTitle')
                        company_elem = job_item.find('div', class_='logoContainer')
                        location_elem = job_item.find('span', class_='jobLocation')
                        
                        job = {
                            'id': f"glassdoor-{page}-{len(jobs)}",
                            'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'location': location_elem.get_text(strip=True) if location_elem else location,
                            'description': '',
                            'url': title_elem.get('href', '') if title_elem else '',
                            'source': 'Glassdoor'
                        }
                        
                        if job['title'] != 'N/A':
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error parsing Glassdoor job: {e}")
                        continue
                
                time.sleep(2)
        
        except Exception as e:
            print(f"Error scraping Glassdoor: {e}")
        
        return jobs


def scrape_jobs(keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
    """
    Convenience function to scrape jobs from multiple sources
    """
    scraper = JobScraper()
    all_jobs = []
    
    print(f"🔍 Scraping jobs for: {keywords} in {location or 'All locations'}")
    
    # Scrape from Indeed
    print("  Scraping Indeed...")
    indeed_jobs = scraper.scrape_indeed(keywords, location, pages)
    all_jobs.extend(indeed_jobs)
    print(f"    Found {len(indeed_jobs)} jobs")
    
    # Scrape from LinkedIn
    print("  Scraping LinkedIn...")
    linkedin_jobs = scraper.scrape_linkedin(keywords, location, pages)
    all_jobs.extend(linkedin_jobs)
    print(f"    Found {len(linkedin_jobs)} jobs")
    
    # Scrape from Glassdoor
    print("  Scraping Glassdoor...")
    glassdoor_jobs = scraper.scrape_glassdoor(keywords, location, pages)
    all_jobs.extend(glassdoor_jobs)
    print(f"    Found {len(glassdoor_jobs)} jobs")
    
    print(f"\n✅ Total jobs scraped: {len(all_jobs)}")
    
    return all_jobs
