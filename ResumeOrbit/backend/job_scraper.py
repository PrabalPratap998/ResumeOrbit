"""
Job Scraper Module
Scrapes job listings from various job websites using BeautifulSoup and requests
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import re
import json
from urllib.parse import urlencode
import random


class JobScraper:
    """Scrape jobs from various job websites using Selenium"""

    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()

            # Run in headless mode for production
            chrome_options.add_argument('--headless')

            # Additional options for better performance and compatibility
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # Speed up loading
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Uncomment for debugging (shows browser window)
            # chrome_options.headless = False

            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

            print("✅ Selenium WebDriver initialized successfully")

        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            print("Make sure ChromeDriver is installed and in PATH")
            raise

    def __del__(self):
        """Cleanup WebDriver on object destruction"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def scrape_indeed(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from Indeed.com using Selenium
        """
        jobs = []
        base_url = "https://www.indeed.com"

        try:
            for page in range(pages):
                try:
                    # Construct search URL
                    search_url = f"{base_url}/jobs?q={keywords.replace(' ', '+')}"
                    if location:
                        search_url += f"&l={location.replace(' ', '+')}"

                    if page > 0:
                        search_url += f"&start={page * 10}"

                    print(f"🔍 Scraping Indeed page {page + 1}: {search_url}")
                    self.driver.get(search_url)

                    # Wait for job cards to load
                    time.sleep(3)  # Give page time to load

                    # Try to find job cards with different selectors
                    job_selectors = [
                        'div.job-card-container',
                        'div[data-jk]',
                        'div.job_seen_beacon',
                        'a[data-jk]'
                    ]

                    job_cards = []
                    for selector in job_selectors:
                        try:
                            job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if job_cards:
                                print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                                break
                        except:
                            continue

                    if not job_cards:
                        print("⚠️ No job cards found on this page")
                        continue

                    for i, card in enumerate(job_cards[:10]):  # Limit to 10 jobs per page
                        try:
                            job_data = self._extract_indeed_job_data(card, page, i)
                            if job_data:
                                jobs.append(job_data)

                        except Exception as e:
                            print(f"❌ Error extracting job data: {e}")
                            continue

                    # Be respectful - add delay between pages
                    if page < pages - 1:
                        time.sleep(2)

                except Exception as e:
                    print(f"❌ Error scraping Indeed page {page + 1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error scraping Indeed: {e}")

        return jobs

    def _extract_indeed_job_data(self, card, page: int, index: int) -> Dict:
        """Extract job data from Indeed job card element"""
        try:
            job_data = {
                'id': f"indeed-{page}-{index}",
                'title': 'N/A',
                'company': 'N/A',
                'location': 'N/A',
                'description': '',
                'url': '',
                'source': 'Indeed',
                'salary': '',
                'posted_date': ''
            }

            # Try to find title
            title_selectors = ['a.jobtitle', 'h2 a', 'a[data-jk] span[title]', '.jobTitle']
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['title'] = title_elem.text.strip()
                    # Try to get job URL
                    if 'href' in title_elem.get_attribute('outerHTML'):
                        job_url = title_elem.get_attribute('href')
                        if job_url and not job_url.startswith('http'):
                            job_url = 'https://www.indeed.com' + job_url
                        job_data['url'] = job_url
                    break
                except:
                    continue

            # Try to find company
            company_selectors = ['span.company', '.companyName', '.company']
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['company'] = company_elem.text.strip()
                    break
                except:
                    continue

            # Try to find location
            location_selectors = ['div.recJobLoc', '.location', '.companyLocation']
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['location'] = location_elem.text.strip()
                    break
                except:
                    continue

            # Try to find salary
            try:
                salary_elem = card.find_element(By.CSS_SELECTOR, '.salary-snippet, .estimated-salary')
                job_data['salary'] = salary_elem.text.strip()
            except:
                pass

            # Try to find description/summary
            try:
                desc_elem = card.find_element(By.CSS_SELECTOR, '.summary, .job-snippet')
                job_data['description'] = desc_elem.text.strip()
            except:
                pass

            # Try to find posted date
            try:
                date_elem = card.find_element(By.CSS_SELECTOR, '.date, .jobsearch-JobMetadataFooter-item')
                job_data['posted_date'] = date_elem.text.strip()
            except:
                pass

            return job_data

        except Exception as e:
            print(f"❌ Error extracting job data: {e}")
            return None

    def scrape_linkedin(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from LinkedIn using Selenium
        """
        jobs = []
        base_url = "https://www.linkedin.com/jobs"

        try:
            for page in range(pages):
                try:
                    # Construct search URL
                    search_url = f"{base_url}/search/?keywords={keywords.replace(' ', '%20')}"
                    if location:
                        search_url += f"&location={location.replace(' ', '%20')}"

                    if page > 0:
                        search_url += f"&start={page * 25}"

                    print(f"🔍 Scraping LinkedIn page {page + 1}: {search_url}")
                    self.driver.get(search_url)

                    # Wait for page to load and handle login popup if it appears
                    time.sleep(5)

                    # Try to close any login popup
                    try:
                        close_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-tracking-control-name="public_jobs_dismiss"]')
                        close_button.click()
                        time.sleep(1)
                    except:
                        pass

                    # Try to find job cards
                    job_selectors = [
                        '.base-card',
                        '.job-card-container',
                        '.jobs-search-results__list-item'
                    ]

                    job_cards = []
                    for selector in job_selectors:
                        try:
                            job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if job_cards:
                                print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                                break
                        except:
                            continue

                    if not job_cards:
                        print("⚠️ No job cards found on this page")
                        continue

                    for i, card in enumerate(job_cards[:10]):  # Limit to 10 jobs per page
                        try:
                            job_data = self._extract_linkedin_job_data(card, page, i)
                            if job_data:
                                jobs.append(job_data)

                        except Exception as e:
                            print(f"❌ Error extracting LinkedIn job data: {e}")
                            continue

                    # Be respectful - add delay between pages
                    if page < pages - 1:
                        time.sleep(3)

                except Exception as e:
                    print(f"❌ Error scraping LinkedIn page {page + 1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error scraping LinkedIn: {e}")

        return jobs

    def _extract_linkedin_job_data(self, card, page: int, index: int) -> Dict:
        """Extract job data from LinkedIn job card element"""
        try:
            job_data = {
                'id': f"linkedin-{page}-{index}",
                'title': 'N/A',
                'company': 'N/A',
                'location': 'N/A',
                'description': '',
                'url': '',
                'source': 'LinkedIn',
                'salary': '',
                'posted_date': ''
            }

            # Try to find title
            title_selectors = ['a.job-card-list__title', '.base-card__full-link', 'h3 a']
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['title'] = title_elem.text.strip()
                    # Try to get job URL
                    job_url = title_elem.get_attribute('href')
                    if job_url:
                        # Clean up LinkedIn URL
                        if 'linkedin.com/jobs/view' in job_url:
                            job_data['url'] = job_url
                        elif '/jobs/view/' in job_url:
                            job_data['url'] = f"https://www.linkedin.com{job_url}"
                    break
                except:
                    continue

            # Try to find company
            company_selectors = ['.job-card-container__company-name', '.base-card__subtitle', 'h4 a']
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['company'] = company_elem.text.strip()
                    break
                except:
                    continue

            # Try to find location
            location_selectors = ['.job-card-container__metadata-item', '.base-card__metadata-item']
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['location'] = location_elem.text.strip()
                    break
                except:
                    continue

            # Try to find description
            try:
                desc_elem = card.find_element(By.CSS_SELECTOR, '.job-card-list__description')
                job_data['description'] = desc_elem.text.strip()
            except:
                pass

            return job_data

        except Exception as e:
            print(f"❌ Error extracting LinkedIn job data: {e}")
            return None

    def scrape_glassdoor(self, keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
        """
        Scrape jobs from Glassdoor using Selenium
        """
        jobs = []
        base_url = "https://www.glassdoor.com"

        try:
            for page in range(pages):
                try:
                    # Construct search URL
                    search_url = f"{base_url}/Job/jobs.htm?sc.keyword={keywords.replace(' ', '%20')}"
                    if location:
                        search_url += f"&locT=C&locId=0&locKeyword={location.replace(' ', '%20')}"

                    if page > 0:
                        search_url += f"&p={page + 1}"

                    print(f"🔍 Scraping Glassdoor page {page + 1}: {search_url}")
                    self.driver.get(search_url)

                    # Wait for page to load
                    time.sleep(5)

                    # Try to close any sign-up popup
                    try:
                        close_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-test="modal-close-btn"], .modal_close')
                        for btn in close_buttons:
                            try:
                                btn.click()
                                time.sleep(1)
                                break
                            except:
                                continue
                    except:
                        pass

                    # Try to find job cards
                    job_selectors = [
                        '.react-job-listing',
                        '.jobContainer',
                        '.jl'
                    ]

                    job_cards = []
                    for selector in job_selectors:
                        try:
                            job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if job_cards:
                                print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                                break
                        except:
                            continue

                    if not job_cards:
                        print("⚠️ No job cards found on this page")
                        continue

                    for i, card in enumerate(job_cards[:10]):  # Limit to 10 jobs per page
                        try:
                            job_data = self._extract_glassdoor_job_data(card, page, i)
                            if job_data:
                                jobs.append(job_data)

                        except Exception as e:
                            print(f"❌ Error extracting Glassdoor job data: {e}")
                            continue

                    # Be respectful - add delay between pages
                    if page < pages - 1:
                        time.sleep(3)

                except Exception as e:
                    print(f"❌ Error scraping Glassdoor page {page + 1}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error scraping Glassdoor: {e}")

        return jobs

    def _extract_glassdoor_job_data(self, card, page: int, index: int) -> Dict:
        """Extract job data from Glassdoor job card element"""
        try:
            job_data = {
                'id': f"glassdoor-{page}-{index}",
                'title': 'N/A',
                'company': 'N/A',
                'location': 'N/A',
                'description': '',
                'url': '',
                'source': 'Glassdoor',
                'salary': '',
                'posted_date': ''
            }

            # Try to find title
            title_selectors = ['a.jobLink', '.jobTitle', 'a[data-test="job-link"]']
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['title'] = title_elem.text.strip()
                    # Try to get job URL
                    job_url = title_elem.get_attribute('href')
                    if job_url and not job_url.startswith('http'):
                        job_url = 'https://www.glassdoor.com' + job_url
                    job_data['url'] = job_url
                    break
                except:
                    continue

            # Try to find company
            company_selectors = ['.jobHeader a', '.companyName', '.employerName']
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['company'] = company_elem.text.strip()
                    break
                except:
                    continue

            # Try to find location
            location_selectors = ['.loc', '.location']
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['location'] = location_elem.text.strip()
                    break
                except:
                    continue

            # Try to find salary
            try:
                salary_elem = card.find_element(By.CSS_SELECTOR, '.salary-estimate, .salary')
                job_data['salary'] = salary_elem.text.strip()
            except:
                pass

            # Try to find description
            try:
                desc_elem = card.find_element(By.CSS_SELECTOR, '.jobDescription, .desc')
                job_data['description'] = desc_elem.text.strip()
            except:
                pass

            return job_data

        except Exception as e:
            print(f"❌ Error extracting Glassdoor job data: {e}")
            return None


def scrape_jobs(keywords: str, location: str = '', pages: int = 1) -> List[Dict]:
    """
    Main function to scrape jobs from multiple sources using Selenium

    Args:
        keywords (str): Job search keywords
        location (str): Job location (optional)
        pages (int): Number of pages to scrape per site (default: 1)

    Returns:
        List[Dict]: List of job dictionaries
    """
    scraper = JobScraper()
    all_jobs = []

    try:
        print(f"🚀 Starting job scraping for '{keywords}' in '{location}'")

        # Scrape from multiple sources
        sources = [
            ('Indeed', scraper.scrape_indeed),
            ('LinkedIn', scraper.scrape_linkedin),
            ('Glassdoor', scraper.scrape_glassdoor)
        ]

        for source_name, scrape_func in sources:
            try:
                print(f"📊 Scraping from {source_name}...")
                jobs = scrape_func(keywords, location, pages)
                print(f"✅ Found {len(jobs)} jobs from {source_name}")
                all_jobs.extend(jobs)

                # Small delay between sources
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error scraping {source_name}: {e}")
                continue

        print(f"🎯 Total jobs scraped: {len(all_jobs)}")

        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        for job in all_jobs:
            key = (job.get('title', '').lower(), job.get('company', '').lower())
            if key not in seen and job.get('title') != 'N/A':
                seen.add(key)
                unique_jobs.append(job)

        print(f"🧹 After deduplication: {len(unique_jobs)} unique jobs")

        return unique_jobs

    except Exception as e:
        print(f"❌ Error in scrape_jobs: {e}")
        return []

    finally:
        # Cleanup
        if scraper.driver:
            try:
                scraper.driver.quit()
            except:
                pass
    
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
