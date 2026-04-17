import spacy
from typing import Dict, List, Optional
import re
from spacy.matcher import Matcher, PhraseMatcher


class ResumeParser:
    """
    Resume parser using spaCy for advanced text processing.
    Uses entity recognition and pattern matching for accurate extraction.
    """
    
    def __init__(self, resume_text: str, model: str = "en_core_web_sm"):
        """
        Initialize the parser with spaCy model.
        
        Args:
            resume_text: Raw text content of the resume
            model: spaCy model to use (default: en_core_web_sm)
        """
        try:
            self.spacy_model = spacy.load(model)
        except OSError:
            raise OSError(
                f"Model '{model}' not found. Install it with: "
                f"python -m spacy download {model}"
            )
        
        self.resume_text = resume_text
        self.doc = self.spacy_model(resume_text)
        self._setup_matchers()
    
    def _setup_matchers(self):
        """Setup spaCy matchers for specific patterns."""
        self.matcher = Matcher(self.spacy_model.vocab)
        
        # Email pattern
        self.matcher.add("EMAIL", [[{"LIKE_EMAIL": True}]])
        
        # Phone pattern
        phone_pattern = [
            [{"TEXT": {"REGEX": r"^\+?[1-9]\d{1,14}$"}}],
            [{"TEXT": {"REGEX": r"^\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$"}}],
        ]
        self.matcher.add("PHONE", phone_pattern)
        
        # Date patterns
        date_pattern = [
            [{"TEXT": {"REGEX": r"^\d{1,2}/\d{4}$"}}, {"IS_PUNCT": True}, {"TEXT": {"REGEX": r"^\d{1,2}/\d{4}$|^Present$|^Current$"}}],
        ]
        self.matcher.add("DATE_RANGE", date_pattern)
    
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
        Extract contact information using spaCy entity recognition.
        Extracts: name, email, phone, location, LinkedIn, GitHub
        """
        contact = {}
        
        # Email extraction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, self.resume_text)
        if email_match:
            contact['email'] = email_match.group(0)
        
        # Phone extraction
        phone_patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
            r'\+\d{1,3}\s?\d{1,14}',
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, self.resume_text)
            if phone_match:
                contact['phone'] = phone_match.group(0)
                break
        
        # LinkedIn extraction
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, self.resume_text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group(0)
        
        # GitHub extraction
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, self.resume_text, re.IGNORECASE)
        if github_match:
            contact['github'] = github_match.group(0)
        
        # Name extraction using spaCy entities (PERSON)
        for ent in self.doc.ents:
            if ent.label_ == "PERSON":
                contact['name'] = ent.text
                break
        
        # Location extraction using spaCy entities (GPE)
        locations = [ent.text for ent in self.doc.ents if ent.label_ == "GPE"]
        if locations:
            contact['location'] = locations[0]
        
        return contact
    
    def extract_summary(self) -> Optional[str]:
        """Extract professional summary using section detection."""
        summary_keywords = ['summary', 'objective', 'professional profile', 'about me']
        
        lines = self.resume_text.split('\n')
        in_summary = False
        summary_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if this is a summary header
            if any(keyword in line_lower for keyword in summary_keywords):
                in_summary = True
                continue
            
            # Check if we've hit another section
            if in_summary and line_lower and any(
                keyword in line_lower for keyword in 
                ['experience', 'education', 'skills', 'projects', 'certification']
            ):
                break
            
            # Collect summary content
            if in_summary and line.strip():
                summary_lines.append(line.strip())
        
        return '\n'.join(summary_lines) if summary_lines else None
    
    def extract_experience(self) -> List[Dict]:
        """
        Extract work experience using spaCy entity recognition for organizations and dates.
        """
        experiences = []
        experience_section = self._get_section('experience')
        
        if not experience_section:
            return []
        
        # Process experience section with spaCy
        exp_doc = self.spacy_model(experience_section)
        
        # Find organizations (ORG entities) and dates
        current_job = {}
        lines = experience_section.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for job titles
            job_keywords = ['engineer', 'developer', 'manager', 'designer', 'analyst', 
                           'consultant', 'specialist', 'architect', 'lead', 'head']
            
            if any(keyword in line.lower() for keyword in job_keywords):
                if current_job and 'title' in current_job:
                    experiences.append(current_job)
                current_job = {'title': line}
            
            # Extract organization names using NER
            line_doc = self.spacy_model(line)
            for ent in line_doc.ents:
                if ent.label_ == "ORG":
                    current_job['company'] = ent.text
            
            # Date extraction
            date_pattern = r'(\d{1,2}/\d{4}|\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|\d{4}|Present|Current)'
            date_match = re.search(date_pattern, line)
            if date_match:
                current_job['duration'] = date_match.group(0)
            
            # Description bullets
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if 'description' not in current_job:
                    current_job['description'] = []
                current_job['description'].append(line.lstrip('•-*').strip())
        
        if current_job and 'title' in current_job:
            experiences.append(current_job)
        
        return experiences
    
    def extract_education(self) -> List[Dict]:
        """
        Extract education using spaCy entity recognition for organizations and dates.
        """
        education = []
        edu_section = self._get_section('education')
        
        if not edu_section:
            return []
        
        edu_doc = self.spacy_model(edu_section)
        lines = edu_section.split('\n')
        
        current_edu = {}
        degree_keywords = ['bachelor', 'master', 'phd', 'associate', 'diploma', 'certificate',
                          'b.s.', 'b.a.', 'm.s.', 'm.a.', 'b.e.', 'm.e.']
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Degree detection
            if any(keyword in line.lower() for keyword in degree_keywords):
                if current_edu:
                    education.append(current_edu)
                current_edu = {'degree': line}
            
            # University/Institution name using NER (ORG)
            line_doc = self.spacy_model(line)
            for ent in line_doc.ents:
                if ent.label_ == "ORG":
                    current_edu['institution'] = ent.text
            
            # GPA extraction
            gpa_pattern = r'GPA[:\s]+([0-9.]+)'
            gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
            if gpa_match:
                current_edu['gpa'] = gpa_match.group(1)
            
            # Year extraction using DATE entity
            for ent in line_doc.ents:
                if ent.label_ == "DATE":
                    current_edu['year'] = ent.text
        
        if current_edu:
            education.append(current_edu)
        
        return education
    
    def extract_skills(self) -> List[str]:
        """
        Extract skills from the skills section.
        """
        skills = []
        skills_section = self._get_section('skills')
        
        if not skills_section:
            return []
        
        # Split by common delimiters
        lines = skills_section.split('\n')[1:]  # Skip header
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Split by comma, semicolon, pipe, bullet
            skill_list = re.split(r'[,;•|\-]', line)
            for skill in skill_list:
                skill = skill.strip()
                if skill and len(skill) > 1:
                    skills.append(skill)
        
        return skills
    
    def extract_certifications(self) -> List[str]:
        """
        Extract certifications and licenses.
        """
        certifications = []
        cert_section = self._get_section('certifications')
        
        if not cert_section:
            return []
        
        lines = cert_section.split('\n')[1:]  # Skip header
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                cert = line.lstrip('•-*').strip()
                if cert:
                    certifications.append(cert)
        
        return certifications
    
    def extract_projects(self) -> List[Dict]:
        """
        Extract projects with descriptions and technologies.
        """
        projects = []
        projects_section = self._get_section('projects')
        
        if not projects_section:
            return []
        
        lines = projects_section.split('\n')[1:]  # Skip header
        current_project = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Project title (usually before description or date)
            if ':' in line or re.search(r'\(.*\d{4}.*\)', line):
                if current_project and 'name' in current_project:
                    projects.append(current_project)
                title = line.split(':')[0].strip()
                current_project = {'name': title}
            
            # Project descriptions
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if 'description' not in current_project:
                    current_project['description'] = []
                current_project['description'].append(line.lstrip('•-*').strip())
        
        if current_project and 'name' in current_project:
            projects.append(current_project)
        
        return projects
    
    def extract_languages(self) -> List[str]:
        """
        Extract languages from languages section.
        """
        languages = []
        lang_section = self._get_section('languages')
        
        if not lang_section:
            return []
        
        lines = lang_section.split('\n')[1:]  # Skip header
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                lang = line.lstrip('•-*').strip()
                if lang:
                    languages.append(lang)
        
        return languages
    
    def _get_section(self, section_name: str) -> Optional[str]:
        """
        Get content of a specific section.
        
        Args:
            section_name: Name of the section (e.g., 'experience', 'education')
            
        Returns:
            Section text or None
        """
        section_headers = {
            'contact': r'(CONTACT\s+INFO|CONTACT|PHONE|EMAIL)',
            'summary': r'(PROFESSIONAL\s+SUMMARY|SUMMARY|OBJECTIVE|PROFILE)',
            'experience': r'(EXPERIENCE|WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE)',
            'education': r'(EDUCATION|EDUCATIONAL\s+BACKGROUND)',
            'skills': r'(SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES)',
            'certifications': r'(CERTIFICATIONS?|LICENSES?|CREDENTIALS?)',
            'projects': r'(PROJECTS?|PORTFOLIO)',
            'languages': r'(LANGUAGES?|LANGUAGE\s+PROFICIENCY)',
        }
        
        pattern = section_headers.get(section_name)
        if not pattern:
            return None
        
        match = re.search(pattern, self.resume_text, re.IGNORECASE)
        if not match:
            return None
        
        start_pos = match.start()
        
        # Find next section
        end_pos = len(self.resume_text)
        remaining_text = self.resume_text[match.end():]
        
        next_section_pattern = r'(CONTACT|SUMMARY|EXPERIENCE|EDUCATION|SKILLS|CERTIFICATIONS?|PROJECTS?|LANGUAGES?)'
        next_match = re.search(next_section_pattern, remaining_text, re.IGNORECASE)
        
        if next_match:
            end_pos = match.end() + next_match.start()
        
        return self.resume_text[start_pos:end_pos].strip()


def parse_resume(resume_text: str, model: str = "en_core_web_sm") -> Dict:
    """
    Convenience function to parse a resume using spaCy.
    
    Args:
        resume_text: Raw text content of the resume
        model: spaCy model to use (default: en_core_web_sm)
        
    Returns:
        Dictionary containing all extracted resume information
    """
    parser = ResumeParser(resume_text, model)
    return parser.parse()
