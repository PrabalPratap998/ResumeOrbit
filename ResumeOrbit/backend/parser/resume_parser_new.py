"""
Resume Parser using regex and text processing.
A lightweight, reliable parser that does not require external model downloads.
"""

import re
from typing import Dict, List, Optional, Tuple
import datetime


class ResumeParser:
    """
    Resume parser using regex patterns and text processing.
    More reliable than model-heavy parsers and does not require model downloads.
    """

    def __init__(self, resume_text: str):
        """
        Initialize the parser with resume text.

        Args:
            resume_text: Raw text content of the resume
        """
        self.resume_text = resume_text
        self.lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup regex patterns for different types of information."""
        self.patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': [
                r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # US format
                r'\+\d{1,3}\s?\d{1,14}',  # International format
                r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Simple US format
            ],
            'linkedin': r'linkedin\.com/in/[\w-]+',
            'github': r'github\.com/[\w-]+',
            'website': r'https?://[^\s]+',
            'date_range': [
                r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|Present|Current)',
                r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|Present|Current',
            ],
            'gpa': r'GPA[:\s]+([0-9.]+)(?:/([0-9.]+))?',
        }

        # Section headers
        self.section_patterns = {
            'contact': r'(?i)^(?:contact\s*(?:info|information)?|personal\s*info|header)$',
            'summary': r'(?i)^(?:professional\s*)?(?:summary|objective|profile|about\s*me)$',
            'experience': r'(?i)^(?:work\s*|professional\s*)?(?:experience|employment|work\s*history)$',
            'education': r'(?i)^(?:education|educational\s*background|academic\s*background)$',
            'skills': r'(?i)^(?:technical\s*|core\s*)?(?:skills|competencies|technologies|expertise)$',
            'certifications': r'(?i)^(?:certifications?|licenses?|credentials?|qualifications?)$',
            'projects': r'(?i)^(?:projects?|portfolio|personal\s*projects?)$',
            'languages': r'(?i)^(?:languages?|language\s*proficiency|spoken\s*languages?)$',
            'achievements': r'(?i)^(?:achievements?|awards?|honors?|accomplishments?)$',
        }

    def parse(self) -> Dict:
        """
        Parse the entire resume and return structured data.

        Returns:
            Dictionary containing all extracted resume information
        """
        return {
            'contact_info': self.extract_contact_info(),
            'summary': self.extract_summary(),
            'experience': self.extract_experience(),
            'education': self.extract_education(),
            'skills': self.extract_skills(),
            'certifications': self.extract_certifications(),
            'projects': self.extract_projects(),
            'languages': self.extract_languages(),
        }

    def extract_contact_info(self) -> Dict:
        """
        Extract contact information from the top of the resume.
        """
        contact = {}
        text = self.resume_text[:1000]  # First 1000 characters usually contain contact info

        # Extract name (usually the first line or first capitalized words)
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if line and not any(char.isdigit() for char in line):  # Avoid lines with numbers
                # Check if it looks like a name (2-4 words, capitalized)
                words = line.split()
                if 1 <= len(words) <= 4 and all(word[0].isupper() for word in words if word):
                    contact['name'] = line
                    break

        # Extract email
        email_match = re.search(self.patterns['email'], text, re.IGNORECASE)
        if email_match:
            contact['email'] = email_match.group(0)

        # Extract phone
        for pattern in self.patterns['phone']:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact['phone'] = phone_match.group(0)
                break

        # Extract LinkedIn
        linkedin_match = re.search(self.patterns['linkedin'], text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group(0)

        # Extract GitHub
        github_match = re.search(self.patterns['github'], text, re.IGNORECASE)
        if github_match:
            contact['github'] = github_match.group(0)

        # Extract website
        website_match = re.search(self.patterns['website'], text, re.IGNORECASE)
        if website_match:
            contact['website'] = website_match.group(0)

        # Extract location (look for city, state patterns)
        location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, State
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)\b',  # City, Country
            r'\b(Remote|New York|San Francisco|Los Angeles|Chicago|Boston|Austin|Seattle|Denver)\b',
        ]

        for pattern in location_patterns:
            location_match = re.search(pattern, text)
            if location_match:
                contact['location'] = location_match.group(0)
                break

        return contact

    def extract_summary(self) -> Optional[str]:
        """Extract professional summary/objective."""
        summary_section = self._get_section_content('summary')
        if summary_section:
            # Clean up the summary text
            lines = [line for line in summary_section.split('\n') if line.strip()]
            return ' '.join(lines).strip()
        return None

    def extract_experience(self) -> List[Dict]:
        """
        Extract work experience information.
        """
        experience = []
        exp_section = self._get_section_content('experience')

        if not exp_section:
            return experience

        # Split into job blocks using more sophisticated logic
        job_blocks = self._split_experience_blocks(exp_section)

        for block in job_blocks:
            job = self._parse_job_block(block)
            if job and job.get('title'):
                experience.append(job)

        return experience

    def _split_experience_blocks(self, text: str) -> List[str]:
        """
        Split experience section into individual job blocks.
        """
        blocks = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        current_block = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line looks like a job title (contains job keywords)
            is_job_title = any(keyword in line.lower() for keyword in [
                'engineer', 'developer', 'manager', 'analyst', 'specialist', 'director',
                'consultant', 'architect', 'scientist', 'administrator', 'coordinator',
                'representative', 'assistant', 'lead', 'senior', 'junior', 'principal'
            ]) and not line.startswith(('•', '-', '*'))

            # Check if this line looks like a company name
            is_company = any(suffix in line.lower() for suffix in [
                'inc', 'llc', 'corp', 'ltd', 'co.', 'company', 'corporation', 'limited',
                'technologies', 'solutions', 'systems', 'labs', 'group'
            ]) and not line.startswith(('•', '-', '*'))

            # Check if next line contains a date range
            has_date_next = False
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                has_date_next = bool(re.search(r'\b(\d{1,2}/\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Present|Current)\b', next_line))

            # If we have a current block and this looks like a new job start
            if current_block and (is_job_title or (is_company and has_date_next)):
                blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)

            i += 1

        # Add the last block
        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks

    def _parse_job_block(self, block: str) -> Dict:
        """Parse a single job experience block."""
        job = {}
        lines = block.split('\n')

        # First pass: identify title, company, and duration
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith(('•', '-', '*')):
                continue

            # Check if this line contains both title and company
            if '|' in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) >= 2:
                    # Usually: Title | Company | Location
                    job['title'] = parts[0]
                    job['company'] = parts[1]
                    continue

            # Check for "at" separator
            if ' at ' in line.lower():
                parts = re.split(r'\s+at\s+', line, flags=re.IGNORECASE)
                job['title'] = parts[0].strip()
                if len(parts) > 1:
                    job['company'] = parts[1].strip()
                continue

            # Look for date ranges
            if 'duration' not in job:
                for pattern in self.patterns['date_range']:
                    date_match = re.search(pattern, line, re.IGNORECASE)
                    if date_match:
                        job['duration'] = date_match.group(0)
                        break

            # If we don't have title yet and line looks like a title
            if 'title' not in job and any(keyword in line.lower() for keyword in [
                'engineer', 'developer', 'manager', 'analyst', 'specialist', 'director'
            ]):
                job['title'] = line
                continue

            # If we don't have company yet and line looks like a company
            if 'company' not in job and any(suffix in line.lower() for suffix in [
                'inc', 'llc', 'corp', 'ltd', 'co.', 'company', 'technologies', 'solutions'
            ]):
                job['company'] = line
                continue

        # Second pass: collect description bullets
        description = []
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '·')) or (line and not any(keyword in line.lower() for keyword in ['duration', 'title', 'company'])):
                clean_line = re.sub(r'^[•\-*·]\s*', '', line).strip()
                if clean_line and len(clean_line) > 10:  # Avoid very short lines
                    description.append(clean_line)

        if description:
            job['description'] = description

        return job

    def extract_education(self) -> List[Dict]:
        """
        Extract education information.
        """
        education = []
        edu_section = self._get_section_content('education')

        if not edu_section:
            return education

        # Split into education blocks
        edu_blocks = self._split_education_blocks(edu_section)

        for block in edu_blocks:
            edu = self._parse_education_block(block)
            if edu:
                education.append(edu)

        return education

    def _split_education_blocks(self, text: str) -> List[str]:
        """
        Split education section into individual education entries.
        """
        blocks = []
        lines = text.split('\n')
        current_block = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this looks like a degree line
            is_degree_line = any(keyword in line.lower() for keyword in [
                'bachelor', 'master', 'phd', 'associate', 'diploma', 'certificate',
                'b.s.', 'b.a.', 'm.s.', 'm.a.', 'b.e.', 'm.e.', 'm.b.a.', 'm.s.c.',
                'doctor', 'degree'
            ])

            # Check if this looks like an institution line
            is_institution_line = any(keyword in line.lower() for keyword in [
                'university', 'college', 'institute', 'school', 'academy'
            ])

            # If we have a degree or institution line and current block exists, start new block
            if (is_degree_line or is_institution_line) and current_block and len(current_block) > 1:
                blocks.append('\n'.join(current_block))
                current_block = [line]
            else:
                current_block.append(line)

        # Add the last block
        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks

    def _parse_education_block(self, block: str) -> Dict:
        """Parse a single education block."""
        edu = {}
        lines = block.split('\n')

        degree_keywords = ['bachelor', 'master', 'phd', 'associate', 'diploma', 'certificate',
                          'b.s.', 'b.a.', 'm.s.', 'm.a.', 'b.e.', 'm.e.', 'm.b.a.', 'm.s.c.']

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for degree
            if any(keyword in line.lower() for keyword in degree_keywords):
                edu['degree'] = line
            # Check for institution
            elif 'institution' not in edu and ('university' in line.lower() or 'college' in line.lower() or 'institute' in line.lower()):
                edu['institution'] = line
            # Check for GPA
            elif 'gpa' not in edu:
                gpa_match = re.search(self.patterns['gpa'], line, re.IGNORECASE)
                if gpa_match:
                    edu['gpa'] = gpa_match.group(1)
            # Check for graduation year
            elif 'year' not in edu:
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    edu['year'] = year_match.group(0)

        return edu

    def extract_skills(self) -> List[str]:
        """
        Extract skills from the skills section (or the whole text if no section is found).
        """
        skills = []
        skills_section = self._get_section_content('skills')

        # Common skill categories and technologies
        skill_keywords = [
            # Programming Languages
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
            'typescript', 'scala', 'perl', 'r', 'matlab', 'sql', 'html', 'css', 'sass', 'less',

            # Frameworks & Libraries
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'express', 'laravel',
            'rails', 'asp.net', 'jquery', 'bootstrap', 'tailwind', 'material-ui',

            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'oracle',
            'sqlite', 'dynamodb', 'firebase',

            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions',
            'terraform', 'ansible', 'nginx', 'apache',

            # Tools & Technologies
            'git', 'linux', 'windows', 'macos', 'vscode', 'intellij', 'eclipse', 'postman',
            'jira', 'confluence', 'slack', 'trello',

            # Data and Analytics
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'jupyter',
            'tableau', 'power bi', 'matplotlib', 'seaborn',

            # Soft Skills
            'leadership', 'communication', 'problem solving', 'teamwork', 'agile', 'scrum',
            'project management', 'analytical thinking'
        ]

        if not skills_section:
            # Fallback: scan the entire resume text for known skills
            text_lower = self.resume_text.lower()
            for skill in skill_keywords:
                if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                    skills.append(skill.title())
            return list(set(skills))

        # Split by common delimiters and check each part
        lines = skills_section.split('\n')
        for line in lines:
            line = line.lower().strip()
            if not line or line.startswith(('skills', 'technical', 'core')):
                continue

            # Split by delimiters
            parts = re.split(r'[,;•|\-\n]', line)
            for part in parts:
                part = part.strip()
                if len(part) > 1:  # Avoid single characters
                    # Remove category labels like "Languages:", "Frameworks:", etc.
                    part = re.sub(r'^(languages|frameworks|databases|tools|technologies?|platforms?)[:\s]*', '', part, flags=re.IGNORECASE)

                    # Check if it matches known skills or looks like a technical term
                    if any(keyword in part for keyword in skill_keywords) or \
                       re.match(r'^[a-zA-Z][a-zA-Z0-9\s#+.-]*$', part):
                        # Clean up the skill name
                        skill = part.strip()
                        # Capitalize properly
                        if skill:
                            skills.append(skill.title())

        # If we still didn't find much, fallback to the entire text
        if not skills:
            text_lower = self.resume_text.lower()
            for skill in skill_keywords:
                if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                    skills.append(skill.title())

        return list(set(skills))  # Remove duplicates

    def extract_certifications(self) -> List[str]:
        """
        Extract certifications and licenses.
        """
        certifications = []
        cert_section = self._get_section_content('certifications')

        if not cert_section:
            return certifications

        lines = cert_section.split('\n')

        for line in lines:
            line = line.strip()
            if line and not line.lower().startswith(('certifications', 'licenses', 'credentials')):
                # Clean up bullet points and extra whitespace
                cert = re.sub(r'^[•\-*]\s*', '', line).strip()
                if cert and len(cert) > 3:  # Avoid very short entries
                    certifications.append(cert)

        return certifications

    def extract_projects(self) -> List[Dict]:
        """
        Extract projects information.
        """
        projects = []
        projects_section = self._get_section_content('projects')

        if not projects_section:
            return projects

        # Split into project blocks
        project_blocks = self._split_into_blocks(projects_section)

        for block in project_blocks:
            project = self._parse_project_block(block)
            if project and project.get('name'):
                projects.append(project)

        return projects

    def _parse_project_block(self, block: str) -> Dict:
        """Parse a single project block."""
        project = {}
        lines = block.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # First line is usually the project name
            if 'name' not in project and line:
                # Remove date information if present
                name = re.sub(r'\s*\([^)]*\d{4}[^)]*\)', '', line).strip()
                project['name'] = name

            # Collect description bullets
            elif line.startswith(('•', '-', '*', '·')):
                if 'description' not in project:
                    project['description'] = []
                project['description'].append(line.lstrip('•-*·').strip())

            # Technologies used
            elif 'technologies' in line.lower() or 'tech stack' in line.lower():
                tech_part = line.split(':', 1)[-1].strip()
                if tech_part:
                    project['technologies'] = [tech.strip() for tech in tech_part.split(',')]

        return project

    def extract_languages(self) -> List[str]:
        """
        Extract languages information.
        """
        languages = []
        lang_section = self._get_section_content('languages')

        if not lang_section:
            return languages

        lines = lang_section.split('\n')

        for line in lines:
            line = line.strip()
            if line and not line.lower().startswith(('languages', 'language')):
                # Clean up and extract language entries
                lang = re.sub(r'^[•\-*]\s*', '', line).strip()
                if lang and len(lang) > 1:
                    languages.append(lang)

        return languages

    def _get_section_content(self, section_name: str) -> Optional[str]:
        """
        Extract content of a specific section.
        """
        pattern = self.section_patterns.get(section_name)
        if not pattern:
            return None

        # Find the section header
        match = re.search(pattern, self.resume_text, re.MULTILINE | re.IGNORECASE)
        if not match:
            return None

        start_pos = match.start()

        # Find the next section header
        remaining_text = self.resume_text[start_pos + len(match.group(0)):]

        next_section_start = len(self.resume_text)
        for other_section, other_pattern in self.section_patterns.items():
            if other_section != section_name:
                other_match = re.search(other_pattern, remaining_text, re.MULTILINE | re.IGNORECASE)
                if other_match and other_match.start() < next_section_start:
                    next_section_start = other_match.start()

        end_pos = start_pos + len(match.group(0)) + next_section_start
        section_content = self.resume_text[start_pos:end_pos].strip()

        # Remove the header line
        lines = section_content.split('\n')
        if lines:
            lines = lines[1:]  # Remove header
            return '\n'.join(lines).strip()

        return section_content

    def _split_into_blocks(self, text: str) -> List[str]:
        """
        Split text into logical blocks (jobs, education entries, projects).
        """
        blocks = []
        current_block = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this looks like a new block header
            if (len(line.split()) <= 6 and  # Short line
                not line.startswith(('•', '-', '*', '·')) and  # Not a bullet
                not any(char.isdigit() for char in line[:4]) and  # No early numbers
                not re.search(self.patterns['date_range'][0], line)):  # Not a date range

                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                current_block.append(line)
            else:
                current_block.append(line)

        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks


def parse_resume(resume_text: str) -> Dict:
    """
    Convenience function to parse a resume using regex-based parsing.

    Args:
        resume_text: Raw text content of the resume

    Returns:
        Dictionary containing all extracted resume information
    """
    parser = ResumeParser(resume_text)
    return parser.parse()