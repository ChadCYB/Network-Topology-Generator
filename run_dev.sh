#!/bin/bash

# Navigate to the script's directory (project root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"

echo "--- Setting up Python Virtual Environment --- "

# Check if python3 is available
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 command not found. Please install Python 3." >&2
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Error creating virtual environment. Exiting." >&2
        exit 1
    fi
else
    echo "Using existing virtual environment in $VENV_DIR."
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "Error activating virtual environment. Exiting." >&2
    exit 1
fi

echo "Virtual environment activated."

echo "--- Installing Dependencies (inside $VENV_DIR) ---"

# Install backend dependencies
echo "Installing backend dependencies..."
python -m pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing backend dependencies. Exiting." >&2
    # Deactivate venv before exiting? Optional, as script terminates.
    exit 1
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
python -m pip install -r frontend/requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing frontend dependencies. Exiting." >&2
    exit 1
fi

echo "--- Starting Servers (inside $VENV_DIR) ---"

# Start backend (FastAPI with Uvicorn) in the background
echo "Starting backend server (Uvicorn) in the background..."
cd backend
# Ensure uvicorn from venv is used
"$SCRIPT_DIR/$VENV_DIR/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 & 
BACKEND_PID=$!
cd ..

echo "Backend server started with PID: $BACKEND_PID"

# Add a delay to allow the backend server to initialize
echo "Waiting for backend server to start... (3 seconds)"
sleep 3

echo "To stop the backend server later, run: kill $BACKEND_PID"

# Start frontend (Streamlit)
echo "Starting frontend server (Streamlit)..."
cd frontend
# Ensure streamlit from venv is used
"$SCRIPT_DIR/$VENV_DIR/bin/streamlit" run app.py --server.port 8501
FRONTEND_EXIT_CODE=$?
cd ..

echo "--- Shutting Down ---"

# Stop the backend server when the frontend server is stopped (e.g., Ctrl+C)
echo "Stopping backend server (PID: $BACKEND_PID)..."
# Check if the process ID exists before trying to kill it
if ps -p $BACKEND_PID > /dev/null; then
   kill $BACKEND_PID
   wait $BACKEND_PID 2>/dev/null # Wait for backend process to terminate gracefully
else
   echo "Backend process (PID: $BACKEND_PID) already stopped."
fi

# Deactivate virtual environment (optional, happens on script exit anyway)
# deactivate

echo "Servers stopped."
exit $FRONTEND_EXIT_CODE 