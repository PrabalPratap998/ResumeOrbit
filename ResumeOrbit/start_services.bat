@echo off
echo ========================================
echo  Starting ResumeOrbit Services
echo ========================================
echo.

echo Starting all ResumeOrbit services...
echo.

REM Start Python Backend
echo Starting Python Backend (Port 5000)...
start "Python Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && python app.py"

timeout /t 3 /nobreak >nul

REM Start Node.js Backend
echo Starting Node.js Backend (Port 3001)...
start "Node.js Backend" cmd /k "cd resume-builder-js && npm start"

timeout /t 3 /nobreak >nul

REM Start Frontend
echo Starting Frontend (Port 8000)...
start "Frontend" cmd /k "cd frontend && python -m http.server 8000"

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo - Frontend: http://localhost:8000
echo - Python API: http://localhost:5000
echo - Node.js API: http://localhost:3001
echo.
echo Press any key to close this window...
echo The services will continue running in separate windows.
echo.

pause >nul