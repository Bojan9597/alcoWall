import os
import time
import subprocess
import psutil
import requests
import json
import platform
from Constants.GENERALCONSTANTS import *

# Use the current working directory as the repository path
REPO_PATH = os.getcwd()
SCRIPT_PATH = os.path.join(REPO_PATH, "../AlcoWall_RPiClient", "main.py")

# Path to the virtual environment's Python interpreter for Raspberry Pi
VENV_PYTHON = "/home/bojan/AlcoWallEnvironment/bin/python3"

STATE_FILE = os.path.join(REPO_PATH, "States", "current_state.txt")
INITIAL_STATE = "InitialState"


def read_device_id():
    """Read the device ID from the device_id.txt file."""
    try:
        with open(DEVICE_ID_FILE, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def read_current_state():
    """Read the current state from the state file."""
    try:
        with open(STATE_FILE, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def write_current_state(state):
    """Write the given state to the state file."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as file:
        file.write(state)


def get_github_branch(device_id):
    """Get the GitHub branch name by making a POST request with the device ID."""
    try:
        response = requests.post(BRANCH_API_URL, json={"device_id": device_id})
        if response.status_code == 200:
            data = response.json()
            return data.get("github_branch_name")
        return None
    except requests.RequestException:
        return None


def is_process_running(script_name):
    """Check if the Python script is currently running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and script_name in cmdline:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


def stop_process(process):
    """Terminate the given process."""
    if process:
        process.terminate()
        process.wait()


def update_repository(branch_name):
    """Pull the latest changes from the specified branch."""
    subprocess.run(["git", "fetch", "--all", "--prune"], cwd=REPO_PATH, capture_output=True, text=True)
    
    current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    
    if current_branch != branch_name:
        subprocess.run(["git", "checkout", branch_name], cwd=REPO_PATH, capture_output=True, text=True)
    
    subprocess.run(["git", "reset", "--hard", f"origin/{branch_name}"], cwd=REPO_PATH, capture_output=True, text=True)


def start_script():
    """Start the Python script using the appropriate Python interpreter."""
    if platform.system() == "Linux" and platform.machine() in ("armv7l", "armv6l", "aarch64"):
        subprocess.Popen([VENV_PYTHON, SCRIPT_PATH])
    else:
        subprocess.Popen(["python3", SCRIPT_PATH])


def check_for_updates(branch_name):
    """Check if local repository is up-to-date with the remote branch."""
    current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    
    if current_branch != branch_name:
        subprocess.run(["git", "checkout", branch_name], cwd=REPO_PATH, capture_output=True, text=True)
    
    subprocess.run(["git", "fetch", "--all", "--prune"], cwd=REPO_PATH, capture_output=True, text=True)

    local_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    remote_commit = subprocess.run(["git", "rev-parse", f"origin/{branch_name}"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()

    return local_commit != remote_commit


def internet_is_available():
    """Check if the internet connection is available by pinging a known server."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def main():
    """Main loop to check for updates while ensuring the script runs even without internet."""
    device_id = read_device_id()

    if not device_id:
        print("Device ID not found. Exiting.")
        return

    # Set the state to InitialState initially
    write_current_state(INITIAL_STATE)

    # Start the main application script immediately
    start_script()

    branch_name = get_github_branch(device_id)

    while True:
        current_state = read_current_state()

        # Proceed only if the state is InitialState
        if current_state != INITIAL_STATE:
            print(f"Current state is {current_state}. Update skipped.")
            time.sleep(10)
            continue

        # Check if the main script is running; if not, restart it
        process = is_process_running(SCRIPT_PATH)
        if not process:
            print("Main script is not running. Starting it.")
            start_script()

        if internet_is_available():
            print("Internet connection is available. Checking for updates...")

            if not branch_name:
                branch_name = get_github_branch(device_id)
                if not branch_name:
                    print("Could not retrieve branch information. Retrying...")

            if branch_name and check_for_updates(branch_name):
                print(f"Repository is out of sync with remote {branch_name} branch. Updating...")

                process = is_process_running(SCRIPT_PATH)
                if process:
                    stop_process(process)

                update_repository(branch_name)
                start_script()
            else:
                print("Repository is up-to-date or branch information not available.")
        else:
            print("No internet connection. Retrying in 10 seconds.")

        time.sleep(10)


if __name__ == "__main__":
    main()
