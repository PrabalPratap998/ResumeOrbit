#!/usr/bin/env python3
"""
Test script for the Selenium-based job scraper
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from job_scraper import scrape_jobs
    print("✅ Successfully imported scrape_jobs function")

    # Test with a simple query
    print("🚀 Testing job scraper with 'python developer'...")
    jobs = scrape_jobs('python developer', 'remote', 1)

    print(f"🎯 Found {len(jobs)} jobs")

    if jobs:
        print("\n📋 Sample job data:")
        for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
            print(f"{i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} ({job.get('source', 'N/A')})")

    print("\n✅ Test completed successfully!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure selenium is installed: pip install selenium")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()