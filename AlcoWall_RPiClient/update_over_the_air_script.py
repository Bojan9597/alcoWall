import os
import time
import subprocess
import psutil
import requests
import json
from CONSTANTS import *
# Use the current working directory as the repository path
REPO_PATH = os.getcwd()
SCRIPT_PATH = os.path.join(REPO_PATH, "../AlcoWall_RPiClient", "main.py")

def read_device_id():
    """Read the device ID from the device_id.txt file."""
    try:
        with open(DEVICE_ID_FILE, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        # print(f"Error: {DEVICE_ID_FILE} not found.")
        return None

def get_github_branch(device_id):
    """Get the GitHub branch name by making a POST request with the device ID."""
    try:
        response = requests.post(BRANCH_API_URL, json={"device_id": device_id})
        if response.status_code == 200:
            data = response.json()
            if "github_branch_name" in data:
                return data["github_branch_name"]
            elif "message" in data and data["message"] == "Device not found.":
                # print("Device not found.")
                return None
        else:
            # print(f"Error: Received status code {response.status_code} from server.")
            return None
    except requests.RequestException as e:
        # print(f"Error during HTTP request: {e}")
        return None

def is_process_running(script_name):
    """Check if the Python script is currently running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if script is in the command line arguments
            if script_name in proc.info['cmdline']:
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
    print(f"Updating repository on branch: {branch_name}...")
    # Fetch all remotes and branches
    fetch_result = subprocess.run(["git", "fetch", "--all", "--prune"], cwd=REPO_PATH, capture_output=True, text=True)
    print(f"Fetch result: {fetch_result.stdout}")
    
    # Switch to the branch if it's different
    current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    
    if current_branch != branch_name:
        print(f"Switching to branch: {branch_name}")
        checkout_result = subprocess.run(["git", "checkout", branch_name], cwd=REPO_PATH, capture_output=True, text=True)
        print(f"Checkout result: {checkout_result.stdout}")
    
    # Reset the local repository to match the remote branch
    reset_result = subprocess.run(["git", "reset", "--hard", f"origin/{branch_name}"], cwd=REPO_PATH, capture_output=True, text=True)
    print(f"Reset result: {reset_result.stdout}")
    
    print("Repository updated.")

def start_script():
    """Start the Python script."""
    print("Starting script...")
    subprocess.Popen(["python3", SCRIPT_PATH])

def check_for_updates(branch_name):
    """Check if local repository is up-to-date with the remote branch."""
    # Ensure we're on the correct branch
    current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    
    # Switch to the correct branch if necessary
    if current_branch != branch_name:
        # print(f"Switching to the {branch_name} branch.")
        switch_branch_result = subprocess.run(["git", "checkout", branch_name], cwd=REPO_PATH, capture_output=True, text=True)
        # print(f"Switch branch result: {switch_branch_result.stdout}")
    
    # Fetch updates from the remote repository
    fetch_result = subprocess.run(["git", "fetch", "--all", "--prune"], cwd=REPO_PATH, capture_output=True, text=True)
    # print(f"Fetch result: {fetch_result.stdout}")

    # Check the current git status
    git_status = subprocess.run(["git", "status"], cwd=REPO_PATH, capture_output=True, text=True).stdout
    # print(f"Git status: {git_status}")

    # Compare the local commit with the remote commit
    local_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    remote_commit = subprocess.run(["git", "rev-parse", f"origin/{branch_name}"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()

    # print(f"Local commit: {local_commit}")
    # print(f"Remote commit: {remote_commit}")
    
    return local_commit != remote_commit

def main():
    """Main loop to check for updates every 10 seconds."""
    device_id = read_device_id()
    if not device_id:
        # print("Device ID not found. Exiting.")
        return
    
    branch_name = get_github_branch(device_id)
    if not branch_name:
        # print("Could not retrieve branch information. Exiting.")
        return
    
    start_script()
    
    while True:
        if check_for_updates(branch_name):
            # print(f"Repository is out of sync with remote {branch_name} branch. Updating...")

            # Check if the Python script is running
            process = is_process_running(SCRIPT_PATH)
            if process:
                # print(f"Script is running. Stopping process {process.pid}.")
                stop_process(process)
            
            # Update the repository
            update_repository(branch_name)

            # Start the script again
            start_script()
        
        else:
            pass
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
