/**
 * ResumeOrbit - Complete Frontend Application
 * Handles: Auth, Resume Parsing, Job Scraping, Job Matching, Auto-Apply
 */

const API_URL = '/api';
const PYTHON_API_URL = '/python-api';

let currentToken = null;
let currentUser = null;
let currentResume = null;
let currentResumeId = null;
let parsedResume = null;

function deriveJobSearchFromResume(parsedData) {
    if (!parsedData || typeof parsedData !== 'object') {
        return { keywords: '', location: '' };
    }

    const skills = Array.isArray(parsedData.skills) ? parsedData.skills : [];
    const experience = Array.isArray(parsedData.experience) ? parsedData.experience : [];

    const firstTitle = experience.find((item) => item && typeof item === 'object' && item.title)?.title;
    const resumeLocation = parsedData?.contact_info?.location;

    let keywords = '';

    if (firstTitle && String(firstTitle).trim()) {
        keywords = String(firstTitle).trim();
    } else if (skills.length) {
        keywords = skills
            .map((s) => String(s || '').trim())
            .filter(Boolean)
            .slice(0, 3)
            .join(' ');
    } else if (parsedData.summary && String(parsedData.summary).trim()) {
        keywords = String(parsedData.summary)
            .trim()
            .split(/\s+/)
            .slice(0, 6)
            .join(' ');
    }

    const location = resumeLocation && String(resumeLocation).trim() ? String(resumeLocation).trim() : '';

    return { keywords, location };
}

function populateJobSearchFromResume(parsedData, { autoSearch = true } = {}) {
    const { keywords, location } = deriveJobSearchFromResume(parsedData);

    const keywordsInput = document.getElementById('jobKeywords');
    const locationInput = document.getElementById('jobLocation');

    if (!keywordsInput) {
        return;
    }

    const hadKeywords = Boolean(keywordsInput.value && keywordsInput.value.trim());
    const hadLocation = Boolean(locationInput?.value && locationInput.value.trim());

    if (!hadKeywords && keywords) {
        keywordsInput.value = keywords;
    }

    if (locationInput && !hadLocation && location) {
        locationInput.value = location;
    }

    // Auto-run the search only if the user hasn't typed anything yet.
    if (autoSearch && !hadKeywords && keywordsInput.value.trim() && currentResumeId) {
        setTimeout(() => {
            const stillEmptyBefore = !hadKeywords;
            if (stillEmptyBefore && document.getElementById('jobKeywords')?.value.trim()) {
                searchJobs();
            }
        }, 250);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkToken();
    setupTabButtons();
});

// ========================
// TOKEN & AUTH MANAGEMENT
// ========================

function checkToken() {
    const token = localStorage.getItem('resumeorbit_token');
    if (token) {
        currentToken = token;
        verifyToken();
    }
}

async function verifyToken() {
    try {
        const response = await fetch(`${API_URL}/auth/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: currentToken })
        });

        const data = await response.json();

        if (data.valid) {
            currentUser = data.user;
            showDashboard();
        } else {
            logout();
        }
    } catch (error) {
        console.error('Token verification error:', error);
        logout();
    }
}

async function login(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showError('loginError', data.message || 'Login failed');
            return false;
        }

        // Store token and user
        localStorage.setItem('resumeorbit_token', data.token);
        currentToken = data.token;
        currentUser = data.user;

        showDashboard();
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPassword').value = '';
        return false;
    } catch (error) {
        showError('loginError', error.message);
        return false;
    }
}

async function register(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showError('registerError', data.message || 'Registration failed');
            return false;
        }

        // Store token and user
        localStorage.setItem('resumeorbit_token', data.token);
        currentToken = data.token;
        currentUser = data.user;

        showDashboard();
        document.getElementById('registerName').value = '';
        document.getElementById('registerEmail').value = '';
        document.getElementById('registerPassword').value = '';
        return false;
    } catch (error) {
        showError('registerError', error.message);
        return false;
    }
}

function logout() {
    localStorage.removeItem('resumeorbit_token');
    currentToken = null;
    currentUser = null;
    currentResume = null;
    currentResumeId = null;
    parsedResume = null;
    switchToLogin();
}

// ========================
// SCREEN MANAGEMENT
// ========================

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function showDashboard() {
    document.getElementById('navGuest').style.display = 'none';
    document.getElementById('navUser').style.display = 'flex';
    document.getElementById('userName').textContent = currentUser.name;
    showScreen('dashboardScreen');
}

function switchToLogin() {
    document.getElementById('navGuest').style.display = 'flex';
    document.getElementById('navUser').style.display = 'none';
    showScreen('loginScreen');
}

function switchToRegister() {
    showScreen('registerScreen');
}

// ========================
// RESUME PARSING
// ========================

async function parseResume() {
    const resumeText = document.getElementById('resumeText').value.trim();
    
    if (!resumeText) {
        showError('parseError', 'Please enter or paste resume text');
        return;
    }

    // Silent parsing - no loader shown

    try {
        const response = await fetch(`${API_URL}/resume/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                resume_text: resumeText,
                resume_name: 'My Resume'
            })
        });

        const data = await response.json();
        hideLoader();

        if (!response.ok) {
            showError('parseError', data.message || 'Parsing failed');
            return;
        }

        currentResumeId = data.resume.id;
        parsedResume = data.resume.parsed_data;
        
        // Show job search section directly
        document.getElementById('jobSearchSection').style.display = 'block';
        document.getElementById('jobSearchSection').scrollIntoView({ behavior: 'smooth' });

        populateJobSearchFromResume(parsedResume, { autoSearch: true });
    } catch (error) {
        hideLoader();
        showError('parseError', error.message);
    }
}

async function parseResumeFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        showError('parseError', 'Please select a file');
        return;
    }

    // Silent parsing - no loader shown

    const formData = new FormData();
    formData.append('file', file);

    try {
        // First upload to Python backend to parse
        const parseResponse = await fetch(`${PYTHON_API_URL}/parse/file`, {
            method: 'POST',
            body: formData
        });

        const parseData = await parseResponse.json();

        if (!parseData.success) {
            hideLoader();
            showError('parseError', parseData.message || 'Parsing failed');
            return;
        }

        // Now save to Node backend with both raw text and parsed data
        const resumeResponse = await fetch(`${API_URL}/resume/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                resume_text: parseData.raw_text || 'Uploaded file',
                resume_name: file.name,
                parsed_data: parseData.data
            })
        });

        const resumeData = await resumeResponse.json();
        hideLoader();

        if (!resumeResponse.ok) {
            showError('parseError', resumeData.message || 'Failed to save resume');
            return;
        }

        currentResumeId = resumeData.resume.id;
        parsedResume = parseData.data;
        
        // Show job search section directly without parsing display
        document.getElementById('jobSearchSection').style.display = 'block';
        document.getElementById('jobSearchSection').scrollIntoView({ behavior: 'smooth' });

        populateJobSearchFromResume(parsedResume, { autoSearch: true });
    } catch (error) {
        hideLoader();
        showError('parseError', error.message);
    }
}

function displayParsedResume() {
    // Skip showing parsing results - go directly to job search
    document.getElementById('jobSearchSection').style.display = 'block';
    document.getElementById('jobSearchSection').scrollIntoView({ behavior: 'smooth' });
    
    // Auto-populate and search with common job keywords
    // User can modify and search if needed
    populateJobSearchFromResume(parsedResume, { autoSearch: false });
}

// ========================
// JOB SCRAPING & MATCHING
// ========================

async function searchJobs() {
    const keywords = document.getElementById('jobKeywords').value.trim();
    const location = document.getElementById('jobLocation').value.trim();

    console.log(`🔍 Searching jobs: keywords="${keywords}", location="${location}", resumeId="${currentResumeId}"`);

    if (!keywords) {
        showError('searchError', 'Please enter job keywords');
        return;
    }

    if (!currentResumeId) {
        showError('searchError', 'Please upload a resume first before searching for jobs');
        return;
    }

    // Show loader
    showLoader('Searching for jobs...');
    document.getElementById('jobMatches').style.display = 'none';

    try {
        // Scrape jobs from Node backend (which saves them to DB)
        console.log('📞 Calling /jobs/scrape endpoint...');
        const scrapeResponse = await fetch(`${API_URL}/jobs/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                keywords: keywords,
                location: location,
                pages: 1
            })
        });

        const scrapeData = await scrapeResponse.json();
        console.log('📝 Scrape response:', scrapeData);

        if (!scrapeData.success) {
            hideLoader();
            showError('searchError', scrapeData.message || 'Job search failed');
            return;
        }

        console.log(`✅ Scraped ${scrapeData.jobs_count} jobs`);

        // Match jobs with resume
        console.log(`⚙️ Calling /jobs/match endpoint with resume_id=${currentResumeId}...`);
        const matchResponse = await fetch(`${API_URL}/jobs/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                resume_id: currentResumeId
            })
        });

        const matchData = await matchResponse.json();
        console.log('🎯 Match response:', matchData);
        hideLoader();

        if (!matchResponse.ok) {
            showError('searchError', matchData.message || 'Matching failed');
            console.error('Match endpoint error:', matchData);
            return;
        }

        console.log(`✅ Received ${matchData.matches?.length || 0} matched jobs`);
        displayJobMatches(matchData.matches);
    } catch (error) {
        hideLoader();
        console.error('Search error:', error);
        showError('searchError', error.message);
    }
}

function displayJobMatches(matches) {
    const container = document.getElementById('jobMatches');
    
    if (!matches || matches.length === 0) {
        container.innerHTML = '<div class="no-results-container"><p class="no-results">🔍 No matching jobs found</p><p class="no-results-sub">Try different keywords or location</p></div>';
        container.style.display = 'block';
        return;
    }

    // Sort matches by score descending
    const sortedMatches = [...matches].sort((a, b) => b.match_score - a.match_score);
    
    let html = `<div class="jobs-header"><h3>💼 Found ${sortedMatches.length} Matching Opportunities</h3></div>`;
    
    sortedMatches.forEach((job, index) => {
        const matchPercent = Math.round(job.match_score);
        const matchColor = matchPercent >= 80 ? '#10b981' : matchPercent >= 60 ? '#f59e0b' : '#ef4444';
        const matchLabel = matchPercent >= 80 ? 'Excellent Match' : matchPercent >= 60 ? 'Good Match' : 'Fair Match';
        const skillBadges = (job.matched_skills || [])
            .slice(0, 5)
            .map(s => `<span class="skill-badge">${s}</span>`)
            .join('');

        html += `
            <div class="job-card premium-card" style="border-left: 4px solid ${matchColor};">
                <div class="job-rank">#{index + 1}</div>
                <div class="job-header-new">
                    <div class="job-info-new">
                        <h3 class="job-title-new">${job.job_title || 'N/A'}</h3>
                        <p class="job-company-new">🏢 ${job.company || 'N/A'}</p>
                        ${job.location ? `<p class="job-location-new">📍 ${job.location}</p>` : ''}
                    </div>
                    <div class="match-badge">
                        <div class="match-circle" style="background: linear-gradient(135deg, ${matchColor}, ${matchColor}AA);">
                            <span class="match-percent">${matchPercent}%</span>
                            <span class="match-label">${matchLabel}</span>
                        </div>
                    </div>
                </div>

                <div class="job-matched-skills">
                    <h4>✓ Matched Skills (${job.matched_skills?.length || 0})</h4>
                    <div class="skills-container">${skillBadges}</div>
                </div>

                <p class="job-description-new">${job.description?.substring(0, 200)}...</p>

                <div class="job-actions-new">
                    <a href="${job.job_url}" target="_blank" class="btn btn-outline">View Full Listing</a>
                    <button class="btn btn-apply" onclick="applyToJob(${job.job_id}, ${currentResumeId})">Apply Now</button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
    container.style.display = 'block';
}

async function applyToJob(jobId, resumeId) {
    showLoader('Applying to job...');

    try {
        const response = await fetch(`${API_URL}/jobs/apply/${jobId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                resume_id: resumeId
            })
        });

        const data = await response.json();
        hideLoader();

        if (response.ok) {
            alert(`✅ Application submitted to ${data.job.company}!`);
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        hideLoader();
        alert(`Application error: ${error.message}`);
    }
}

// ========================
// UI HELPERS
// ========================

function setupTabButtons() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = `Selected: ${file.name}`;
    }
}

function showLoader(message = 'Processing...') {
    document.getElementById('globalLoader').style.display = 'flex';
    document.querySelector('#globalLoader p').textContent = message;
}

function hideLoader() {
    document.getElementById('globalLoader').style.display = 'none';
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
    }
}
