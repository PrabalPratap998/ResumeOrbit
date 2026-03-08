/**
 * User Routes
 * Handles user profile and account management
 */

const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jwt-simple');
const { getQuery, runQuery } = require('../db/database');

const SECRET = process.env.JWT_SECRET || 'resumeorbit-secret-key-change-in-production';

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

// Get user profile
router.get('/profile', verifyToken, async (req, res) => {
  try {
    const userId = req.user.id;

    const user = await getQuery(
      'SELECT id, email, name, created_at FROM users WHERE id = ?',
      [userId]
    );

    if (!user) {
      return res.status(404).json({
        error: 'User not found'
      });
    }

    res.json({
      success: true,
      user: user
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      error: 'Failed to retrieve profile',
      message: error.message
    });
  }
});

// Update user profile
router.put('/profile', verifyToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const { name, email } = req.body;

    if (!name && !email) {
      return res.status(400).json({
        error: 'No fields to update'
      });
    }

    let updateQuery = 'UPDATE users SET updated_at = CURRENT_TIMESTAMP';
    let params = [];

    if (name) {
      updateQuery += ', name = ?';
      params.push(name);
    }

    if (email) {
      // Check if email already exists
      const existing = await getQuery(
        'SELECT id FROM users WHERE email = ? AND id != ?',
        [email, userId]
      );

      if (existing) {
        return res.status(409).json({
          error: 'Email already in use'
        });
      }

      updateQuery += ', email = ?';
      params.push(email);
    }

    updateQuery += ' WHERE id = ?';
    params.push(userId);

    await runQuery(updateQuery, params);

    res.json({
      success: true,
      message: 'Profile updated successfully'
    });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({
      error: 'Failed to update profile',
      message: error.message
    });
  }
});

// Change password
router.post('/change-password', verifyToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const { current_password, new_password } = req.body;

    if (!current_password || !new_password) {
      return res.status(400).json({
        error: 'Missing required fields'
      });
    }

    // Get user
    const user = await getQuery(
      'SELECT password FROM users WHERE id = ?',
      [userId]
    );

    if (!user) {
      return res.status(404).json({
        error: 'User not found'
      });
    }

    // Verify current password
    const isValid = await bcrypt.compare(current_password, user.password);

    if (!isValid) {
      return res.status(401).json({
        error: 'Invalid current password'
      });
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(new_password, 10);

    // Update password
    await runQuery(
      'UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
      [hashedPassword, userId]
    );

    res.json({
      success: true,
      message: 'Password changed successfully'
    });
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({
      error: 'Failed to change password',
      message: error.message
    });
  }
});

// Delete account
router.delete('/account', verifyToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const { password } = req.body;

    if (!password) {
      return res.status(400).json({
        error: 'Password required for account deletion'
      });
    }

    // Get user
    const user = await getQuery(
      'SELECT password FROM users WHERE id = ?',
      [userId]
    );

    if (!user) {
      return res.status(404).json({
        error: 'User not found'
      });
    }

    // Verify password
    const isValid = await bcrypt.compare(password, user.password);

    if (!isValid) {
      return res.status(401).json({
        error: 'Invalid password'
      });
    }

    // Delete user (cascades to related data)
    await runQuery('DELETE FROM users WHERE id = ?', [userId]);

    res.json({
      success: true,
      message: 'Account deleted successfully'
    });
  } catch (error) {
    console.error('Delete account error:', error);
    res.status(500).json({
      error: 'Failed to delete account',
      message: error.message
    });
  }
});

module.exports = router;
