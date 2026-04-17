#!/usr/bin/env python3
"""
Quick test script to verify the resume parser works end-to-end
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from parser.resume_parser_new import parse_resume

# Test resume text
test_resume = """
JOHN DOE
john.doe@email.com | (555) 123-4567 | San Francisco, CA
linkedin.com/in/johndoe | github.com/johndoe

PROFESSIONAL SUMMARY
Senior Python Developer with 7+ years of experience in web development and data science.

WORK EXPERIENCE

Senior Python Developer | Tech Corp | San Francisco, CA
01/2020 - Present
• Led development of REST APIs serving 100K+ users
• Implemented recommendation models for the recommendation system
• Mentored junior developers and improved code quality

Python Developer | Startup Inc | San Francisco, CA
06/2017 - 12/2019
• Built web applications using Django and React
• Optimized database queries improving performance by 50%

EDUCATION

Master of Science in Computer Science
Stanford University | Stanford, CA
Graduated: 2017
GPA: 3.9/4.0

TECHNICAL SKILLS
Python, Django, React, PostgreSQL, AWS, Docker, Git
"""

def main():
    print("🧪 Testing Resume Parser...")
    print("=" * 50)

    try:
        # Parse the resume
        result = parse_resume(test_resume)

        # Check key sections
        assert result['contact_info']['name'] == 'JOHN DOE'
        assert result['contact_info']['email'] == 'john.doe@email.com'
        assert len(result['experience']) == 2
        assert len(result['education']) == 1
        assert len(result['skills']) > 0

        print("✅ All tests passed!")
        print(f"📊 Extracted {len(result['experience'])} jobs")
        print(f"🎓 Extracted {len(result['education'])} education entries")
        print(f"🛠️  Extracted {len(result['skills'])} skills")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)