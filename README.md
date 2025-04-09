# Network Topology Generator

This project provides a web-based tool to generate, visualize, and configure network topologies, initially focusing on stacked ring configurations.

It uses FastAPI for the backend API and Streamlit for the interactive frontend.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   └── main.py       # FastAPI application logic, NetworkX generation
│   ├── requirements.txt  # Backend Python dependencies
│   └── README.md         # Backend specific details
├── frontend/
│   ├── app.py            # Streamlit application UI and logic
│   ├── requirements.txt  # Frontend Python dependencies
│   └── README.md         # Frontend specific details
├── .venv/                # Python virtual environment (created by run_dev.sh)
├── run_dev.sh          # Script to setup environment and run both servers
└── README.md           # This file
```

## Features

*   Define the total number of nodes for the topology.
*   Add multiple "skip" connection layers (e.g., skip=1 for a basic ring, skip=2 for connections jumping two nodes).
*   Visualize the generated topology using NetworkX and Matplotlib.
*   Export the current configuration (number of nodes and skips) as a JSON file.
*   View the JSON configuration directly in the UI.
*   Reset the configuration to start over.

## Running the Application

1.  **Prerequisites:** Ensure you have Python 3 installed on your system.
2.  **Make the script executable (first time only):**
    ```bash
    chmod +x run_dev.sh
    ```
3.  **Run the development server script:**
    ```bash
    ./run_dev.sh
    ```

This script will automatically:
*   Create a Python virtual environment (`.venv`) if it doesn't exist.
*   Install all required dependencies from `backend/requirements.txt` and `frontend/requirements.txt` into the virtual environment.
*   Start the FastAPI backend server on `http://localhost:8000` (in the background).
*   Start the Streamlit frontend server on `http://localhost:8501` (in the foreground) and likely open it in your browser.

To stop both servers, simply press `Ctrl+C` in the terminal where `./run_dev.sh` is running. The script will handle shutting down the background backend server. 