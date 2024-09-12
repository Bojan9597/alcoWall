import os
import time
import subprocess
import psutil

# Use the current working directory as the repository path
REPO_PATH = os.getcwd()
SCRIPT_PATH = os.path.join(REPO_PATH, "AlcoWall_RPiClient", "main.py")
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
    subprocess.run(["git", "fetch"], cwd=REPO_PATH)
    subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=REPO_PATH)
    print("Repository updated.")

def start_script():
    """Start the Python script."""
    print("Starting script...")
    subprocess.Popen(["python3", SCRIPT_PATH])

def check_for_updates():
    """Check if local repository is up-to-date with the remote main branch."""
    # Fetch updates from the remote repository
    fetch_result = subprocess.run(["git", "fetch", GIT_URL], cwd=REPO_PATH, capture_output=True)
    
    # Check if the local main branch is behind the remote
    local_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()
    remote_commit = subprocess.run(["git", "rev-parse", "origin/main"], cwd=REPO_PATH, capture_output=True, text=True).stdout.strip()

    return local_commit != remote_commit

def main():
    """Main loop to check for updates every 10 seconds."""
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
            print("Repository is up-to-date.")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()
