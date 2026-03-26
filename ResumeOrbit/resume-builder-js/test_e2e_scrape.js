const axios = require('axios');

const API_URL = 'http://localhost:3001/api';

async function runTest() {
  try {
    console.log('1. Registering user...');
    // Random email string
    const email = `testuser_${Date.now()}@example.com`;
    const regRes = await axios.post(`${API_URL}/auth/register`, {
      name: 'Test User',
      email: email,
      password: 'password123'
    });
    const token = regRes.data.token;
    console.log('User registered. Token:', token.substring(0, 10) + '...');

    console.log('2. Uploading a test resume...');
    const resumeText = 'Experienced Python Developer with 5 years of experience building web applications using Django and Flask. Proficient in JavaScript, React, and SQL.';
    const resUpload = await axios.post(`${API_URL}/resume/upload`, {
      resume_text: resumeText,
      resume_name: 'Test Resume'
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    const resumeId = resUpload.data.resume.id;
    console.log('Resume uploaded. ID:', resumeId);

    console.log('3. Calling /jobs/scrape endpoint...');
    const scrapeRes = await axios.post(`${API_URL}/jobs/scrape`, {
      keywords: 'python developer',
      location: 'remote',
      pages: 1
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log(`Scrape successful. Found ${scrapeRes.data.jobs_count} jobs and saved to DB.`);

    console.log('4. Calling /jobs/match endpoint...');
    const matchRes = await axios.post(`${API_URL}/jobs/match`, {
      resume_id: resumeId
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    const matches = matchRes.data.matches;
    console.log(`Match successful. Found ${matches.length} matching jobs.`);
    if (matches.length > 0) {
      console.log('First match:');
      console.log(`- Title: ${matches[0].job_title}`);
      console.log(`- Company: ${matches[0].company}`);
      console.log(`- URL: ${matches[0].job_url}`);
    } else {
      console.log('WARNING: No matches found even after saving to DB!');
    }
    
    console.log('Test completed successfully!');
  } catch (error) {
    if (error.response) {
      console.error('API Error Response:', error.response.data);
    } else {
      console.error('Request failed:', error.message);
    }
    process.exit(1);
  }
}

runTest();
