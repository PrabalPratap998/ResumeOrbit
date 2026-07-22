const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 8000;

app.use((req, res, next) => {
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  next();
});

// Parse JSON
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname)));

// Proxy requests to Node backend
app.all(/^\/api\/.*/, async (req, res) => {
  try {
    const backendUrl = `http://localhost:3001${req.originalUrl}`;
    const config = {
      method: req.method,
      url: backendUrl,
      headers: {
        ...req.headers,
        host: 'localhost:3001'
      }
    };

    if (req.body && Object.keys(req.body).length > 0) {
      config.data = req.body;
    }

    const response = await axios(config);
    res.status(response.status).send(response.data);
  } catch (error) {
    if (error.response) {
      res.status(error.response.status).send(error.response.data);
    } else {
      res.status(500).json({ error: 'Backend connection failed' });
    }
  }
});

// Proxy requests to Python backend
app.all(/^\/python-api\/.*/, async (req, res) => {
  try {
    const pythonPath = req.originalUrl.replace(/^\/python-api/, '') || '/';
    const backendUrl = `http://localhost:5000${pythonPath}`;
    const config = {
      method: req.method,
      url: backendUrl,
      headers: {
        ...req.headers,
        host: 'localhost:5000'
      }
    };

    if (req.body && Object.keys(req.body).length > 0) {
      config.data = req.body;
    }

    const response = await axios(config);
    res.status(response.status).send(response.data);
  } catch (error) {
    if (error.response) {
      res.status(error.response.status).send(error.response.data);
    } else {
      res.status(500).json({ error: 'Python backend connection failed' });
    }
  }
});

// Serve index.html for SPA
app.get(/.*/, (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Frontend development server running on http://localhost:${PORT}`);
  console.log(`📡 Proxying /api to http://localhost:3001`);
  console.log(`📡 Proxying /python-api to http://localhost:5000`);
});
