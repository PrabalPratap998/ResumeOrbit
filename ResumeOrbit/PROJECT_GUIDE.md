# ResumeOrbit - Complete Project Guide

## 📋 Project Overview

**ResumeOrbit** is a comprehensive full-stack web application that combines AI-powered resume parsing with intelligent job matching and application tracking. The platform allows users to upload or paste their resumes, automatically extracts key information using Natural Language Processing (NLP), and matches them with relevant job opportunities scraped from multiple job boards.

### 🎯 Core Features

- **AI-Powered Resume Parsing**: Uses spaCy NLP to extract contact information, skills, experience, education, and more
- **Multi-Format Support**: Supports TXT, PDF, and DOCX resume uploads
- **Real-Time Job Scraping**: Scrapes jobs from Indeed, LinkedIn, and Glassdoor
- **Intelligent Job Matching**: Matches resume skills with job requirements and provides match scores
- **User Authentication**: Secure JWT-based registration and login system
- **Application Tracking**: Track job applications and application history
- **Responsive Web Interface**: Modern, mobile-friendly frontend

---

## 🏗️ Architecture & Tech Stack

### System Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Port 8000)                  │
│        HTML5/CSS3/JavaScript - User Interface           │
└─────────────────────┬───────────────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
┌──────────▼─────────┐  ┌────────▼──────────┐
│   Node.js Backend  │  │  Python Backend   │
│     (Port 3001)    │  │    (Port 5000)    │
├────────────────────┤  ├───────────────────┤
│ • User Auth        │  │ • Resume Parsing  │
│ • Job Matching     │  │ • Job Scraping    │
│ • Database Ops     │  │ • NLP Processing  │
│ • SQLite Database  │  │ • File Processing │
└────────────────────┘  └───────────────────┘
```

### Technology Stack

#### Backend (Python - Resume Processing)
- **Framework**: Flask 3.0+
- **NLP Engine**: spaCy 3.8+ with en_core_web_sm model
- **File Processing**: PyPDF2, python-docx
- **Web Scraping**: BeautifulSoup4, Selenium, Requests
- **CORS Support**: Flask-CORS

#### Backend (Node.js - User Management)
- **Framework**: Express.js 4.18+
- **Authentication**: JWT (jwt-simple), bcryptjs
- **Database**: SQLite3 with custom database layer
- **Session Management**: express-session
- **CORS**: cors middleware
- **HTTP Client**: axios

#### Frontend (Vanilla JavaScript)
- **HTML5**: Semantic markup and accessibility
- **CSS3**: Modern styling with responsive design
- **JavaScript (ES6+)**: Async/await, fetch API, localStorage
- **No Frameworks**: Pure vanilla implementation for simplicity

#### Development Tools
- **Version Control**: Git
- **Package Management**: pip (Python), npm (Node.js)
- **Process Management**: Built-in servers for development

---

## 📁 Project Structure

```
ResumeOrbit/
├── README.md                    # Main project documentation
├── QUICK_START.md              # Quick start guide for users
├── QUICKSTART.md               # Simplified quick start
├── SETUP_GUIDE.md              # Detailed setup instructions
├── TESTING_GUIDE.md            # Testing with sample data
├── PROJECT_GUIDE.md            # This comprehensive guide
├── setup.bat                   # Windows automated setup
├── setup.sh                    # Linux/Mac automated setup
├── start_services.bat          # Windows service starter
├── start_services.sh           # Linux/Mac service starter
├── TEST_DATA.json              # Test data for development
│
├── backend/                    # Python Flask API
│   ├── app.py                  # Main Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── run.bat                 # Windows runner script
│   ├── parser/                 # Resume parsing module
│   │   ├── resume_parser.py    # Core NLP parsing logic
│   │   ├── job_scraper.py      # Web scraping functionality
│   │   └── test_parser.py      # Parser testing script
│   └── uploads/                # Temporary file storage
│
├── resume-builder-js/          # Node.js Express API
│   ├── server.js               # Main Express server
│   ├── package.json            # Node.js dependencies
│   ├── run.bat                 # Windows runner script
│   ├── data/                   # Database storage
│   ├── src/
│   │   ├── db/
│   │   │   └── database.js     # SQLite database operations
│   │   └── routes/             # API route handlers
│   │       ├── auth.js         # Authentication routes
│   │       ├── jobs.js         # Job operations routes
│   │       ├── resume.js       # Resume management routes
│   │       └── user.js         # User management routes
│   └── server/                 # Additional server files
│
├── frontend/                   # Static web interface
│   ├── index.html              # Main application page
│   ├── app.js                  # Frontend application logic
│   ├── script.js               # Additional JavaScript
│   ├── style.css               # Application styling
│   └── run.bat                 # Windows runner script
│
└── sample_resumes/             # Test data
    ├── sample_resume.txt       # Full Stack Developer sample
    ├── sample_resume_2.txt     # Product Manager sample
    └── sample_resume_3.txt     # Data Scientist sample
```

---

## 🚀 Features & Capabilities

### Resume Parsing Engine
- **Contact Information**: Name, email, phone, location, LinkedIn, GitHub
- **Professional Summary**: Objective and summary extraction
- **Work Experience**: Job titles, companies, dates, descriptions
- **Education**: Degrees, institutions, GPA, graduation dates
- **Skills**: Automatic categorization and extraction
- **Certifications**: Professional certifications and licenses
- **Projects**: Personal and professional projects
- **Languages**: Spoken languages and proficiency levels

### Job Matching System
- **Multi-Source Scraping**: Indeed, LinkedIn, Glassdoor integration
- **Skill-Based Matching**: Compares resume skills with job requirements
- **Match Scoring**: Percentage-based relevance scoring
- **Location Filtering**: Geographic job search capabilities
- **Real-Time Updates**: Fresh job data on each search

### User Management
- **Secure Registration**: Email/password with validation
- **JWT Authentication**: Token-based session management
- **Resume Storage**: Multiple resume storage per user
- **Application History**: Track applied positions and status
- **Profile Management**: User account and preference settings

### File Processing
- **Text Files**: Direct parsing of .txt files
- **PDF Support**: Text extraction from PDF documents
- **Word Documents**: Content extraction from .docx files
- **File Validation**: Size limits and format checking
- **Temporary Storage**: Secure file handling and cleanup

---

## 📡 API Endpoints

### Python Backend (Port 5000)

#### Health & Status
- `GET /health` - Server health check

#### Resume Parsing
- `POST /parse/text` - Parse resume from text input
  - Body: `{"resume_text": "resume content"}`
- `POST /parse/file` - Parse resume from file upload
  - Multipart: file (txt/pdf/docx)

#### Job Scraping
- `POST /scrape/jobs` - Scrape job listings
  - Body: `{"keywords": "job title", "location": "city", "pages": 1}`

### Node.js Backend (Port 3001)

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify` - Token verification

#### Resume Management
- `POST /api/resume/upload` - Upload and parse resume
- `GET /api/resume/list` - Get user's resumes
- `GET /api/resume/:id` - Get specific resume

#### Job Operations
- `POST /api/jobs/scrape` - Scrape jobs from web
- `POST /api/jobs/match` - Match jobs with resume
- `POST /api/jobs/apply/:job_id` - Apply to a job
- `GET /api/jobs/applied` - Get applied jobs

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Resumes Table
```sql
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    raw_text TEXT,
    parsed_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    requirements TEXT,
    salary_range TEXT,
    job_url TEXT UNIQUE,
    source TEXT,
    posted_date DATETIME,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Applied_Jobs Table
```sql
CREATE TABLE applied_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    resume_id INTEGER NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'applied',
    application_method TEXT DEFAULT 'auto',
    response TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);
```

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **Web Browser** (Chrome, Firefox, Safari, Edge)

### Automated Setup (Recommended)

#### Windows
```batch
setup.bat
```

#### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

#### 1. Python Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### 2. Node.js Backend Setup
```bash
cd resume-builder-js
npm install
```

#### 3. Start Services
```bash
# Terminal 1 - Python Backend
cd backend
python app.py

# Terminal 2 - Node.js Backend
cd resume-builder-js
npm start

# Terminal 3 - Frontend
cd frontend
python -m http.server 8000
```

#### 4. Access Application
- Frontend: http://localhost:8000
- Python API: http://localhost:5000
- Node.js API: http://localhost:3001

---

## 🧪 Testing & Development

### Sample Test Data
Three comprehensive sample resumes are included:

1. **sample_resume.txt** - John Anderson (Full Stack Developer)
   - Skills: Python, JavaScript, React, Node.js, Flask, AWS
   - Test Keywords: "Python Developer", "Full Stack Engineer"

2. **sample_resume_2.txt** - Sarah Martinez (Product Manager)
   - Skills: Product Strategy, User Research, Figma, Agile
   - Test Keywords: "Product Manager", "UX Designer"

3. **sample_resume_3.txt** - Alex Chen (Data Scientist)
   - Skills: Python, Machine Learning, TensorFlow, SQL
   - Test Keywords: "Data Scientist", "Machine Learning Engineer"

### Testing Workflow
1. Register/Login at http://localhost:8000
2. Upload or paste a sample resume
3. Enter job keywords and location
4. View matched job recommendations
5. Test the apply feature

### API Testing
```bash
# Test resume parsing
curl -X POST http://localhost:5000/parse/text \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "John Doe\nPython Developer\nSkills: Python, JS"}'

# Test job scraping
curl -X POST http://localhost:5000/scrape/jobs \
  -H "Content-Type: application/json" \
  -d '{"keywords": "python developer", "location": "remote"}'
```

---

## 🔧 Configuration

### Environment Variables (Node.js)
Create `.env` file in `resume-builder-js/`:
```env
PORT=3001
JWT_SECRET=your-super-secret-jwt-key-here
PYTHON_API_URL=http://localhost:5000
NODE_ENV=development
```

### Python Configuration (app.py)
```python
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### Frontend Configuration (app.js)
```javascript
const API_BASE_URL = 'http://localhost:3001/api';
const PYTHON_API_URL = 'http://localhost:5000';
```

---

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Find process using port
netstat -ano | findstr :3001  # Windows
lsof -i :3001                 # Linux/Mac

# Kill process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/Mac
```

#### spaCy Model Missing
```bash
python -m spacy download en_core_web_sm
```

#### Node Modules Issues
```bash
cd resume-builder-js
rm -rf node_modules package-lock.json
npm install
```

#### Database Issues
```bash
cd resume-builder-js
rm data/resumeorbit.db
npm start  # Recreates database
```

#### CORS Errors
```bash
pip install Flask-CORS
# Restart Python backend
```

---

## 🚀 Deployment

### Development Deployment
- All services run locally on different ports
- SQLite database for data persistence
- File-based storage for uploads

### Production Considerations
- **Frontend**: Deploy to Netlify, Vercel, or GitHub Pages
- **Node.js Backend**: Deploy to Heroku, Railway, or VPS
- **Python Backend**: Deploy to same server or separate instance
- **Database**: Migrate from SQLite to PostgreSQL/MySQL
- **File Storage**: Use cloud storage (AWS S3, Cloudinary)
- **Environment Variables**: Configure production secrets
- **Process Management**: Use PM2, gunicorn for production servers

### Production Commands
```bash
# Python Backend (Production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Node.js Backend (Production)
npm install -g pm2
pm2 start server.js --name "resumeorbit-api"
```

---

## 🔒 Security Features

- **Password Hashing**: bcryptjs for secure password storage
- **JWT Authentication**: Token-based session management
- **CORS Protection**: Configured cross-origin policies
- **Input Validation**: File type and size restrictions
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Input sanitization
- **Rate Limiting**: Basic request throttling (configurable)

---

## 📈 Performance Considerations

- **Resume Parsing**: spaCy model loads once at startup
- **Job Scraping**: Rate limiting and caching mechanisms
- **Database**: SQLite optimized for concurrent reads
- **File Uploads**: Size limits and temporary file cleanup
- **API Responses**: JSON optimization and compression
- **Frontend**: Minimal JavaScript for fast loading

---

## 🔄 Development Workflow

### Code Organization
- **Separation of Concerns**: Each service has distinct responsibilities
- **Modular Architecture**: Reusable components and utilities
- **Error Handling**: Comprehensive error catching and logging
- **Code Comments**: Well-documented functions and classes

### Version Control
- **Git Flow**: Feature branches and pull requests
- **Commit Messages**: Descriptive commit history
- **Documentation**: Updated docs with code changes

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Manual Testing**: User workflow validation
- **Sample Data**: Comprehensive test cases

---

## 📊 Monitoring & Logging

### Application Logs
- **Python Backend**: Console logging with timestamps
- **Node.js Backend**: Request/response logging
- **Frontend**: Browser console for debugging
- **Database**: Query logging in development

### Health Checks
- `GET /health` - Python API status
- `GET /api/health` - Node.js API status
- Service availability monitoring

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Clone your fork
3. Create feature branch
4. Make changes
5. Test thoroughly
6. Submit pull request

### Code Standards
- **Python**: PEP 8 style guide
- **JavaScript**: ESLint configuration
- **Documentation**: Clear comments and docstrings
- **Testing**: Include tests for new features

---

## 📄 License

**MIT License** - Free for personal and commercial use

Copyright (c) 2024 ResumeOrbit

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

---

## 📞 Support & Resources

### Documentation Files
- `README.md` - Main project overview
- `QUICK_START.md` - User quick start guide
- `SETUP_GUIDE.md` - Detailed setup instructions
- `TESTING_GUIDE.md` - Testing with samples
- `PROJECT_GUIDE.md` - This comprehensive guide

### Getting Help
- **Issues**: GitHub Issues for bugs and feature requests
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Check all guide files first
- **Logs**: Check terminal/console output for errors

### Community
- **Contributing**: See contributing guidelines
- **Code of Conduct**: Respectful and inclusive community
- **License**: MIT - open source and free to use

---

## 🎯 Future Enhancements

### Planned Features
- [ ] Resume formatting recommendations
- [ ] Advanced job filtering options
- [ ] Resume comparison tools
- [ ] Interview preparation module
- [ ] Mobile application
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with LinkedIn API
- [ ] Resume optimization suggestions

### Technical Improvements
- [ ] Database migration to PostgreSQL
- [ ] Redis caching layer
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Automated testing suite
- [ ] Performance monitoring
- [ ] API rate limiting
- [ ] Backup and recovery systems

---

**Built with ❤️ using modern web technologies and AI-powered NLP**

*ResumeOrbit - Your AI-powered career companion*</content>
<parameter name="filePath">c:\Users\New\OneDrive\Desktop\ResumeOrbit\PROJECT_GUIDE.md