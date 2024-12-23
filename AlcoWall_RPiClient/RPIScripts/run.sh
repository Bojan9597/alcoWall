#!/bin/bash

# Define variables
REPO_URL="https://github.com/Bojan9597/alcoWall.git"
DESKTOP_DIR="$HOME/Desktop/AlcoWall"
VENV_DIR="$HOME/AlcoWallEnvironment"
SCRIPT_DIR="$DESKTOP_DIR/alcowall/AlcoWall_RPiClient"
SCRIPT_PATH="$SCRIPT_DIR/main.py"

# Step 1: Clone the repository
mkdir -p "$DESKTOP_DIR"
if [ ! -d "$DESKTOP_DIR/alcowall" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$DESKTOP_DIR/alcowall"
else
    echo "Repository already exists. Pulling latest changes..."
    cd "$DESKTOP_DIR/alcowall" && git pull
fi

# Step 2: Install system dependencies for Qt
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libx11-xcb-dev

# Step 3: Create and activate the virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Step 4: Install required Python packages
echo "Installing required Python packages..."
pip install --upgrade pip
pip install requests PySide6 adafruit-circuitpython-ads1x15 IPython imageio[ffmpeg]

# Step 5: Change directory to the script's location and run it
cd "$SCRIPT_DIR"
echo "Running the Python script..."
python "$SCRIPT_PATH"

# Deactivate the virtual environment
deactivate

# End of script
echo "Done!"
