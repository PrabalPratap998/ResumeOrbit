/**
 * Authentication Routes
 * Handles user registration, login, logout
 */

const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jwt-simple');
const { runQuery, getQuery } = require('../db/database');

const SECRET = process.env.JWT_SECRET || 'resumeorbit-secret-key-change-in-production';

// In-memory session storage for LinkedIn credentials (expires on server restart)
const userSessions = new Map();

// Registration
router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password || !name) {
      return res.status(400).json({
        error: 'Missing required fields',
        message: 'Please provide email, password, and name'
      });
    }

    // Check if user already exists
    const existingUser = await getQuery(
      'SELECT id FROM users WHERE email = ?',
      [email]
    );

    if (existingUser) {
      return res.status(409).json({
        error: 'User already exists',
        message: 'Email is already registered'
      });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const result = await runQuery(
      'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
      [email, hashedPassword, name]
    );

    // Generate JWT token
    const token = jwt.encode({
      id: result.id,
      email: email,
      name: name,
      iat: Math.floor(Date.now() / 1000)
    }, SECRET);

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      token: token,
      user: {
        id: result.id,
        email: email,
        name: name
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      error: 'Registration failed',
      message: error.message
    });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        error: 'Missing credentials',
        message: 'Please provide email and password'
      });
    }

    // Find user
    const user = await getQuery(
      'SELECT * FROM users WHERE email = ?',
      [email]
    );

    if (!user) {
      return res.status(401).json({
        error: 'Invalid credentials',
        message: 'Email or password is incorrect'
      });
    }

    // Compare password
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return res.status(401).json({
        error: 'Invalid credentials',
        message: 'Email or password is incorrect'
      });
    }

    // Generate token
    const token = jwt.encode({
      id: user.id,
      email: user.email,
      name: user.name,
      iat: Math.floor(Date.now() / 1000)
    }, SECRET);

    res.json({
      success: true,
      message: 'Login successful',
      token: token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      error: 'Login failed',
      message: error.message
    });
  }
});

// Verify Token
router.post('/verify', (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({
        error: 'No token provided',
        valid: false
      });
    }

    const decoded = jwt.decode(token, SECRET);

    res.json({
      valid: true,
      user: {
        id: decoded.id,
        email: decoded.email,
        name: decoded.name
      }
    });
  } catch (error) {
    res.status(401).json({
      error: 'Invalid token',
      valid: false,
      message: error.message
    });
  }
});

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

// Save LinkedIn credentials to session (in-memory)
router.post('/session/credentials', verifyToken, (req, res) => {
  try {
    const userId = req.user.id;
    const { linkedin_email, linkedin_password } = req.body;

    if (!linkedin_email || !linkedin_password) {
      return res.status(400).json({
        error: 'Missing credentials',
        message: 'Email and password are required'
      });
    }

    // Store in memory with user ID (expires on server restart)
    userSessions.set(userId, {
      linkedin_email,
      linkedin_password,
      timestamp: Date.now()
    });

    res.json({ success: true, message: 'LinkedIn credentials stored in session' });
  } catch (error) {
    res.status(500).json({ error: 'Session storage failed', message: error.message });
  }
});

// Check if LinkedIn credentials are stored in session
router.get('/session/credentials', verifyToken, (req, res) => {
  try {
    const userId = req.user.id;
    const session = userSessions.get(userId);

    if (!session) {
      return res.status(404).json({
        error: 'No credentials',
        has_credentials: false
      });
    }

    res.json({
      success: true,
      has_credentials: true,
      linkedin_email: session.linkedin_email
    });
  } catch (error) {
    res.status(500).json({ error: 'Session retrieval failed', message: error.message });
  }
});

// Clear stored LinkedIn credentials
router.post('/session/logout-linkedin', verifyToken, (req, res) => {
  try {
    const userId = req.user.id;
    userSessions.delete(userId);
    res.json({ success: true, message: 'LinkedIn credentials cleared' });
  } catch (error) {
    res.status(500).json({ error: 'Logout failed', message: error.message });
  }
});

module.exports = { router, userSessions };
