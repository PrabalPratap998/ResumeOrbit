# ⚡ Quick Start Guide

Get ResumeOrbit running in 5 minutes!

## 1️⃣ Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 2️⃣ Start the API Server

```bash
python app.py
```

You should see:
```
🚀 Starting Resume Parser API Server...
📍 Running on http://localhost:5000
```

## 3️⃣ Start the Frontend Server

Open a **new terminal** and run:

```bash
cd frontend
python -m http.server 8000
```

## 4️⃣ Open in Browser

Go to: **http://localhost:8000**

## 5️⃣ Try It Out!

1. **Paste some resume text** and click "Parse Resume"
   - Or upload a file (TXT, PDF, DOCX)
2. **View parsed results** - contact info, experience, education, skills, etc.
3. **Download JSON** - export the structured data

---

## 🎯 What Happens Next?

The parser will extract:
- 👤 Contact info (name, email, phone, etc.)
- 📄 Summary/Objective
- 💼 Work experience
- 🎓 Education
- 🛠️ Skills
- 📜 Certifications
- 📦 Projects
- 🌐 Languages

## 📝 Sample Resume to Test

Paste this in the "Paste Text" tab:

```
JOHN SMITH
john@email.com | +1 (555) 123-4567 | New York, NY

PROFESSIONAL SUMMARY
Full Stack Developer with 5+ years of experience.

EXPERIENCE

Senior Engineer | Tech Corp | 01/2022 - Present
• Led development of new features
• Improved performance by 40%

EDUCATION
Bachelor of Science in Computer Science
University of Massachusetts | 2018
GPA: 3.8/4.0

SKILLS
Python, JavaScript, React, Django, PostgreSQL

LANGUAGES
English (Native), Spanish (Conversational)
```

## ❓ Troubleshooting

**Port 5000 already in use?**
```bash
# Change port in backend/app.py (line at bottom)
app.run(debug=True, host='0.0.0.0', port=5001)
```

**spaCy model not found?**
```bash
python -m spacy download en_core_web_sm
```

**CORS error?**
```bash
pip install Flask-CORS
```

**PDF/DOCX upload not working?**
```bash
pip install PyPDF2 python-docx
```

---

## 📚 More Info

See [README.md](README.md) for complete documentation.
