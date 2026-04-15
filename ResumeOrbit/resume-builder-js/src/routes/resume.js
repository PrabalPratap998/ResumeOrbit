/**
 * Resume Routes
 * Handles resume upload, parsing, and retrieval
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

// Upload and parse resume
router.post('/upload', verifyToken, async (req, res) => {
  try {
    const { resume_text, resume_name, parsed_data } = req.body;
    const userId = req.user.id;

    if (!resume_text || !resume_name) {
      return res.status(400).json({
        error: 'Missing required fields',
        message: 'Please provide resume_text and resume_name'
      });
    }

    let finalParsedData = parsed_data;

    // If parsed_data is not provided, call Python API to parse resume
    if (!parsed_data) {
      const parseResponse = await axios.post(`${PYTHON_API_URL}/parse/text`, {
        resume_text: resume_text
      });

      if (!parseResponse.data.success) {
        return res.status(400).json({
          error: 'Parsing failed',
          message: parseResponse.data.message
        });
      }

      finalParsedData = parseResponse.data.data;
    }

    // Save to database
    const result = await runQuery(
      `INSERT INTO resumes (user_id, name, raw_text, parsed_data) 
       VALUES (?, ?, ?, ?)`,
      [userId, resume_name, resume_text, JSON.stringify(finalParsedData)]
    );

    res.status(201).json({
      success: true,
      message: 'Resume uploaded and parsed successfully',
      resume: {
        id: result.id,
        name: resume_name,
        parsed_data: finalParsedData
      }
    });
  } catch (error) {
    console.error('Resume upload error:', error);
    res.status(500).json({
      error: 'Upload failed',
      message: error.message
    });
  }
});

// Get user's resumes
router.get('/list', verifyToken, async (req, res) => {
  try {
    const userId = req.user.id;

    const resumes = await allQuery(
      `SELECT id, name, created_at, updated_at FROM resumes 
       WHERE user_id = ? ORDER BY created_at DESC`,
      [userId]
    );

    res.json({
      success: true,
      resumes: resumes || []
    });
  } catch (error) {
    console.error('List resumes error:', error);
    res.status(500).json({
      error: 'Failed to retrieve resumes',
      message: error.message
    });
  }
});

// Get specific resume
router.get('/:id', verifyToken, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const resume = await getQuery(
      `SELECT * FROM resumes WHERE id = ? AND user_id = ?`,
      [id, userId]
    );

    if (!resume) {
      return res.status(404).json({
        error: 'Resume not found',
        message: 'This resume does not exist or you do not have access'
      });
    }

    // Parse JSON data
    resume.parsed_data = JSON.parse(resume.parsed_data || '{}');

    res.json({
      success: true,
      resume: resume
    });
  } catch (error) {
    console.error('Get resume error:', error);
    res.status(500).json({
      error: 'Failed to retrieve resume',
      message: error.message
    });
  }
});

// Delete resume
router.delete('/:id', verifyToken, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    // Check ownership
    const resume = await getQuery(
      `SELECT id FROM resumes WHERE id = ? AND user_id = ?`,
      [id, userId]
    );

    if (!resume) {
      return res.status(404).json({
        error: 'Resume not found',
        message: 'This resume does not exist or you do not have access'
      });
    }

    await runQuery('DELETE FROM resumes WHERE id = ?', [id]);

    res.json({
      success: true,
      message: 'Resume deleted successfully'
    });
  } catch (error) {
    console.error('Delete resume error:', error);
    res.status(500).json({
      error: 'Failed to delete resume',
      message: error.message
    });
  }
});

module.exports = router;
