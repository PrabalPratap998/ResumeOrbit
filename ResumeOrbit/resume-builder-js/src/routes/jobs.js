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

    if (!keywords) {
      return res.status(400).json({
        error: 'Missing keywords',
        message: 'Please provide job search keywords'
      });
    }

    // Call Python API to scrape jobs
    const scrapeResponse = await axios.post(`${PYTHON_API_URL}/scrape/jobs`, {
      keywords: keywords,
      location: location || '',
      pages: pages
    });

    if (!scrapeResponse.data.success) {
      return res.status(400).json({
        error: 'Scraping failed',
        message: scrapeResponse.data.message
      });
    }

    const jobs = scrapeResponse.data.jobs;

    // Save jobs to database
    for (const job of jobs) {
      await runQuery(
        `INSERT OR IGNORE INTO jobs 
         (job_id, title, company, location, description, requirements, salary_range, job_url, source) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          job.id || `${job.company}-${job.title}-${Date.now()}`,
          job.title,
          job.company,
          job.location || '',
          job.description || '',
          job.requirements || '',
          job.salary_range || '',
          job.url,
          job.source || 'web'
        ]
      );
    }

    res.json({
      success: true,
      message: `Scraped ${jobs.length} jobs`,
      jobs_count: jobs.length
    });
  } catch (error) {
    console.error('Job scraping error:', error);
    res.status(500).json({
      error: 'Scraping failed',
      message: error.message
    });
  }
});

// Match jobs with resume
router.post('/match', verifyToken, async (req, res) => {
  try {
    const { resume_id } = req.body;
    const userId = req.user.id;

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
      return res.status(404).json({
        error: 'Resume not found',
        message: 'Resume does not exist'
      });
    }

    const parsedData = JSON.parse(resume.parsed_data || '{}');
    const resumeSkills = parsedData.skills || [];

    // Get all jobs
    const jobs = await allQuery('SELECT * FROM jobs LIMIT 100');

    // Calculate match scores
    const matches = [];
    for (const job of jobs) {
      // Simple skill match scoring
      const jobText = `${job.title} ${job.description || ''} ${job.requirements || ''}`.toLowerCase();
      let matchedSkills = [];
      let score = 0;

      for (const skill of resumeSkills) {
        if (jobText.includes(skill.toLowerCase())) {
          matchedSkills.push(skill);
          score += 10;
        }
      }

      // Bonus for company/title match
      if (score > 0 || matchedSkills.length > 0) {
        const matchPercentage = Math.min((score / Math.max(resumeSkills.length, 1)) * 100, 100);
        
        matches.push({
          job_id: job.id,
          job_title: job.title,
          company: job.company,
          location: job.location,
          job_url: job.job_url,
          match_score: matchPercentage,
          matched_skills: matchedSkills,
          description: job.description?.substring(0, 200) + '...'
        });

        // Save match to database
        await runQuery(
          `INSERT OR IGNORE INTO job_matches 
           (resume_id, job_id, match_score, matched_skills) 
           VALUES (?, ?, ?, ?)`,
          [resume_id, job.id, matchPercentage, JSON.stringify(matchedSkills)]
        );
      }
    }

    // Sort by match score descending
    matches.sort((a, b) => b.match_score - a.match_score);

    res.json({
      success: true,
      message: `Found ${matches.length} matching jobs`,
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
