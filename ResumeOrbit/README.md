# ResumeOrbit - AI-Powered Resume Parser & Job Matcher

A comprehensive full-stack application that parses resumes using advanced NLP and matches them with relevant job opportunities. Upload your resume and discover personalized job recommendations based on your skills and experience.

## 🚀 Features

### Resume Parsing
- **Multiple Input Methods**: Paste resume text directly or upload files (TXT, PDF, DOCX)
- **Advanced NLP**: Uses spaCy for Named Entity Recognition and pattern matching
- **Comprehensive Extraction**:
  - Contact Information (name, email, phone, location, LinkedIn, GitHub)
  - Professional Summary
  - Work Experience (titles, companies, dates, descriptions)
  - Education (degrees, institutions, GPA, graduation year)
  - Skills (automatically categorized)
  - Certifications & Licenses
  - Projects & Languages

### Job Matching & Recommendations
- **Real-time Job Scraping**: Scrapes jobs from LinkedIn and other sources
- **Intelligent Matching**: Matches resume skills with job requirements
- **Personalized Recommendations**: Ranked job suggestions with match scores
- **Skill-based Filtering**: Shows which skills match each job

### User Management
- **Secure Authentication**: JWT-based user registration and login
- **Resume Storage**: Save multiple resumes per user
- **Job Application Tracking**: Track applied positions

## 🏗️ Architecture

```
ResumeOrbit/
├── backend/                    # Python Flask API
│   ├── app.py                 # Resume parsing & job scraping
│   ├── requirements.txt       # Python dependencies
│   └── parser/
│       ├── resume_parser.py   # NLP parsing logic
│       └── job_scraper.py     # Web scraping functionality
├── resume-builder-js/         # Node.js Express API
│   ├── server.js              # User auth & job matching
│   ├── package.json           # Node.js dependencies
│   └── src/
│       ├── routes/            # API routes
│       └── db/                # SQLite database
├── frontend/                  # Static web interface
│   ├── index.html            # Main UI
│   ├── app.js                # Frontend logic
│   └── style.css             # Modern styling
```

## 🛠️ Tech Stack

- **Backend (Python)**: Flask, spaCy, BeautifulSoup, Selenium
- **Backend (Node.js)**: Express.js, SQLite3, JWT, bcryptjs
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite3
- **Authentication**: JWT tokens
- **Scraping**: Requests, BeautifulSoup (with Selenium fallback)

## 📋 Prerequisites

- **Python 3.8+** (with pip)
- **Node.js 16+** (with npm)
- **Git** (for version control)
- **Windows/Linux/Mac** (cross-platform)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

1. **Run the setup script**:
   ```bash
   # On Windows
   setup.bat

   # On Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Open your browser**:
   - Frontend: http://localhost:8000
   - Python API: http://localhost:5000
   - Node.js API: http://localhost:3001

### Option 2: Manual Setup

#### 1. Python Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Start the server
python app.py
```

#### 2. Node.js Backend Setup

```bash
# Navigate to Node.js backend
cd resume-builder-js

# Install dependencies
npm install

# Start the server
npm start
```

#### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Start local server
python -m http.server 8000
```

## 📖 API Documentation

### Python Backend (Port 5000)

#### Health Check
```http
GET /health
```

#### Parse Resume from Text
```http
POST /parse/text
Content-Type: application/json

{
  "resume_text": "Your resume content here..."
}
```

#### Parse Resume from File
```http
POST /parse/file
Content-Type: multipart/form-data

file: <resume_file>
```

#### Scrape Jobs
```http
POST /scrape/jobs
Content-Type: application/json

{
  "keywords": "python developer",
  "location": "remote",
  "pages": 1
}
```

### Node.js Backend (Port 3001)

#### Authentication
```http
POST /api/auth/register
POST /api/auth/login
```

#### Resume Management
```http
POST /api/resume/upload    # Upload & parse resume
GET  /api/resume/list      # Get user's resumes
```

#### Job Matching
```http
POST /api/jobs/scrape      # Scrape jobs from web
POST /api/jobs/match       # Match jobs with resume
GET  /api/jobs/matched/:resume_id  # Get matched jobs
```

## 🧪 Testing

Use your own resume text (paste into the UI or upload a file) to exercise parsing and job matching end-to-end.

### API Testing
```bash
# Test parsing
curl -X POST http://localhost:5000/parse/text \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"John Doe\nPython Developer\nSkills: Python, JavaScript"}'

# Test job scraping
curl -X POST http://localhost:5000/scrape/jobs \
  -H "Content-Type: application/json" \
  -d '{"keywords":"python developer"}'
```

### Full Workflow Test
1. Register/Login via frontend
2. Upload a sample resume
3. Search for jobs (e.g., "python developer")
4. View personalized job recommendations

## 🔧 Configuration

### Environment Variables
Create `.env` file in `resume-builder-js/`:
```env
PORT=3001
JWT_SECRET=your-secret-key-here
PYTHON_API_URL=http://localhost:5000
```

### Database
SQLite database is created automatically in `resume-builder-js/data/`

## 🐛 Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Find process using port
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

**spaCy model not found**:
```bash
python -m spacy download en_core_web_sm
```

**Node.js dependencies**:
```bash
cd resume-builder-js
rm -rf node_modules package-lock.json
npm install
```

**Python virtual environment**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Service Status Check
- Python API: http://localhost:5000/health
- Node.js API: http://localhost:3001/api/health
- Frontend: http://localhost:8000

## 📊 Sample Output

### Parsed Resume
```json
{
  "contact_info": {
    "name": "John Anderson",
    "email": "john.anderson@email.com",
    "phone": "(555) 123-4567",
    "location": "San Francisco, CA"
  },
  "summary": "Experienced Full Stack Developer...",
  "experience": [...],
  "skills": ["Python", "JavaScript", "React", "Django"],
  "education": [...]
}
```

### Job Recommendations
```json
{
  "success": true,
  "matches": [
    {
      "job_title": "Senior Python Developer",
      "company": "Tech Corp",
      "match_score": 85,
      "matched_skills": ["Python", "Django"],
      "location": "Remote"
    }
  ]
}
```

## 🚀 Deployment

### Local Development
Follow the setup instructions above.

### Production Deployment
1. Set up production servers for Python and Node.js backends
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Enable HTTPS
5. Configure database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - Free for personal and commercial use.

## 📧 Support

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Email**: Contact the maintainers

---

**Built with ❤️ using modern web technologies and AI-powered NLP**
pip install -r requirements.txt
```

#### Step 2: Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

#### Step 3: Install Optional Dependencies (for PDF & DOCX support)
```bash
pip install PyPDF2 python-docx
```

### 2. Frontend Setup
No installation needed! The frontend is plain HTML, CSS, and JavaScript.

## 🏃 Running the Application

### Start the Backend API Server

```bash
cd backend
python app.py
```

The API will start at `http://localhost:5000`

You should see:
```
🚀 Starting Resume Parser API Server...
📍 Running on http://localhost:5000
📚 API Documentation: http://localhost:5000
```

### Open the Frontend

1. **Using a local server** (recommended):
```bash
cd frontend
python -m http.server 8000
```
Then open `http://localhost:8000` in your browser.

2. **Direct file opening**:
- Simply open `frontend/index.html` in your web browser
- Note: File upload may not work due to CORS/security restrictions

## 📖 API Endpoints

### 1. Health Check
```
GET /health
```
Returns server status.

### 2. Parse Resume from Text
```
POST /parse/text
Content-Type: application/json

{
    "resume_text": "Your resume text here..."
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "contact_info": {...},
        "summary": "...",
        "experience": [...],
        "education": [...],
        "skills": [...],
        "certifications": [...],
        "projects": [...],
        "languages": [...]
    }
}
```

### 3. Parse Resume from File
```
POST /parse/file
Content-Type: multipart/form-data

file: <resume.txt|resume.pdf|resume.docx>
```

Same response format as `/parse/text`.

## 🧪 Testing

### Test the Parser Locally
```bash
cd backend/parser
python test_parser.py
```

This will run the parser on a sample resume and display all extracted information.

### Test with cURL
```bash
# Text parsing
curl -X POST http://localhost:5000/parse/text \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"Your resume text here..."}'

# File upload
curl -X POST http://localhost:5000/parse/file \
  -F "file=@resume.txt"
```

## 🎨 Frontend Features

### Paste Resume Text
1. Click the "Paste Text" tab
2. Paste your resume content
3. Click "Parse Resume"
4. View results

### Upload Resume File
1. Click the "Upload File" tab
2. Click the upload area or drag & drop a file
3. Click "Parse Resume"
4. View results

### Download Results
- Click "Download JSON" to export parsed data
- Click "Parse Another Resume" to reset the form

## 📁 File Format Support

- **TXT**: Plain text files (best supported)
- **PDF**: Requires PyPDF2
- **DOCX**: Requires python-docx

## ⚙️ Configuration

### Backend Configuration (app.py)
- `MAX_FILE_SIZE`: 10MB (configurable)
- `ALLOWED_EXTENSIONS`: txt, pdf, docx (configurable)
- `UPLOAD_FOLDER`: Temporary file storage

### frontend Configuration (script.js)
- `API_URL`: Points to `http://localhost:5000`
- Modify if backend runs on different host/port

## 🐛 Troubleshooting

### CORS Errors
Ensure Flask-CORS is installed:
```bash
pip install Flask-CORS
```

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### PDF/DOCX Upload Not Working
Install additional libraries:
```bash
pip install PyPDF2 python-docx
```

### Port 5000 Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📊 Sample Output

```json
{
  "contact_info": {
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1 (555) 123-4567",
    "location": "New York, NY",
    "linkedin": "linkedin.com/in/johnsmith",
    "github": "github.com/johnsmith"
  },
  "summary": "Experienced Full Stack Developer...",
  "experience": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Company Inc.",
      "duration": "01/2022 - Present",
      "description": ["Led development...", "Implemented CI/CD..."]
    }
  ],
  "skills": ["Python", "JavaScript", "React", "Django"],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "University of Massachusetts",
      "year": "2018",
      "gpa": "3.8"
    }
  ]
}
```

## 🚀 Future Enhancements

- [ ] Database integration to save parsed resumes
- [ ] User authentication & resume storage
- [ ] Resume matching with job descriptions
- [ ] Support for more file formats
- [ ] Multiple language support
- [ ] Resume formatting recommendations
- [ ] Duplicate resume detection

## 📝 License

MIT License - Feel free to use this project for personal or commercial use.

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue in the repository.

---

**Built with ❤️ using spaCy, Flask, and modern web technologies**
