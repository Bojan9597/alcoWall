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
VIDEOS_DIRECTORY = "videos/"
DEVICE_ID = 1

alcoWall = AlcoWall()
from States.AlcoholCheck import AlcoholCheck

class InitialState(State):
    def __init__(self):
        alcoWall.video_widget.show()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.hide()   
        self.get_highscores()
        self.coin_check_timer = QTimer()
        self.coin_check_timer.timeout.connect(self.check_next_state)
        self.coin_check_timer.start(1000)  # Check every 1 second
        self.videos_directory = VIDEOS_DIRECTORY
        self.device_id = DEVICE_ID
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self.play_next_video)
        self.start_fetching_videos()

    def play_next_video(self):
        video_url = self.get_ad_url(self.device_id)
        
        if video_url:
            video_filename = self.extract_filename_from_url(video_url)
            video_path = os.path.join(self.videos_directory, video_filename)
            
            if os.path.exists(video_path):
                if not self.is_video_corrupted(video_path):
                    alcoWall.video_widget.play_video(video_path)
                    self.retry_timer.stop()  # Stop retrying
                else:
                    print(f"Video is corrupted, deleting: {video_path}")
                    os.remove(video_path)
                    self.retry_timer.start(1000)  # Retry fetching a valid video
            else:
                self.download_and_play_video(video_url, video_path)
        else:
            alcoWall.video_widget.play_video("videos/beer1.mp4")
            print("Failed to retrieve video URL. Retrying...")

    def download_and_play_video(self, video_url, save_path):
        try:
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as video_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            video_file.write(chunk)
                print(f"Video downloaded successfully and saved to {save_path}")
                
                if self.is_video_corrupted(save_path):
                    print(f"Downloaded video is corrupted, deleting: {save_path}")
                    os.remove(save_path)
                    alcoWall.video_widget.play_video("videos/beer1.mp4")
                else:
                    resolution = self.get_video_resolution(save_path)
                    print(f"Video resolution: {resolution[0]}x{resolution[1]}")
                    
                    if resolution != (1024, 600):
                        print(f"Converting video to 1024x600 resolution...")
                        self.convert_video_to_resolution(save_path, 1024, 600)
                        print(f"Video converted successfully to 1024x600.")
                    alcoWall.video_widget.play_video(save_path)

            else:
                print(f"Failed to download video. Status code: {response.status_code}")
                alcoWall.video_widget.play_video("videos/beer1.mp4")
        except requests.ConnectionError as e:
            print(f"Connection error while downloading: {e}")

    def is_video_corrupted(self, video_path):
        """Check if the video is corrupted using ffmpeg."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", video_path, "-f", "null", "-"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # If ffmpeg returns an error, the video is likely corrupted
            if result.returncode != 0:
                print(f"ffmpeg error: {result.stderr}")
                return True
            return False
        except Exception as e:
            print(f"Error checking video corruption: {e}")
            return True

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
        parsed_url = urlparse(video_url)
        return os.path.basename(parsed_url.path)
    
    def start_fetching_videos(self):
        self.retry_timer.start(1000)  # Retry every 2 seconds

    def handle_successful(self):
        self.coin_check_timer.stop()
        return AlcoholCheck()  # Transition to AlcoholCheck state

    def handle_unsuccessful(self):
        return self
    
    def handle_error(self):
        return InitialState()
    
    def check_next_state(self):
        if self.check_errors():
            alcoWall.handle_error()
        else:
            self.check_coin_inserted()

    def check_errors(self):
        try:
            if alcoWall.service_door_open or alcoWall.coins_door_open or alcoWall.coin_stuck:
                return True
            else:
                return False
        except FileNotFoundError:
            return True

    def check_coin_inserted(self):
        try:
            if alcoWall.credit >= 1:
                alcoWall.handle_successful() 
            else:
                alcoWall.handle_unsuccessful()
        except FileNotFoundError:
            pass

    def get_highscores(self):
        if not self.get_highscore_from_database():
            self.load_highscores()

    def get_highscore_from_database(self):
        return False
    
    def load_highscores(self):
        highscore_file = "jsonFiles/highscores.json"
        
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
        url = f"{BASE_URL}/advertisment/get_ad_url"
        payload = {"device_id": device_id}
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                ad_url = response.json().get("ad_url")
                if ad_url:
                    return ad_url
                else:
                    print("No ad URL found in the response.")
                    return None
            else:
                print(f"Failed to fetch ad URL. Status code: {response.status_code}")
                return None
        except requests.ConnectionError as e:
            print(f"Connection error: {e}")
            return None
