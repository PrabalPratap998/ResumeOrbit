@echo off
echo ========================================
echo  ResumeOrbit Setup Script
echo ========================================
echo.

echo Setting up ResumeOrbit - AI-Powered Resume Parser & Job Matcher
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo Python and Node.js are installed. Proceeding with setup...
echo.

REM Setup Python Backend
echo ========================================
echo Setting up Python Backend...
echo ========================================

cd backend

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)

REM Download spaCy model
echo Downloading spaCy language model...
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo WARNING: Failed to download spaCy model. You may need to run this manually later.
)

cd ..

echo Python backend setup complete!
echo.

REM Setup Node.js Backend
echo ========================================
echo Setting up Node.js Backend...
echo ========================================

cd resume-builder-js

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node.js dependencies
    cd ..
    pause
    exit /b 1
)

cd ..

echo Node.js backend setup complete!
echo.

REM Create data directory for database
echo ========================================
echo Setting up Database...
echo ========================================

if not exist resume-builder-js\data (
    mkdir resume-builder-js\data
    echo Created data directory for database.
)

echo Database setup complete!
echo.

REM Setup complete
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo 1. Run: start_services.bat
echo 2. Open: http://localhost:8000
echo.
echo Or run services manually:
echo - Python Backend: cd backend && venv\Scripts\activate && python app.py
echo - Node.js Backend: cd resume-builder-js && npm start
echo - Frontend: cd frontend && python -m http.server 8000
echo.
echo Test files are available in the root directory.
echo.

pause