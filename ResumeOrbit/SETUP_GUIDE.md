# 🚀 ResumeOrbit - Complete Setup Guide

## ⭐ Project Overview

ResumeOrbit is a full-stack application with the following components:

1. **Python Backend** (Resume Parsing + Job Scraping)
   - Flask REST API (Port 5000)
   - spaCy for NLP-based resume parsing
   - Web scraping for job listings

2. **Node.js Backend** (Authentication + Job Matching)
   - Express server (Port 3000)
   - User registration/login with JWT
   - Job matching algorithm
   - SQLite database

3. **Frontend** (HTML/CSS/JavaScript)
   - Authentication pages
   - Resume upload & parsing
   - Job search & matching
   - Auto-apply feature

---

## 📋 Installation & Setup

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Install Node.js Dependencies

```bash
cd resume-builder-js
npm install
```

Or using Yarn:
```bash
yarn install
```

### Step 3: Start Python Backend

In terminal 1:
```bash
cd backend
python app.py
```

You should see:
```
🚀 Starting Resume Parser API Server...
📍 Running on http://localhost:5000
```

### Step 4: Start Node.js Backend

In terminal 2:
```bash
cd resume-builder-js
npm start
```

Or with nodemon (development):
```bash
npm run dev
```

You should see:
```
🚀 ResumeOrbit Backend Server running on http://localhost:3000
```

### Step 5: Start Frontend Server

In terminal 3:
```bash
cd frontend
python -m http.server 8000
```

### Step 6: Open in Browser

Go to: **http://localhost:8000**

---

## 🔄 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (8000)                       │
│        HTML/CSS/JavaScript - Login & Job Search         │
└──────────────┬──────────────────────────────────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼─────────┐  ┌──────▼────────┐
│ Node Backend │  │ Python Backend│
│   (3000)     │  │    (5000)      │
├──────────────┤  ├────────────────┤
│ • Auth       │  │ • Parse Resume │
│ • Job Match  │  │ • Scrape Jobs  │
│ • Database   │  │ • NLP (spaCy)  │
└──────────────┘  └────────────────┘
     │                   │
     └─────────┬─────────┘
               │
        ┌──────▼──────┐
        │   SQLite    │
        │  Database   │
        └─────────────┘
```

---

## 📚 API Endpoints

### Python API (Flask) - Port 5000

**Resume Parsing:**
```
POST /parse/text
- Parse resume from text input
- Body: { "resume_text": "..." }

POST /parse/file
- Parse resume from file upload
- Multipart: file

GET /health
- Health check
```

**Job Scraping:**
```
POST /scrape/jobs
- Scrape job listings
- Body: { "keywords": "...", "location": "...", "pages": 1 }
```

### Node.js API (Express) - Port 3000

**Authentication:**
```
POST /api/auth/register
- Register new user
- Body: { "email": "...", "password": "...", "name": "..." }

POST /api/auth/login
- Login user
- Body: { "email": "...", "password": "..." }

POST /api/auth/verify
- Verify JWT token
- Body: { "token": "..." }
```

**Resume Management:**
```
POST /api/resume/upload
- Upload and parse resume
- Headers: Authorization: Bearer <token>
- Body: { "resume_text": "...", "resume_name": "..." }

GET /api/resume/list
- Get user's resumes
- Headers: Authorization: Bearer <token>

GET /api/resume/:id
- Get specific resume
- Headers: Authorization: Bearer <token>
```

**Job Operations:**
```
POST /api/jobs/scrape
- Scrape jobs from web
- Headers: Authorization: Bearer <token>
- Body: { "keywords": "...", "location": "...", "pages": 1 }

POST /api/jobs/match
- Match jobs with resume
- Headers: Authorization: Bearer <token>
- Body: { "resume_id": 1 }

POST /api/jobs/apply/:job_id
- Apply to a job
- Headers: Authorization: Bearer <token>
- Body: { "resume_id": 1 }

GET /api/jobs/applied
- Get applied jobs
- Headers: Authorization: Bearer <token>
```

---

## 🔐 Authentication Flow

1. User creates account on frontend
2. Frontend sends registration request to Node.js backend
3. Backend creates user in SQLite database
4. Backend returns JWT token
5. Token stored in localStorage
6. All subsequent requests include token in Authorization header
7. Backend verifies token before processing requests

---

## 📊 Job Matching Algorithm

1. **Parse Resume**: Extract skills, experience, education
2. **Scrape Jobs**: Get job listings from Indeed, LinkedIn, Glassdoor
3. **Match Skills**: Compare resume skills with job requirements
4. **Calculate Score**: Match percentage based on skill overlap
5. **Display Results**: Show jobs sorted by match score
6. **Auto-Apply**: User can apply with one click

---

## 🗄️ Database Schema

### Users Table
```sql
- id (INTEGER, PRIMARY KEY)
- email (TEXT, UNIQUE)
- password (TEXT)
- name (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### Resumes Table
```sql
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY)
- name (TEXT)
- raw_text (TEXT)
- parsed_data (JSON)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### Jobs Table
```sql
- id (INTEGER, PRIMARY KEY)
- job_id (TEXT, UNIQUE)
- title (TEXT)
- company (TEXT)
- location (TEXT)
- description (TEXT)
- requirements (TEXT)
- salary_range (TEXT)
- job_url (TEXT, UNIQUE)
- source (TEXT - Indeed/LinkedIn/Glassdoor)
- posted_date (DATETIME)
- scraped_at (DATETIME)
```

### Applied_Jobs Table
```sql
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY)
- job_id (INTEGER, FOREIGN KEY)
- resume_id (INTEGER, FOREIGN KEY)
- applied_at (DATETIME)
- status (TEXT - applied/in-process/rejected)
- application_method (TEXT - auto/manual)
- response (TEXT)
```

---

## 🧪 Testing

### Test Python Backend

```bash
cd backend/parser
python test_parser.py
```

### Test Node.js Backend

```bash
cd resume-builder-js
npm test  # if tests are available
```

### Manual API Testing

**Using cURL:**

```bash
# Register
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","name":"John Doe"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Parse Resume
curl -X POST http://localhost:3000/api/resume/upload \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"resume_text":"Your resume text...","resume_name":"My Resume"}'
```

---

## 🐛 Troubleshooting

### Port 5000/3000/8000 Already in Use

**Find and kill process:**
```bash
# Windows
netstat -ano | findstr :<PORT>
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :<PORT>
kill -9 <PID>
```

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### Node Modules Not Installed
```bash
cd resume-builder-js
npm install
```

### CORS Errors
Ensure Flask-CORS is installed:
```bash
pip install Flask-CORS
```

### Database Connection Issues
Delete `data/resumeorbit.db` and restart Node server:
```bash
rm data/resumeorbit.db
npm start
```

---

## 📝 Sample Workflow

1. **User Registration**
   - Go to http://localhost:8000
   - Click "Sign Up"
   - Enter name, email, password
   - Account created

2. **Upload Resume**
   - Paste resume text or upload file
   - Click "Parse Resume"
   - View parsed data (contact, skills, experience, etc.)

3. **Search Jobs**
   - Enter job keywords: "Python Developer"
   - Enter location: "New York"
   - Click "Search Jobs"
   - System scrapes Indeed, LinkedIn, Glassdoor

4. **View Matches**
   - See jobs ranked by match score
   - View matched skills
   - Click "View Job" to visit listing

5. **Apply**
   - Click "Apply Now"
   - Application saved to database
   - View applied jobs in "Applied" section

---

## 🚀 Deployment

### Frontend
- Host on Netlify, Vercel, or GitHub Pages
- Update API_URL in app.js

### Node.js Backend  
- Deploy to Heroku, Railway, or cloud VPC
- Set environment variables (PORT, JWT_SECRET)
- Use production database

### Python Backend
- Deploy to same server or separate
- Use gunicorn for production:
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 app:app
  ```

---

## 📞 Support & Issues

For issues or questions:
1. Check terminal logs
2. Verify all services are running
3. Check database file exists: `data/resumeorbit.db`
4. Ensure ports 3000, 5000, 8000 are available

---

## 📄 License

MIT License - Feel free to use for personal or commercial projects

---

**Built with ❤️ using Node.js, Python, spaCy, and Flask**
