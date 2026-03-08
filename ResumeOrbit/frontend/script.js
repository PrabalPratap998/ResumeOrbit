// ==========================================
// ResumeOrbit - Resume Parser JavaScript
// ==========================================

const API_URL = 'http://localhost:5000';
let parsedData = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupTabButtons();
    setupDragDrop();
});

// Setup Tab Buttons
function setupTabButtons() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

// Switch Tabs
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// Setup Drag and Drop
function setupDragDrop() {
    const dropArea = document.querySelector('.file-upload-area');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropArea.style.borderColor = 'var(--primary-color)';
        dropArea.style.background = 'rgba(99, 102, 241, 0.1)';
    }

    function unhighlight(e) {
        dropArea.style.borderColor = 'var(--border-color)';
        dropArea.style.background = 'var(--bg-color)';
    }

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        document.getElementById('fileInput').files = files;
        handleFileSelect({target: {files: files}});
    }
}

// Handle File Select
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const fileName = document.getElementById('fileName');
        fileName.textContent = `Selected: ${file.name}`;
    }
}

// Parse Text
async function parseText() {
    const resumeText = document.getElementById('resumeText').value.trim();
    
    if (!resumeText) {
        showError('Please enter resume text');
        return;
    }

    showLoading();
    
    try {
        const response = await fetch(`${API_URL}/parse/text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                resume_text: resumeText
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.message || 'Failed to parse resume');
            return;
        }

        parsedData = data.data;
        displayResults(parsedData);
    } catch (error) {
        showError(`Error: ${error.message}`);
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// Parse File
async function parseFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        showError('Please select a file');
        return;
    }

    showLoading();

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/parse/file`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.message || 'Failed to parse resume');
            return;
        }

        parsedData = data.data;
        displayResults(parsedData);
    } catch (error) {
        showError(`Error: ${error.message}`);
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// Display Results
function displayResults(data) {
    // Contact Info
    const contactContainer = document.getElementById('contactInfo');
    contactContainer.innerHTML = '';
    if (data.contact_info && Object.keys(data.contact_info).length > 0) {
        Object.entries(data.contact_info).forEach(([key, value]) => {
            const div = document.createElement('div');
            div.className = 'info-item';
            let displayValue = value;
            if (key.includes('linkedin') || key.includes('github') || key.includes('email')) {
                displayValue = `<a href="https://${value}" target="_blank">${value}</a>`;
            }
            div.innerHTML = `
                <div class="info-label">${formatLabel(key)}</div>
                <div class="info-value">${displayValue}</div>
            `;
            contactContainer.appendChild(div);
        });
    } else {
        contactContainer.innerHTML = '<p>No contact information found</p>';
    }

    // Summary
    const summaryElement = document.getElementById('summary');
    summaryElement.textContent = data.summary || 'No summary found';

    // Experience
    const experienceContainer = document.getElementById('experience');
    experienceContainer.innerHTML = '';
    if (data.experience && data.experience.length > 0) {
        data.experience.forEach(job => {
            const div = document.createElement('div');
            div.className = 'experience-item';
            let descriptions = '';
            if (job.description && job.description.length > 0) {
                descriptions = `<ul class="job-description">
                    ${job.description.map(desc => `<li>${escapeHtml(desc)}</li>`).join('')}
                </ul>`;
            }
            div.innerHTML = `
                <div class="job-title">${escapeHtml(job.title || '')}</div>
                ${job.company ? `<div class="company-name">${escapeHtml(job.company)}</div>` : ''}
                ${job.duration ? `<div class="job-duration">${escapeHtml(job.duration)}</div>` : ''}
                ${descriptions}
            `;
            experienceContainer.appendChild(div);
        });
    } else {
        experienceContainer.innerHTML = '<p>No experience found</p>';
    }

    // Education
    const educationContainer = document.getElementById('education');
    educationContainer.innerHTML = '';
    if (data.education && data.education.length > 0) {
        data.education.forEach(edu => {
            const div = document.createElement('div');
            div.className = 'education-item';
            div.innerHTML = `
                <div class="degree">${escapeHtml(edu.degree || '')}</div>
                ${edu.institution ? `<div class="institution">${escapeHtml(edu.institution)}</div>` : ''}
                ${edu.year ? `<div style="color: var(--text-secondary); font-size: 0.9rem;">${escapeHtml(edu.year)}</div>` : ''}
                ${edu.gpa ? `<div style="color: var(--text-secondary); font-size: 0.9rem;">GPA: ${escapeHtml(edu.gpa)}</div>` : ''}
            `;
            educationContainer.appendChild(div);
        });
    } else {
        educationContainer.innerHTML = '<p>No education found</p>';
    }

    // Skills
    const skillsContainer = document.getElementById('skills');
    skillsContainer.innerHTML = '';
    if (data.skills && data.skills.length > 0) {
        data.skills.forEach(skill => {
            const span = document.createElement('span');
            span.className = 'skill-badge';
            span.textContent = escapeHtml(skill);
            skillsContainer.appendChild(span);
        });
    } else {
        skillsContainer.innerHTML = '<p>No skills found</p>';
    }

    // Certifications
    const certificationsContainer = document.getElementById('certifications');
    certificationsContainer.innerHTML = '';
    if (data.certifications && data.certifications.length > 0) {
        data.certifications.forEach(cert => {
            const div = document.createElement('div');
            div.className = 'cert-name';
            div.style.marginBottom = '0.5rem';
            div.textContent = escapeHtml(cert);
            certificationsContainer.appendChild(div);
        });
    } else {
        certificationsContainer.innerHTML = '<p>No certifications found</p>';
    }

    // Projects
    const projectsContainer = document.getElementById('projects');
    projectsContainer.innerHTML = '';
    if (data.projects && data.projects.length > 0) {
        data.projects.forEach(project => {
            const div = document.createElement('div');
            div.className = 'project-item';
            let descriptions = '';
            if (project.description && project.description.length > 0) {
                descriptions = `<ul class="job-description">
                    ${project.description.map(desc => `<li>${escapeHtml(desc)}</li>`).join('')}
                </ul>`;
            }
            div.innerHTML = `
                <div class="project-name">${escapeHtml(project.name || '')}</div>
                ${descriptions}
            `;
            projectsContainer.appendChild(div);
        });
    } else {
        projectsContainer.innerHTML = '<p>No projects found</p>';
    }

    // Languages
    const languagesContainer = document.getElementById('languages');
    languagesContainer.innerHTML = '';
    if (data.languages && data.languages.length > 0) {
        data.languages.forEach(lang => {
            const div = document.createElement('div');
            div.className = 'language-item';
            div.textContent = escapeHtml(lang);
            languagesContainer.appendChild(div);
        });
    } else {
        languagesContainer.innerHTML = '<p>No languages found</p>';
    }

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    window.scrollTo({ top: document.getElementById('resultsSection').offsetTop - 100, behavior: 'smooth' });
}

// Helper Functions
function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function formatLabel(text) {
    return text
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function downloadJSON() {
    if (!parsedData) {
        showError('No data to download');
        return;
    }

    const dataStr = JSON.stringify(parsedData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `parsed-resume-${new Date().getTime()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function resetForm() {
    document.getElementById('resumeText').value = '';
    document.getElementById('fileInput').value = '';
    document.getElementById('fileName').textContent = '';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    parsedData = null;
}
