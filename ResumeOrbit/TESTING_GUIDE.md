# ResumeOrbit - Sample Resumes for Testing

This folder contains sample resumes you can use to test the ResumeOrbit application.

## Sample Resume Files

### 1. **sample_resume.txt** - John Anderson (Full Stack Developer)
- **Role**: Senior Full Stack Developer
- **Experience**: 6+ years
- **Top Skills**: Python, JavaScript, React, Node.js, Flask, AWS, Docker, Kubernetes

**Test Job Keywords**: 
- "Python Developer"
- "Full Stack Engineer"
- "Senior Software Engineer"
- "Backend Developer"

---

### 2. **sample_resume_2.txt** - Sarah Martinez (Product Manager & UX Designer)
- **Role**: Senior Product Manager & UX Designer
- **Experience**: 5+ years in Product Management
- **Top Skills**: Product Strategy, User Research, Figma, Agile, Analytics, Leadership

**Test Job Keywords**:
- "Product Manager"
- "UX Designer"
- "Product Designer"
- "User Experience Manager"
- "Product Strategy"

---

### 3. **sample_resume_3.txt** - Alex Chen (Data Scientist & ML Engineer)
- **Role**: Senior Data Scientist & ML Engineer
- **Experience**: 7+ years
- **Top Skills**: Python, Machine Learning, TensorFlow, PyTorch, SQL, Spark, AWS, Data Analysis

**Test Job Keywords**:
- "Data Scientist"
- "Machine Learning Engineer"
- "ML Engineer"
- "Data Engineer"
- "AI Engineer"

---

## How to Test

### **Method 1: Paste Text (Copy Paste)**

1. Go to http://localhost:8000
2. Login or Register with your credentials
3. In **Upload Your Resume** section:
   - Click on **"Paste Text"** tab
   - Open one of the sample resume files (sample_resume.txt, etc.)
   - Copy all the content
   - Paste it into the textarea
   - Click **"Parse Resume"**
4. The app will silently parse the resume
5. Enter job keywords (e.g., "Python Developer", "Full Stack Engineer")
6. Select location (e.g., "Remote", "California", "New York")
7. Click **"Search Jobs"**
8. View matching job recommendations with match scores

### **Method 2: File Upload**

1. Go to http://localhost:8000
2. Login/Register
3. In **Upload Your Resume** section:
   - Click on **"Upload File"** tab
   - Click the file upload area or drag one of the sample resume files
   - The file will be processed automatically
4. Job recommendations section will appear
5. Enter job keywords and location
6. Click **"Search Jobs"**

---

## Expected Behavior

✅ **What You Should See:**

1. **Silent Resume Parsing**: No loading message, resume is processed in background
2. **Job Recommendations**: Section appears with input fields for keywords and location
3. **Automatic Job Matching**: 
   - Jobs are scraped from Indeed, LinkedIn, Glassdoor
   - Each job shows a match score (percentage)
   - Match quality indicator (Excellent/Good/Fair)
   - #1, #2, #3 ranking badges
   - Matched skills displayed in badges
4. **Job Cards Display**:
   - Job title and company
   - Location information
   - Match score with color coding
   - "View Full Listing" button
   - "Apply Now" button

---

## Test Scenarios

### **Scenario 1: Full Stack Developer Job Search**
- Use: **sample_resume.txt** (John Anderson)
- Search Keywords: "Python Developer", "Full Stack Engineer"
- Location: "Remote" or "California"
- **Expected**: High match score with backend, frontend, and DevOps jobs

### **Scenario 2: Product Management Job Search**
- Use: **sample_resume_2.txt** (Sarah Martinez)
- Search Keywords: "Product Manager", "UX Designer"
- Location: "New York" or "San Francisco"
- **Expected**: High match with product management and design roles

### **Scenario 3: Data Science Job Search**
- Use: **sample_resume_3.txt** (Alex Chen)
- Search Keywords: "Data Scientist", "Machine Learning"
- Location: "Seattle" or "Remote"
- **Expected**: High match with ML engineer and data scientist positions

---

## Troubleshooting

### **Issue: No jobs appearing**
- ✓ Make sure to enter job keywords (don't leave blank)
- ✓ Check that all three services are running (Python, Node, Frontend)
- ✓ Refresh browser if needed
- ✓ Check browser console for errors (F12 → Console)

### **Issue: Resume not parsing**
- ✓ Ensure resume has clear sections (Contact, Skills, Experience, Education)
- ✓ Check that Python backend is running on port 5000
- ✓ Verify spaCy model is installed

### **Issue: Jobs not showing match scores**
- ✓ Ensure Node.js backend is running on port 3001
- ✓ Verify database is created correctly (should be in resume-builder-js/data/)

---

## API Testing (Advanced)

You can also test the APIs directly:

### **Test Resume Parsing**
```bash
curl -X POST http://localhost:5000/parse/text \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "[paste resume text here]"}'
```

### **Test Job Scraping**
```bash
curl -X POST http://localhost:5000/scrape/jobs \
  -H "Content-Type: application/json" \
  -d '{"keywords": "Python Developer", "location": "Remote"}'
```

---

## Tips for Best Results

1. **Use Complete Resumes**: The sample resumes have all sections which helps with better parsing
2. **Realistic Job Keywords**: Use titles that exist in the job market (Python Developer, Full Stack Engineer, etc.)
3. **Clear Locations**: Use city names or "Remote" for location
4. **Check Browser Console**: Open DevTools (F12) to see any errors or API responses
5. **Test All Three Samples**: Each has different skills for different job markets

---

## Next Steps

Once you've tested with these samples:

1. Try uploading your own resume
2. Test different job keywords and locations
3. Try the auto-apply feature to see how jobs are saved
4. Check the database to see stored resumes and applications
5. Modify the UI further based on your preferences

Enjoy testing! 🚀
