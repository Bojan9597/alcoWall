import os
from PySide6.QtCore import QTimer, Qt
from AlcoWall import AlcoWall
from States.state import State
import json
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse
import subprocess
BASE_URL = "https://node.alkowall.indigoingenium.ba"  # Intentional wrong URL for retry testing

alcoWall = AlcoWall()
from States.AlcoholCheck import AlcoholCheck

class InitialState(State):
    def __init__(self):
        """
        @brief Initializes the InitialState.

        This constructor sets up the initial state of the AlcoWall system. It performs the following tasks:
        
        - Displays the video widget to the user.
        - Hides the background image and working widgets.
        - Retrieves high scores from either the database or a local JSON file.
        - Sets up a timer to periodically check for coin insertion.
        
        The timer is configured to trigger every second, ensuring that the state can promptly respond to user actions.

        This setup ensures that the system is in a ready state to detect coin insertions and handle state transitions based on user interactions and system status.
        """
        # alcoWall.credit = 0 # Remove this line
        print("InitialState: __init__")
        alcoWall.video_widget.show()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.hide()   
        self.get_highscores()
        self.coin_check_timer = QTimer()
        self.coin_check_timer.timeout.connect(self.check_next_state)
        self.coin_check_timer.start(1000)  # Check every 1 second
        self.videos_directory = "videos/"
        self.device_id = 1
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self.play_next_video())
        # Start the first video fetching process
        self.start_fetching_videos()

    def play_next_video(self):
        # Get the video URL
        video_url = self.get_ad_url(self.device_id)
        
        if video_url:
            # Extract the video filename from the URL
            video_filename = self.extract_filename_from_url(video_url)
            video_path = os.path.join(self.videos_directory, video_filename)
            
            # Check if the video already exists
            if os.path.exists(video_path):
                # Play the video if it exists
                alcoWall.video_widget.play_video(video_path)
                print("Playing existing video..." + video_path)
                self.retry_timer.stop()  # Stop retrying
            else:
                # Download and then play the video
                self.download_and_play_video(video_url, video_path)
                print("Downloading and playing video..." + video_path)
                self.retry_timer.stop()  # Stop retrying
        else:
            print("Failed to retrieve video URL. Retrying...")

    def download_and_play_video(self, video_url, save_path):
        # Download the video from the ad URL
        try:
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as video_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            video_file.write(chunk)
                print(f"Video downloaded successfully and saved to {save_path}")
                
                # Check the resolution of the video
                resolution = self.get_video_resolution(save_path)
                print(f"Video resolution: {resolution[0]}x{resolution[1]}")

                # If the resolution is not 1024x600, convert it
                if resolution != (1024, 600):
                    print(f"Converting video to 1024x600 resolution...")
                    self.convert_video_to_resolution(save_path, 1024, 600)
                    print(f"Video converted successfully to 1024x600.")
                else:
                    print("Video resolution is already 1024x600, no conversion needed.")

                # Play the downloaded (or converted) video
                alcoWall.video_widget.play_video(save_path)

            else:
                print(f"Failed to download video. Status code: {response.status_code}")
        except requests.ConnectionError as e:
            print(f"Connection error while downloading: {e}")

    def get_video_resolution(self, video_path):
        """Use ffmpeg to get the resolution of the video."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", 
                "stream=width,height", "-of", "csv=s=x:p=0", video_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            width, height = map(int, result.stdout.strip().split('x'))
            return width, height
        except Exception as e:
            print(f"Error getting video resolution: {e}")
            return None, None

    def convert_video_to_resolution(self, video_path, width, height):
        """Convert the video to the specified resolution using ffmpeg."""
        try:
            temp_path = video_path + "_temp.mp4"
            subprocess.run(
                ["ffmpeg", "-i", video_path, "-vf", f"scale={width}:{height}", "-crf", "23", temp_path],
                check=True
            )
            # Replace the original file with the converted one
            os.replace(temp_path, video_path)
        except subprocess.CalledProcessError as e:
            print(f"Error during video conversion: {e}")
    
    def extract_filename_from_url(self, video_url):
        # Extract the filename from the URL path
        parsed_url = urlparse(video_url)
        return os.path.basename(parsed_url.path)
    
    def start_fetching_videos(self):
        # Start the retry timer to attempt to fetch a valid URL every 2 seconds
        self.retry_timer.start(1000)  # Retry every 2 seconds

    def handle_successful(self):
        """
        @brief Handles the successful insertion of a coin.

        This function is called when a coin is successfully inserted. It decreases the credit,
        updates the credit label, stops the coin check timer, and transitions to the AlcoholCheck state.

        @return AlcoholCheck: The next state to transition to.
        """
        print("InitialState: handle_successful")
        self.coin_check_timer.stop()
        return AlcoholCheck()  # Transition to AlcoholCheck state

    def handle_unsuccessful(self):
        """
        @brief Handles the unsuccessful insertion of a coin.

        This function is called when a coin is not successfully inserted.
        It simply returns the current state to retry the process.

        @return InitialState: The current state to remain in.
        """
        print("InitialState: handle_unsuccessful")
        return self
    
    def handle_error(self):
        """
        @brief Handles errors during the initial state.

        This function is called when an error is detected in the process.
        It simply prints an error message and returns the current state.

        @return InitialState: The current state to remain in.
        """
        print("InitialState: handle_error")
        return InitialState()
    
    def check_next_state(self):
        """
        @brief Checks for errors and proceeds to check coin insertion if no errors are found.

        This function is called periodically by a timer to determine whether to transition
        to the next state or handle an error.
        """
        # print("Checking next state")
        if self.check_errors():
            alcoWall.handle_error()
        else:
            self.check_coin_inserted()

    def check_errors(self):
        """
        @brief Checks for any errors such as open service or coin doors, or coin stuck.

        This function checks various error conditions that might prevent the process
        from continuing.

        @return bool: True if any error is detected, False otherwise.
        """
        try:
            if alcoWall.service_door_open or alcoWall.coins_door_open or alcoWall.coin_stuck:
                return True
            else:
                return False
        except FileNotFoundError:
            return True

    def check_coin_inserted(self):
        """
        @brief Checks if a coin has been inserted.

        This function checks if the user has inserted enough coins to proceed.
        If so, it handles the successful coin insertion. Otherwise, it handles the unsuccessful attempt.
        """
        try:
            # print("Checking coin inserted")
            if alcoWall.credit >= 1:
                print("credit in check_coin_inserted: ", alcoWall.credit)
                alcoWall.handle_successful() 
            else:
                alcoWall.handle_unsuccessful()
        except FileNotFoundError:
            pass

    def get_highscores(self):
        """
        @brief Retrieves high scores from the database or local file.

        This function first attempts to get high scores from the database. If that fails,
        it loads high scores from a local JSON file.
        """
        if not self.get_highscore_from_database():
            self.load_highscores()

    def get_highscore_from_database(self):
        """
        @brief Attempts to retrieve high scores from the database.

        This function is a placeholder for database interaction.
        Currently, it always returns False to indicate that the database is not available.

        @return bool: False if the database is not available.
        """
        # Get highscores from the database
        # If the database is not available, return False
        return False
    
    def load_highscores(self):
        """
        @brief Loads high scores from a local JSON file.

        This function reads high scores from a specified JSON file and updates the relevant
        highscore variables and UI labels.

        If the file cannot be read, it handles the IOError and continues.
        """
        highscore_file = "jsonFiles/highscores.json"
        
        # Initialize highscores
        highscores = {
            "weekly_highscore": 0.0,
            "monthly_highscore": 0.0,
            "highscore": 0.0
        }

        if os.path.exists(highscore_file):
            try:
                with open(highscore_file, "r") as file:
                    highscores = json.load(file)
            except IOError as e:
                print(f"An error occurred while reading the highscore file: {e}")

    def get_ad_url(self, device_id):
            # Function to get ad URL
            url = f"{BASE_URL}/advertisment/get_ad_url"
            payload = {"device_id": device_id}
            try:
                response = requests.post(url, json=payload)
                # response.status_code = random.choice([200, 404])  # Simulate random status codes
                if response.status_code == 200:
                    # Assuming the response JSON has an "ad_url" field
                    ad_url = response.json().get("ad_url")
                    if ad_url:
                        return ad_url
                    else:
                        print("No ad URL found in the response.")
                        return None
                else:
                    print(f"Failed to fetch ad URL. Status code: {response.status_code}")
                    self.video_widget.show_placeholder()
                    return None
            except requests.ConnectionError as e:
                print(f"Connection error: {e}")
                return None