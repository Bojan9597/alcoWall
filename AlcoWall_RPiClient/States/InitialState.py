# InitialState.py

import os
from PySide6.QtCore import QTimer, Qt, Slot
from Components.AlcoWall import AlcoWall
from States.state import State
import requests
from urllib.parse import urlparse
import subprocess
from Constants.GENERALCONSTANTS import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEOS_DIRECTORY, DEVICE_ID
from DatabaseManagement.DataManager import DataManager
from States.AlcoholCheck import AlcoholCheck

alcoWall = AlcoWall()

class InitialState(State):
    def __init__(self):
        alcoWall.video_widget.show()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.hide()

        self.device_id = alcoWall.read_device_id()
        self.data_manager = DataManager(self.device_id)
        self.get_highscores()

        self.coin_check_timer = QTimer()
        self.coin_check_timer.timeout.connect(self.check_next_state)
        self.coin_check_timer.start(100)  # Check every 100 milliseconds

        self.videos_directory = VIDEOS_DIRECTORY
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self.play_next_video)
        self.start_fetching_videos()
        alcoWall.video_widget.video_finished.connect(self.video_finished_handler)

    @Slot()
    def video_finished_handler(self):
        print("Video finished.")
        self.play_next_video()

    def play_next_video(self):
        print("Fetching video...")
        video_url = self.data_manager.get_ad_url()

        if video_url:
            video_filename = self.extract_filename_from_url(video_url)
            video_path = os.path.join(self.videos_directory, video_filename)
            print(f"Video URL: {video_url}")
            if os.path.exists(video_path):
                if not self.is_video_corrupted(video_path):
                    print(f"Playing video: {video_path}")
                    alcoWall.video_widget.play_video(video_path)
                    self.retry_timer.stop()  # Stop retrying
                else:
                    print(f"Video is corrupted, deleting: {video_path}")
                    os.remove(video_path)
                    self.retry_timer.start(1000)  # Retry fetching a valid video
            else:
                self.download_and_play_video(video_url, video_path)
        else:
            alcoWall.video_widget.play_video("Media/videos/beer1.mp4")
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
                    alcoWall.video_widget.play_video("Media/videos/beer1.mp4")
                else:
                    resolution = self.get_video_resolution(save_path)
                    print(f"Video resolution: {resolution[0]}x{resolution[1]}")

                    if resolution != (VIDEO_WIDTH, VIDEO_HEIGHT):
                        print(f"Converting video to {VIDEO_WIDTH}x{VIDEO_HEIGHT} resolution...")
                        self.convert_video_to_resolution(save_path, VIDEO_WIDTH, VIDEO_HEIGHT)
                        print("Video converted successfully.")
                    alcoWall.video_widget.play_video(save_path)

            else:
                print(f"Failed to download video. Status code: {response.status_code}")
                alcoWall.video_widget.play_video("Media/videos/beer1.mp4")
        except requests.ConnectionError as e:
            print(f"Connection error while downloading: {e}")
            alcoWall.video_widget.play_video("Media/videos/beer1.mp4")

    def is_video_corrupted(self, video_path):
        """Check if the video is corrupted using ffmpeg."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", video_path, "-f", "null", "-"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # If ffmpeg returns an error, the video is likely corrupted
            if result.returncode != 0:
                print(f"ffmpeg error: {result.stderr.decode()}")
                return True
            return False
        except Exception as e:
            print(f"Error checking video corruption: {e}")
            return True

    def get_video_resolution(self, video_path):
        """Use ffprobe to get the resolution of the video."""
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
        self.play_next_video()

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
            if alcoWall.get_credit() >= 100:
                alcoWall.handle_successful()
            else:
                alcoWall.handle_unsuccessful()
        except FileNotFoundError:
            pass

    def get_highscores(self):
        """
        Try to fetch highscore from the external API.
        If successful, compare it with the local highscore.
        If the local highscore is higher, send it to the server.
        If the request fails, load highscores from the local file.
        """
        latest_database_highscore = self.data_manager.get_highscore_from_database()

        if latest_database_highscore is not None:
            # Load local highscores
            local_highscores = self.data_manager.load_highscores_from_file()

            # Compare with local highscore
            if local_highscores["highscore"] > latest_database_highscore:
                success = self.data_manager.send_alcohol_level_to_database(
                    local_highscores["highscore"]
                )

                if success:
                    print("Local highscore sent to the database.")
                    # Update database highscore
                    latest_database_highscore = local_highscores["highscore"]
                else:
                    print("Failed to send local highscore to the database.")
            else:
                print(f"Database highscore is higher or equal: {latest_database_highscore}. No update needed.")

            # Update the local highscores with the database highscore
            self.data_manager.update_highscores(local_highscores, latest_database_highscore)

            # Save the updated highscores back to the local file
            self.data_manager.update_local_highscores(local_highscores)

            # Update alcoWall variables
            alcoWall.weekly_highscore = local_highscores["weekly_highscore"]
            alcoWall.monthly_highscore = local_highscores["monthly_highscore"]
            alcoWall.highscore = local_highscores["highscore"]

        else:
            # Load highscores from the local file if fetching from the database failed
            local_highscores = self.data_manager.load_highscores_from_file()
            # Update alcoWall variables with local highscores
            alcoWall.weekly_highscore = local_highscores["weekly_highscore"]
            alcoWall.monthly_highscore = local_highscores["monthly_highscore"]
            alcoWall.highscore = local_highscores["highscore"]

    # Rest of the class remains unchanged