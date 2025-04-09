# Frontend (Streamlit)

This directory contains the Streamlit frontend application for the Network Topology Generator.

## Functionality

*   Provides an interactive web interface for configuring network topologies.
*   Allows users to:
    *   Set the total number of nodes.
    *   Add/remove different "skip" connection values.
    *   Reset the configuration.
*   Sends the configuration to the backend API (`/generate_topology`) when requested.
*   Receives the generated graph data from the backend.
*   Visualizes the topology using NetworkX and Matplotlib.
*   Displays the configuration JSON used for generation.
*   Allows downloading the configuration as a JSON file.

## Key Files

*   `app.py`: The main Streamlit application file containing the UI layout, state management, interaction logic, and calls to the backend API.
*   `requirements.txt`: Lists the Python dependencies required for the frontend (Streamlit, Requests, NetworkX, Matplotlib).

## Running Standalone (for development/testing)

While the main `../run_dev.sh` script handles running both backend and frontend, you can run the frontend independently (assuming the backend is already running separately):

1.  **Navigate to the project root directory.**
2.  **Set up and activate the virtual environment (if not already done):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate 
    ```
3.  **Install dependencies:**
    ```bash
    python -m pip install -r frontend/requirements.txt
    ```
4.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```
5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py --server.port 8501
    ```

The frontend application will be available at `http://localhost:8501`. 