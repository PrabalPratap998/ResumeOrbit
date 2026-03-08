#!/bin/bash

echo "========================================"
echo " ResumeOrbit Setup Script"
echo "========================================"
echo

echo "Setting up ResumeOrbit - AI-Powered Resume Parser & Job Matcher"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js 16+"
    exit 1
fi

echo "Python and Node.js are installed. Proceeding with setup..."
echo

# Setup Python Backend
echo "========================================"
echo "Setting up Python Backend..."
echo "========================================"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        cd ..
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    cd ..
    exit 1
fi

# Download spaCy model
echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to download spaCy model. You may need to run this manually later."
fi

cd ..

echo "Python backend setup complete!"
echo

# Setup Node.js Backend
echo "========================================"
echo "Setting up Node.js Backend..."
echo "========================================"

cd resume-builder-js

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Node.js dependencies"
    cd ..
    exit 1
fi

cd ..

echo "Node.js backend setup complete!"
echo

# Create data directory for database
echo "========================================"
echo "Setting up Database..."
echo "========================================"

if [ ! -d "resume-builder-js/data" ]; then
    mkdir -p resume-builder-js/data
    echo "Created data directory for database."
fi

echo "Database setup complete!"
echo

# Setup complete
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "To start the application:"
echo "1. Run: ./start_services.sh"
echo "2. Open: http://localhost:8000"
echo
echo "Or run services manually:"
echo "- Python Backend: cd backend && source venv/bin/activate && python app.py"
echo "- Node.js Backend: cd resume-builder-js && npm start"
echo "- Frontend: cd frontend && python -m http.server 8000"
echo
echo "Test files are available in the root directory."
echo