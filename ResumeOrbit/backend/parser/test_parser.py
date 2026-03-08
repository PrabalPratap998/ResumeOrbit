"""
Test script for the Resume Parser
"""

from resume_parser import parse_resume
import json


# Sample resume text for testing
SAMPLE_RESUME = """
JOHN SMITH
john.smith@email.com | +1 (555) 123-4567 | New York, NY
linkedin.com/in/johnsmith | github.com/johnsmith

PROFESSIONAL SUMMARY
Experienced Full Stack Developer with 5+ years of experience building scalable web applications.
Proficient in Python, JavaScript, and cloud technologies. Passionate about creating user-friendly solutions.

WORK EXPERIENCE

Senior Software Engineer | Tech Company Inc. | New York, NY
01/2022 - Present
• Led development of microservices architecture supporting 1M+ users
• Implemented CI/CD pipelines reducing deployment time by 40%
• Mentored junior developers and conducted code reviews
• Improved application performance by 35% through optimization

Software Engineer | Digital Solutions LLC | Boston, MA
06/2019 - 12/2021
• Developed full-stack web applications using React and Django
• Designed and optimized database schemas for improved query performance
• Collaborated with product team to deliver 12+ features per quarter
• Wrote comprehensive unit and integration tests achieving 85% coverage

Junior Developer | StartUp Tech | Boston, MA
03/2018 - 05/2019
• Built responsive web interfaces using HTML, CSS, and JavaScript
• Participated in agile development process with bi-weekly sprints
• Fixed bugs and maintained legacy codebase

EDUCATION

Bachelor of Science in Computer Science
University of Massachusetts | Boston, MA
Graduated: 2018
GPA: 3.8/4.0

TECHNICAL SKILLS
Languages: Python, JavaScript, Java, SQL, HTML, CSS
Frameworks: Django, React, FastAPI, Flask
Databases: PostgreSQL, MongoDB, Redis
Tools: Git, Docker, AWS, Jenkins, JIRA

CERTIFICATIONS
AWS Certified Solutions Architect - Associate (2022)
Python Professional Certificate - DataCamp (2021)
Scrum Master Certified - Scrum Alliance (2020)

PROJECTS
Real-Time Chat Application | 2021
• Built full-stack chat application using React and Django WebSockets
• Implemented real-time messaging and user authentication
• Deployed on AWS using Docker and Docker Compose

E-Commerce Platform | 2020
• Developed complete e-commerce platform with payment integration
• Implemented product search using Elasticsearch
• Created admin dashboard for inventory management

LANGUAGES
English (Native)
Spanish (Conversational)
French (Basic)
"""


def test_parser():
    """Run parser on sample resume and display results."""
    
    print("=" * 80)
    print("RESUME PARSER TEST")
    print("=" * 80)
    print()
    
    try:
        # Parse the resume
        print("📝 Parsing resume...")
        result = parse_resume(SAMPLE_RESUME)
        
        # Display results
        print("\n✅ PARSING SUCCESSFUL!\n")
        
        # Contact Info
        print("-" * 80)
        print("CONTACT INFORMATION")
        print("-" * 80)
        if result['contact_info']:
            for key, value in result['contact_info'].items():
                print(f"  {key.upper()}: {value}")
        else:
            print("  No contact info extracted")
        
        # Summary
        print("\n" + "-" * 80)
        print("PROFESSIONAL SUMMARY")
        print("-" * 80)
        if result['summary']:
            print(f"  {result['summary']}")
        else:
            print("  No summary extracted")
        
        # Experience
        print("\n" + "-" * 80)
        print("WORK EXPERIENCE")
        print("-" * 80)
        if result['experience']:
            for i, job in enumerate(result['experience'], 1):
                print(f"\n  Job {i}:")
                for key, value in job.items():
                    if key == 'description' and isinstance(value, list):
                        print(f"    {key.upper()}:")
                        for desc in value:
                            print(f"      • {desc}")
                    else:
                        print(f"    {key.upper()}: {value}")
        else:
            print("  No experience extracted")
        
        # Education
        print("\n" + "-" * 80)
        print("EDUCATION")
        print("-" * 80)
        if result['education']:
            for i, edu in enumerate(result['education'], 1):
                print(f"\n  Education {i}:")
                for key, value in edu.items():
                    print(f"    {key.upper()}: {value}")
        else:
            print("  No education extracted")
        
        # Skills
        print("\n" + "-" * 80)
        print("SKILLS")
        print("-" * 80)
        if result['skills']:
            for skill in result['skills']:
                print(f"  • {skill}")
        else:
            print("  No skills extracted")
        
        # Certifications
        print("\n" + "-" * 80)
        print("CERTIFICATIONS")
        print("-" * 80)
        if result['certifications']:
            for cert in result['certifications']:
                print(f"  • {cert}")
        else:
            print("  No certifications extracted")
        
        # Projects
        print("\n" + "-" * 80)
        print("PROJECTS")
        print("-" * 80)
        if result['projects']:
            for i, project in enumerate(result['projects'], 1):
                print(f"\n  Project {i}:")
                for key, value in project.items():
                    if key == 'description' and isinstance(value, list):
                        print(f"    {key.upper()}:")
                        for desc in value:
                            print(f"      • {desc}")
                    else:
                        print(f"    {key.upper()}: {value}")
        else:
            print("  No projects extracted")
        
        # Languages
        print("\n" + "-" * 80)
        print("LANGUAGES")
        print("-" * 80)
        if result['languages']:
            for lang in result['languages']:
                print(f"  • {lang}")
        else:
            print("  No languages extracted")
        
        # Full JSON output
        print("\n" + "=" * 80)
        print("FULL JSON OUTPUT")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_parser()
