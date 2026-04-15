/**
 * Jobs Routes
 * Handles job scraping, matching, and application
 */

const express = require('express');
const router = express.Router();
const axios = require('axios');
const jwt = require('jwt-simple');
const { runQuery, getQuery, allQuery } = require('../db/database');

const SECRET = process.env.JWT_SECRET || 'resumeorbit-secret-key-change-in-production';
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:5000';
const DEFAULT_MATCH_STRICTNESS = (process.env.MATCH_STRICTNESS || 'medium').toLowerCase();

function getMinScoreForStrictness(strictness = DEFAULT_MATCH_STRICTNESS) {
  const level = String(strictness || '').toLowerCase();
  if (level === 'low') {
    return 10;
  }
  if (level === 'high') {
    return 30;
  }
  return 18;
}

function toSafeArray(value) {
  return Array.isArray(value) ? value : [];
}

function tokenize(text) {
  if (!text || typeof text !== 'string') {
    return [];
  }

  return text
    .toLowerCase()
    .replace(/[^a-z0-9+#\s]/g, ' ')
    .split(/\s+/)
    .filter((token) => token.length >= 3);
}

function buildResumeSignals(parsedData = {}) {
  const skills = toSafeArray(parsedData.skills)
    .map((s) => String(s || '').trim())
    .filter(Boolean);

  const experienceTitles = toSafeArray(parsedData.experience)
    .map((exp) => String(exp?.title || ''))
    .filter(Boolean);

  const projectNames = toSafeArray(parsedData.projects)
    .map((project) => String(project?.name || ''))
    .filter(Boolean);

  const summary = String(parsedData.summary || '');
  const degreeLines = toSafeArray(parsedData.education)
    .map((edu) => String(edu?.degree || ''))
    .filter(Boolean);

  const textPool = [
    ...skills,
    ...experienceTitles,
    ...projectNames,
    ...degreeLines,
    summary
  ];

  const tokenSet = new Set();
  textPool.forEach((item) => tokenize(item).forEach((t) => tokenSet.add(t)));

  return {
    skills,
    tokenSet,
    hasSignals: skills.length > 0 || tokenSet.size > 0
  };
}

function scoreJobAgainstResume(job, resumeSignals) {
  const jobTitle = String(job.title || '');
  const jobDescription = String(job.description || '');
  const jobRequirements = String(job.requirements || '');

  const jobText = `${jobTitle} ${jobDescription} ${jobRequirements}`.toLowerCase();
  const jobTokens = new Set(tokenize(jobText));

  const matchedSkills = resumeSignals.skills.filter((skill) => {
    const normalized = skill.toLowerCase();
    return normalized.length >= 2 && jobText.includes(normalized);
  });

  let keywordHits = 0;
  resumeSignals.tokenSet.forEach((token) => {
    if (jobTokens.has(token)) {
      keywordHits += 1;
    }
  });

  // Skills have the highest weight; token overlap adds secondary relevance.
  const skillScore = matchedSkills.length * 22;
  const keywordScore = keywordHits * 5;
  const titleBoost = matchedSkills.some((s) => jobTitle.toLowerCase().includes(s.toLowerCase())) ? 8 : 0;
  const rawScore = skillScore + keywordScore + titleBoost;
  const matchScore = Math.min(rawScore, 100);

  return {
    matchedSkills,
    keywordHits,
    matchScore
  };
}

// Middleware to verify token
function verifyToken(req, res, next) {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = jwt.decode(token, SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}

// Scrape jobs from web
router.post('/scrape', verifyToken, async (req, res) => {
  try {
    const { keywords, location, pages = 1 } = req.body;

    console.log(`\n🔍 Job scraping request: keywords="${keywords}", location="${location}"`);

    if (!keywords) {
      return res.status(400).json({
        error: 'Missing keywords',
        message: 'Please provide job search keywords'
      });
    }

    // Call Python API to scrape jobs
    console.log(`📞 Calling Python API: ${PYTHON_API_URL}/scrape/jobs`);
    const scrapeResponse = await axios.post(`${PYTHON_API_URL}/scrape/jobs`, {
      keywords: keywords,
      location: location || '',
      pages: pages
    });

    if (!scrapeResponse.data.success) {
      console.log(`❌ Python API returned error: ${scrapeResponse.data.message}`);
      return res.status(400).json({
        error: 'Scraping failed',
        message: scrapeResponse.data.message
      });
    }

    const jobs = scrapeResponse.data.jobs;
    console.log(`📝 Python API returned ${jobs.length} jobs`);

    // Clear old jobs before saving new ones
    try {
      await runQuery('DELETE FROM jobs WHERE 1=1');
      console.log(`🗑️ Cleared old jobs from database`);
    } catch (clearError) {
      console.warn('Failed to clear old jobs:', clearError);
    }

    // Save jobs to database
    let savedCount = 0;
    for (const job of jobs) {
      try {
        const result = await runQuery(
          `INSERT INTO jobs 
           (job_id, title, company, location, description, requirements, salary_range, job_url, source) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            job.id || `${job.company}-${job.title}-${Date.now()}`,
            job.title,
            job.company,
            job.location || '',
            job.description || '',
            job.requirements || '',
            job.salary_range || job.salary || '',
            job.url,
            job.source || 'web'
          ]
        );
        savedCount++;
        console.log(`✅ Saved job: ${job.title} at ${job.company} (ID: ${result.id})`);
      } catch (dbError) {
        console.error(`❌ Error saving job "${job.title}":`, dbError.message);
      }
    }

    // Verify jobs were saved
    const savedJobs = await allQuery('SELECT COUNT(*) as count FROM jobs');
    console.log(`📊 Total jobs now in database: ${savedJobs[0].count}`);

    res.json({
      success: true,
      message: `Scraped ${savedCount} jobs`,
      jobs_count: savedCount,
      jobs: jobs
    });
  } catch (error) {
    console.error('Job scraping error:', error);

    const pythonMessage =
      error?.response?.data?.message ||
      error?.response?.data?.error ||
      null;

    const isConnRefused = error?.code === 'ECONNREFUSED' || /ECONNREFUSED/i.test(String(error?.message || ''));
    const isTimeout = error?.code === 'ETIMEDOUT' || /timeout/i.test(String(error?.message || ''));

    const message = isConnRefused
      ? `Python backend is not reachable at ${PYTHON_API_URL}. Start the Python service on port 5000 (or set PYTHON_API_URL correctly).`
      : isTimeout
        ? `Python backend timed out at ${PYTHON_API_URL}. It may be down or taking too long to respond.`
        : (pythonMessage || error.message);

    res.status(isConnRefused ? 502 : 500).json({
      error: 'Scraping failed',
      message
    });
  }
});

// Match jobs with resume
router.post('/match', verifyToken, async (req, res) => {
  try {
    const { resume_id, strictness } = req.body;
    const userId = req.user.id;
    const minMatchScore = getMinScoreForStrictness(strictness);

    console.log(`\n📋 Matching jobs for resume ${resume_id} (user: ${userId})`);

    if (!resume_id) {
      return res.status(400).json({
        error: 'Missing resume_id',
        message: 'Please provide a resume ID'
      });
    }

    // Get resume
    const resume = await getQuery(
      `SELECT parsed_data FROM resumes WHERE id = ? AND user_id = ?`,
      [resume_id, userId]
    );

    if (!resume) {
      console.log(`❌ Resume ${resume_id} not found for user ${userId}`);
      return res.status(404).json({
        error: 'Resume not found',
        message: 'Resume does not exist'
      });
    }

    const parsedData = JSON.parse(resume.parsed_data || '{}');
    const resumeSignals = buildResumeSignals(parsedData);
    console.log(`📊 Resume signals: skills=${resumeSignals.skills.length}, tokens=${resumeSignals.tokenSet.size}, strictness=${strictness || DEFAULT_MATCH_STRICTNESS}, min_score=${minMatchScore}`);

    // Get all jobs
    const jobs = await allQuery('SELECT * FROM jobs LIMIT 100');
    console.log(`📝 Found ${jobs.length} jobs in database`);

    if (jobs.length === 0) {
      console.log(`⚠️ No jobs in database`);
      return res.json({
        success: true,
        message: 'No jobs found',
        matches: []
      });
    }

    // Calculate match scores
    const matches = [];
    for (const job of jobs) {
      const { matchedSkills, keywordHits, matchScore } = scoreJobAgainstResume(job, resumeSignals);

      // When resume signals exist, enforce a relevance floor to reduce generic role-only results.
      if (resumeSignals.hasSignals && (matchScore < minMatchScore || keywordHits === 0)) {
        continue;
      }

      matches.push({
        job_id: job.id,
        job_title: job.title,
        company: job.company,
        location: job.location,
        job_url: job.job_url,
        match_score: matchScore,
        matched_skills: matchedSkills,
        description: job.description?.substring(0, 200) + '...',
        source: job.source
      });

      // Save match to database
      try {
        await runQuery(
          `INSERT OR IGNORE INTO job_matches 
           (resume_id, job_id, match_score, matched_skills) 
           VALUES (?, ?, ?, ?)`,
          [resume_id, job.id, matchScore, JSON.stringify(matchedSkills)]
        );
      } catch (dbError) {
        console.error(`Error saving match for job ${job.id}:`, dbError);
      }
    }

    // If filtering removed everything, return top jobs with score 0 instead of failing silently.
    if (matches.length === 0) {
      const fallbackJobs = jobs.slice(0, 10).map((job) => ({
        job_id: job.id,
        job_title: job.title,
        company: job.company,
        location: job.location,
        job_url: job.job_url,
        match_score: 0,
        matched_skills: [],
        description: job.description?.substring(0, 200) + '...',
        source: job.source
      }));

      return res.json({
        success: true,
        message: 'No strong resume-based matches found. Showing latest jobs instead.',
        total_jobs: jobs.length,
        matches: fallbackJobs
      });
    }

    // Sort by match score descending
    matches.sort((a, b) => b.match_score - a.match_score);

    console.log(`✅ Returning ${matches.length} matched jobs`);
    res.json({
      success: true,
      message: `Found ${matches.length} jobs`,
      total_jobs: jobs.length,
      matches: matches
    });
  } catch (error) {
    console.error('Job matching error:', error);
    res.status(500).json({
      error: 'Matching failed',
      message: error.message
    });
  }
});

// Get matched jobs for resume
router.get('/matched/:resume_id', verifyToken, async (req, res) => {
  try {
    const { resume_id } = req.params;
    const userId = req.user.id;

    // Verify resume ownership
    const resume = await getQuery(
      `SELECT id FROM resumes WHERE id = ? AND user_id = ?`,
      [resume_id, userId]
    );

    if (!resume) {
      return res.status(404).json({
        error: 'Resume not found'
      });
    }

    // Get matched jobs
    const matches = await allQuery(
      `SELECT jm.*, j.title, j.company, j.location, j.job_url, j.description
       FROM job_matches jm
       JOIN jobs j ON jm.job_id = j.id
       WHERE jm.resume_id = ?
       ORDER BY jm.match_score DESC`,
      [resume_id]
    );

    // Parse matched_skills JSON
    const parsedMatches = matches.map(m => ({
      ...m,
      matched_skills: JSON.parse(m.matched_skills || '[]')
    }));

    res.json({
      success: true,
      matches: parsedMatches,
      total: parsedMatches.length
    });
  } catch (error) {
    console.error('Get matched jobs error:', error);
    res.status(500).json({
      error: 'Failed to retrieve matched jobs',
      message: error.message
    });
  }
});

// Apply to job
router.post('/apply/:job_id', verifyToken, async (req, res) => {
  try {
    const { job_id } = req.params;
    const { resume_id } = req.body;
    const userId = req.user.id;

    if (!resume_id) {
      return res.status(400).json({
        error: 'Missing resume_id',
        message: 'Please provide a resume ID'
      });
    }

    // Verify job exists
    const job = await getQuery(
      'SELECT * FROM jobs WHERE id = ?',
      [job_id]
    );

    if (!job) {
      return res.status(404).json({
        error: 'Job not found'
      });
    }

    // Check if already applied
    const existingApplication = await getQuery(
      'SELECT id FROM applied_jobs WHERE user_id = ? AND job_id = ?',
      [userId, job_id]
    );

    if (existingApplication) {
      return res.status(409).json({
        error: 'Already applied',
        message: 'You have already applied to this job'
      });
    }

    // Record application
    const result = await runQuery(
      `INSERT INTO applied_jobs (user_id, job_id, resume_id, status, application_method)
       VALUES (?, ?, ?, ?, ?)`,
      [userId, job_id, resume_id, 'applied', 'auto']
    );

    res.status(201).json({
      success: true,
      message: 'Application submitted successfully',
      application_id: result.id,
      job: {
        title: job.title,
        company: job.company,
        url: job.job_url
      }
    });
  } catch (error) {
    console.error('Application error:', error);
    res.status(500).json({
      error: 'Application failed',
      message: error.message
    });
  }
});

// Get applied jobs
router.get('/applied', verifyToken, async (req, res) => {
  try {
    const userId = req.user.id;

    const appliedJobs = await allQuery(
      `SELECT aj.*, j.title, j.company, j.job_url, j.location
       FROM applied_jobs aj
       JOIN jobs j ON aj.job_id = j.id
       WHERE aj.user_id = ?
       ORDER BY aj.applied_at DESC`,
      [userId]
    );

    res.json({
      success: true,
      total: appliedJobs.length,
      jobs: appliedJobs
    });
  } catch (error) {
    console.error('Get applied jobs error:', error);
    res.status(500).json({
      error: 'Failed to retrieve applied jobs',
      message: error.message
    });
  }
});

module.exports = router;
