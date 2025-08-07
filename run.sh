#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Ollama Search App Setup ---"

# --- 1. Check for Python 3 ---
if ! command -v python3 &> /dev/null
then
    echo "ERROR: python3 could not be found. Please install Python 3."
    exit 1
fi

# --- 2. Create a Virtual Environment ---
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

# --- 3. Activate the Virtual Environment ---
# Note: The activation command differs between shells. This works for bash/zsh.
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# --- 4. Install Dependencies ---
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found. Skipping dependency installation."
fi

# --- 5. Run the Application ---
echo "-------------------------------------"
echo "Setup complete. Starting the Flask application..."
echo "Access the app at http://127.0.0.1:5000"
echo "Press CTRL+C to stop the server."
echo "-------------------------------------"
python3 app.py

# Deactivate the virtual environment when the script is stopped (e.g., with CTRL+C)
deactivate
echo "--- Server stopped. Virtual environment deactivated. ---"
