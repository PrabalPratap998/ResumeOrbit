# Quick Start Guide - ResumeOrbit

## 🚀 Getting Started

### **Services Running?**
Before testing, make sure all three services are running on your local machine:
- **Python Backend**: http://localhost:5000 (Flask)
- **Node.js Backend**: http://localhost:3001 (Express)
- **Frontend**: http://localhost:8000 (Web App)

---

## 📋 How to Use ResumeOrbit

### **Step 1: Create Account or Login**
- Visit http://localhost:8000
- Click **"Sign Up"** to create a new account OR **"Login"** if you have one
- Fill in your email, password, and name (for signup)

### **Step 2: Upload Your Resume**
Choose one of two methods:

**Option A: Paste Text**
1. Click **"Paste Text"** tab
2. Copy and paste your resume content
3. Click **"Parse Resume"** button

**Option B: Upload File**
1. Click **"Upload File"** tab
2. Click the upload area or drag & drop your file (TXT, PDF, DOCX supported)
3. Your resume will be automatically processed

### **Step 3: Find Jobs**
1. After resume is parsed, **Job Recommendations** section appears
2. Enter job keywords (e.g., "Python Developer", "Frontend Engineer")
3. Enter desired location (e.g., "Remote", "New York", "San Francisco")
4. Click **"Search Jobs"** button

### **Step 4: View & Apply**
1. Job recommendations appear with match scores
2. Each job card shows:
   - **Job title** and **company name**
   - **Location** 
   - **Match score** (percentage)
   - **Matched skills** (top 5)
   - **Job description** preview
3. Click **"View Full Listing"** to see the full job on original site
4. Click **"Apply Now"** to apply (saves application to database)

---

## 🎯 Key Features

### **Smart Match Scoring**
- **Green (80%+)**: Excellent Match
- **Orange (60-79%)**: Good Match  
- **Red (<60%)**: Fair Match

### **Job Ranking**
- Jobs are numbered (#1, #2, #3) and sorted by match score
- Highest matches appear first

### **Skill Matching**
- Shows which of your resume skills match the job requirements
- Top 5 matched skills displayed as badges

### **Auto-Apply**
- Click "Apply Now" to apply with one click
- Application is saved to your account history

---

## 📁 Sample Resumes to Test With

Three complete sample resumes are included:

1. **sample_resume.txt** 
   - Full Stack Developer
   - Test keywords: "Python Developer", "Full Stack Engineer"

2. **sample_resume_2.txt**
   - Product Manager & UX Designer
   - Test keywords: "Product Manager", "UX Designer"

3. **sample_resume_3.txt**
   - Data Scientist & ML Engineer
   - Test keywords: "Data Scientist", "Machine Learning Engineer"

See **TESTING_GUIDE.md** for detailed testing instructions.

---

## 🔑 Important Notes

✅ **What Happens Automatically:**
- Resume parsing (silent - no loading message)
- Skill extraction from your resume
- Job scraping from multiple sites (Indeed, LinkedIn, Glassdoor)
- Match scoring based on your skills

✅ **What You Control:**
- Job keywords to search for
- Location preference
- Which jobs to apply to
- Your account and resume data

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Node Backend**: Express.js, SQLite3, JWT Auth
- **Python Backend**: Flask, spaCy NLP, BeautifulSoup Web Scraping
- **Database**: SQLite (local file-based)

---

## 📊 Data Stored

The app stores:
- **Your Account**: Email, encrypted password, name
- **Your Resumes**: Raw text and parsed data (skills, experience, education, etc.)
- **Job Applications**: Which jobs you've applied to and when
- **Job Listings**: Scraped from job sites
- **Job Matches**: Match scores and matched skills

All data is stored locally in SQLite database.

---

## 🤔 FAQ

**Q: How does the matching work?**
A: System extracts skills from your resume and matches them against job descriptions. Each matched skill adds points to the final match score.

**Q: Can I upload PDF or Word documents?**
A: Yes! The app supports TXT, PDF (.pdf), and Word (.docx) files.

**Q: Where are jobs scraped from?**
A: Jobs are scraped from Indeed, LinkedIn, and Glassdoor in real-time.

**Q: Is my data secure?**
A: Passwords are encrypted with bcryptjs. All data is stored locally on your machine.

**Q: Can I apply to the same job twice?**
A: No, the system tracks applications and won't let you apply to the same job twice.

**Q: How do I delete my account?**
A: Your account can be deleted from profile settings (all associated data will be deleted).

---

## 💡 Pro Tips

1. **Use Realistic Job Titles**: "Python Developer" works better than "Development Programmer"
2. **Be Specific with Location**: "Remote" often gets more results than leaving blank
3. **Try Different Keywords**: "Full Stack Developer" vs "Backend Engineer" may yield different results
4. **Check Matched Skills**: Look at which skills are being matched to understand scoring
5. **Save Your Resume**: You can upload multiple resumes and switch between them

---

## 🚨 Troubleshooting

**Can't login?**
- Check that Node backend is running on port 3001
- Try refreshing the page
- Check browser console (F12) for errors

**No jobs showing up?**
- Make sure you entered job keywords (required)
- Check that Python backend is running on port 5000
- Try different keywords (some may not have results)

**Resume not parsing?**
- Make sure resume has clear sections
- For PDF/DOCX: check that file isn't corrupted
- Check Python backend is on port 5000

**Jobs showing 0% match?**
- This means no skills in your resume match job requirements
- Try searching for different jobs or verify resume was uploaded
- Check that skills section is present in your resume

---

## 📞 Support

For detailed information, see:
- **Testing Guide**: TESTING_GUIDE.md
- **Setup Guide**: SETUP_GUIDE.md (if available)
- **Backend API Docs**: Check Python/Node backend files

---

**Now you're ready to test! Go to http://localhost:8000 and get started! 🎉**
