"""
Enhanced Job Scraper with Multiple Career Websites
Supports: LinkedIn, Indeed, Glassdoor, Monster, ZipRecruiter
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import random
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MultiSourceJobScraper:
    """Scrape jobs from multiple career websites"""

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.session = self._create_session()

    def _create_session(self):
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry = Retry(total=3, read=3, connect=3, backoff_factor=0.5, status_forcelist=(500, 502, 504))
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get_headers(self):
        """Get headers with random user agent"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

    def scrape_linkedin(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """Scrape from LinkedIn"""
        jobs = []
        try:
            for page in range(pages):
                try:
                    url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search'
                    params = {'keywords': keywords, 'location': location or '', 'start': page * 25}
                    print(f"🔍 Scraping LinkedIn page {page + 1}...")
                    response = self.session.get(url, params=params, headers=self.get_headers(), timeout=15)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-card')
                    
                    if not job_cards:
                        continue
                    
                    for idx, card in enumerate(job_cards):
                        try:
                            title = card.find('h3', class_='base-search-card__title').text.strip() if card.find('h3', class_='base-search-card__title') else 'N/A'
                            company = card.find('h4', class_='base-search-card__subtitle').text.strip() if card.find('h4', class_='base-search-card__subtitle') else 'Unknown'
                            location_elem = card.find('span', class_='job-search-card__location')
                            loc = location_elem.text.strip() if location_elem else location
                            
                            link_elem = card.find('a', class_='base-card__full-link')
                            job_url = link_elem['href'].split('?')[0] if link_elem and link_elem.get('href') else ''
                            
                            job = {
                                'id': f"linkedin-{page}-{idx}",
                                'title': title,
                                'company': company,
                                'location': loc,
                                'url': job_url,
                                'source': 'LinkedIn',
                                'salary': '',
                                'posted_date': ''
                            }
                            jobs.append(job)
                        except:
                            continue
                    
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"LinkedIn page error: {e}")
                    continue
        except Exception as e:
            print(f"LinkedIn scrape error: {e}")
        
        return jobs

    def scrape_indeed(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """Scrape from Indeed.com"""
        jobs = []
        try:
            for page in range(pages):
                try:
                    url = 'https://www.indeed.com/jobs'
                    params = {'q': keywords, 'l': location, 'start': page * 10}
                    print(f"🔍 Scraping Indeed page {page + 1}...")
                    response = self.session.get(url, params=params, headers=self.get_headers(), timeout=15)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_cards = soup.find_all('div', {'data-jk': True})
                    
                    if not job_cards:
                        continue
                    
                    for idx, card in enumerate(job_cards[:15]):
                        try:
                            title_elem = card.find('h2') or card.find('a')
                            title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                            
                            company_elem = card.find('span', {'data-testid': 'company-name'})
                            company = company_elem.get_text(strip=True) if company_elem else 'Unknown'
                            
                            location_elem = card.find('div', {'data-testid': 'text-location'})
                            loc = location_elem.get_text(strip=True) if location_elem else location
                            
                            link_elem = card.find('a', {'href': True})
                            job_url = 'https://www.indeed.com' + link_elem.get('href', '') if link_elem else ''
                            
                            job = {
                                'id': f"indeed-{page}-{idx}",
                                'title': title,
                                'company': company,
                                'location': loc,
                                'url': job_url,
                                'source': 'Indeed',
                                'salary': ''
                            }
                            jobs.append(job)
                        except:
                            continue
                    
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"Indeed page error: {e}")
                    continue
        except Exception as e:
            print(f"Indeed scrape error: {e}")
        
        return jobs

    def scrape_glassdoor(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """Scrape from Glassdoor.com"""
        jobs = []
        try:
            print(f"🔍 Scraping Glassdoor for '{keywords}'...")
            # Glassdoor API endpoint
            url = 'https://www.glassdoor.com/api/glassdoor.htm'
            params = {
                'returnUrl': 'true',
                'q': keywords,
                'locT': 'N' if location else 'C',
                'loc': location or 'United States',
                'actionType': 2
            }
            
            response = self.session.get(url, params=params, headers=self.get_headers(), timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('li', class_='jLLum0d')
                
                for idx, card in enumerate(job_cards[:10]):
                    try:
                        title = card.find('a', class_='jobTitle').text.strip() if card.find('a', class_='jobTitle') else 'N/A'
                        company = card.find('a', class_='jobCompanyName').text.strip() if card.find('a', class_='jobCompanyName') else 'Unknown'
                        
                        job = {
                            'id': f"glassdoor-{idx}",
                            'title': title,
                            'company': company,
                            'location': location,
                            'url': 'https://www.glassdoor.com',
                            'source': 'Glassdoor',
                            'salary': ''
                        }
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"Glassdoor scrape error: {e}")
        
        return jobs

    def scrape_monster(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """Scrape from Monster.com"""
        jobs = []
        try:
            print(f"🔍 Scraping Monster for '{keywords}'...")
            for page in range(pages):
                url = 'https://www.monster.com/jobs/search'
                params = {
                    'q': keywords,
                    'where': location or 'United States',
                    'page': page + 1
                }
                
                response = self.session.get(url, params=params, headers=self.get_headers(), timeout=15)
                
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-card')
                
                for idx, card in enumerate(job_cards[:12]):
                    try:
                        title = card.find('h2', class_='title').text.strip() if card.find('h2', class_='title') else 'N/A'
                        company = card.find('a', class_='company-name').text.strip() if card.find('a', class_='company-name') else 'Unknown'
                        
                        job = {
                            'id': f"monster-{page}-{idx}",
                            'title': title,
                            'company': company,
                            'location': location,
                            'url': 'https://www.monster.com',
                            'source': 'Monster',
                            'salary': ''
                        }
                        jobs.append(job)
                    except:
                        continue
                
                time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"Monster scrape error: {e}")
        
        return jobs

    def scrape_ziprecruiter(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """Scrape from ZipRecruiter.com"""
        jobs = []
        try:
            print(f"🔍 Scraping ZipRecruiter for '{keywords}'...")
            url = 'https://www.ziprecruiter.com/Jobs'
            params = {'search': keywords, 'location': location or 'United States'}
            
            response = self.session.get(url, params=params, headers=self.get_headers(), timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_card')
                
                for idx, card in enumerate(job_cards[:10]):
                    try:
                        title = card.find('h2').text.strip() if card.find('h2') else 'N/A'
                        company = card.find('span', class_='company').text.strip() if card.find('span', class_='company') else 'Unknown'
                        
                        job = {
                            'id': f"ziprecruiter-{idx}",
                            'title': title,
                            'company': company,
                            'location': location,
                            'url': 'https://www.ziprecruiter.com',
                            'source': 'ZipRecruiter',
                            'salary': ''
                        }
                        jobs.append(job)
                    except:
                        continue
        except Exception as e:
            print(f"ZipRecruiter scrape error: {e}")
        
        return jobs

    def scrape_all_sources(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """Scrape from all sources"""
        all_jobs = []
        
        print(f"\n🚀 Starting multi-source job search for '{keywords}' in '{location or 'All locations'}'")
        print("=" * 70)
        
        # LinkedIn
        print("\n📊 LinkedIn...")
        linkedin_jobs = self.scrape_linkedin(keywords, location, pages)
        all_jobs.extend(linkedin_jobs)
        print(f"✅ Found {len(linkedin_jobs)} jobs from LinkedIn")
        
        time.sleep(1)
        
        # Indeed
        print("\n📊 Indeed...")
        indeed_jobs = self.scrape_indeed(keywords, location, pages)
        all_jobs.extend(indeed_jobs)
        print(f"✅ Found {len(indeed_jobs)} jobs from Indeed")
        
        time.sleep(1)
        
        # Glassdoor
        print("\n📊 Glassdoor...")
        glassdoor_jobs = self.scrape_glassdoor(keywords, location, pages)
        all_jobs.extend(glassdoor_jobs)
        print(f"✅ Found {len(glassdoor_jobs)} jobs from Glassdoor")
        
        time.sleep(1)
        
        # Monster
        print("\n📊 Monster...")
        monster_jobs = self.scrape_monster(keywords, location, pages)
        all_jobs.extend(monster_jobs)
        print(f"✅ Found {len(monster_jobs)} jobs from Monster")
        
        time.sleep(1)
        
        # ZipRecruiter
        print("\n📊 ZipRecruiter...")
        ziprecruiter_jobs = self.scrape_ziprecruiter(keywords, location, pages)
        all_jobs.extend(ziprecruiter_jobs)
        print(f"✅ Found {len(ziprecruiter_jobs)} jobs from ZipRecruiter")
        
        print("\n" + "=" * 70)
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


def scrape_jobs_multisource(keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
    """Main function for multi-source scraping"""
    scraper = MultiSourceJobScraper()
    return scraper.scrape_all_sources(keywords, location, pages)
