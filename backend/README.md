# Backend (FastAPI)

This directory contains the FastAPI backend application for the Network Topology Generator.

## Functionality

*   Provides an API endpoint (`/generate_topology`) to receive network configuration (number of nodes and a list of skip values).
*   Uses the NetworkX library to generate the corresponding graph based on the input.
*   Serializes the generated graph into JSON format (node-link data).
*   Returns the graph JSON and the original configuration back to the client.

## Key Files

*   `app/main.py`: The main FastAPI application file containing endpoint definitions, data models (Pydantic), and topology generation logic.
*   `requirements.txt`: Lists the Python dependencies required for the backend (FastAPI, Uvicorn, NetworkX, Pydantic).

## Running Standalone (for development/testing)

While the main `../run_dev.sh` script handles running both backend and frontend, you can run the backend independently:

1.  **Navigate to the project root directory.**
2.  **Set up and activate the virtual environment (if not already done):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate 
    ```
3.  **Install dependencies:**
    ```bash
    python -m pip install -r backend/requirements.txt
    ```
4.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```
5.  **Run the Uvicorn server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

The backend API will be available at `http://localhost:8000`. 