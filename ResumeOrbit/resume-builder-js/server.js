/**
 * ResumeOrbit - Node.js Express Backend
 * Handles: User Authentication, Resume Management, Job Scraping Orchestration
 */

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));
app.use(express.static('public'));

// Import routes
const authRoutes = require('./src/routes/auth');
const resumeRoutes = require('./src/routes/resume');
const jobRoutes = require('./src/routes/jobs');
const userRoutes = require('./src/routes/user');

// Initialize database
const { initializeDatabase } = require('./src/db/database');
initializeDatabase();

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/resume', resumeRoutes);
app.use('/api/jobs', jobRoutes);
app.use('/api/user', userRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'online', message: 'ResumeOrbit API Server' });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'ResumeOrbit Backend',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      resume: '/api/resume',
      jobs: '/api/jobs',
      user: '/api/user'
    }
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`\n🚀 ResumeOrbit Backend Server running on http://localhost:${PORT}`);
  console.log(`📍 API Documentation: http://localhost:${PORT}`);
  console.log(`🔗 Frontend: http://localhost:8000\n`);
});

module.exports = app;
