#!/bin/bash

echo "========================================"
echo " Starting ResumeOrbit Services"
echo "========================================"
echo

echo "Starting all ResumeOrbit services..."
echo

# Start Python Backend
echo "Starting Python Backend (Port 5000)..."
cd backend
source venv/bin/activate
python app.py &
PYTHON_PID=$!
cd ..

sleep 3

# Start Node.js Backend
echo "Starting Node.js Backend (Port 3001)..."
cd resume-builder-js
npm start &
NODE_PID=$!
cd ..

sleep 3

# Start Frontend
echo "Starting Frontend (Port 8000)..."
cd frontend
python -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo
echo "========================================"
echo "Services Started!"
echo "========================================"
echo
echo "- Frontend: http://localhost:8000"
echo "- Python API: http://localhost:5000"
echo "- Node.js API: http://localhost:3001"
echo
echo "Press Ctrl+C to stop all services"
echo

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $PYTHON_PID $NODE_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait