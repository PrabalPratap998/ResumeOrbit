const axios = require('axios');

const API_URL = 'http://localhost:3001/api';

async function runTest() {
  try {
    const email = `testuser_${Date.now()}@example.com`;
    const regRes = await axios.post(`${API_URL}/auth/register`, { name: 'Test', email, password: 'pw' });
    const token = regRes.data.token;
    
    // Upload a basic Python resume
    const resUpload = await axios.post(`${API_URL}/resume/upload`, {
      resume_text: 'Python Developer with Flask and Django experience.',
      resume_name: 'Test'
    }, { headers: { Authorization: `Bearer ${token}` } });
    const resumeId = resUpload.data.resume.id;
    
    // Scrape
    const scrapeRes = await axios.post(`${API_URL}/jobs/scrape`, { keywords: 'django', location: 'remote', pages: 1 }, { headers: { Authorization: `Bearer ${token}` } });
    console.log(`Scraped jobs:`, scrapeRes.data.jobs_count);
    
    // Match
    const matchRes = await axios.post(`${API_URL}/jobs/match`, { resume_id: resumeId }, { headers: { Authorization: `Bearer ${token}` } });
    console.log(`Matched jobs:`, matchRes.data.matches.length);
    if (matchRes.data.matches.length > 0) {
      console.log('Sample URL:', matchRes.data.matches[0].job_url);
    }
  } catch (e) {
    if (e.response) console.log(e.response.data);
    else console.log(e.message);
  }
}
runTest();
