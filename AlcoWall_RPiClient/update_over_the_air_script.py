import os
import time
import subprocess
import psutil

# Use the current working directory as the repository path
REPO_PATH = os.getcwd()
SCRIPT_PATH = os.path.join(REPO_PATH, "../AlcoWall_RPiClient", "main.py")
GIT_URL = "https://github.com/Bojan9597/alcoWall.git"

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

def update_repository():
    """Pull the latest changes from the main branch."""
    print("Updating repository...")
    # Fetch all remotes and branches
    fetch_result = subprocess.run(["git", "fetch", "--all", "--prune"], cwd=REPO_PATH, capture_output=True, text=True)
    print(f"Fetch result: {fetch_result.stdout}")
    
    # Reset the local repository to match the remote main branch
    reset_result = subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=REPO_PATH, capture_output=True, text=True)
    print(f"Reset result: {reset_result.stdout}")
    
    print("Repository updated.")

def start_script():
    """Start the Python script."""
    print("Starting script...")
    subprocess.Popen(["python3", SCRIPT_PATH])

def check_for_updates():
    """Check if local repository is up-to-date with the remote main branch."""
    # Ensure we're on the main branch
    current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    # print(f"Current branch: {current_branch}")
    
    # If not on the main branch, switch to main
    if current_branch != "main":
        print("Switching to the main branch.")
        switch_branch_result = subprocess.run(["git", "checkout", "main"], cwd=REPO_PATH, capture_output=True, text=True)
        print(f"Switch branch result: {switch_branch_result.stdout}")
    
    # Fetch updates from the remote repository
    fetch_result = subprocess.run(["git", "fetch", "--all", "--prune"], cwd=REPO_PATH, capture_output=True, text=True)
    print(f"Fetch result: {fetch_result.stdout}")

    # Check the current git status
    git_status = subprocess.run(["git", "status"], cwd=REPO_PATH, capture_output=True, text=True).stdout
    print(f"Git status: {git_status}")

    # Compare the local commit with the remote commit
    local_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    remote_commit = subprocess.run(["git", "rev-parse", "origin/main"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()

    print(f"Local commit: {local_commit}")
    print(f"Remote commit: {remote_commit}")
    
    return local_commit != remote_commit

def main():
    """Main loop to check for updates every 10 seconds."""
    start_script()
    while True:
        if check_for_updates():
            print("Repository is out of sync with remote. Updating...")

            # Check if the Python script is running
            process = is_process_running(SCRIPT_PATH)
            if process:
                print(f"Script is running. Stopping process {process.pid}.")
                stop_process(process)
            
            # Update the repository
            update_repository()

            # Start the script again
            start_script()
        
        else:
            pass
            # print("Repository is up-to-date.")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
