import os
from PySide6.QtCore import QTimer, Qt
from AlcoWall import AlcoWall
from States.state import State
import json
from datetime import datetime, timedelta
# from InitialState import InitialState

alcoWall = AlcoWall()

class AlcoholCheck(State):
    def __init__(self):
        alcoWall.video_widget.hide()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.show()   
        self.alcohol_check_timer = QTimer()
        self.alcohol_check_timer.timeout.connect(self.check_next_state)
        self.alcohol_check_timer.start(2000)  # Check every 1 second
        print("AlcoholCheck: __init__")
    
    def handle_successful(self):
        print("Alcohol level inserted successfully")
        print(alcoWall.alcohol_level)
        self.write_data()
        self.alcohol_check_timer.stop()
        from States.InitialState import InitialState
        return InitialState()  # Transition back to InitialState

    def handle_unsuccessful(self):
        print("Alcohol level insertion failed")
        return self

    def handle_error(self):
        from States.InitialState import InitialState
        return InitialState()

    def check_next_state(self):
        if self.check_errors():
            alcoWall.handle_error()
        else:
            self.check_alcohol()

    def check_errors(self):
        try:
            if alcoWall.service_door_open or alcoWall.coins_door_open or alcoWall.coin_stuck:
                return True
            else:
                return False
        except FileNotFoundError:
            return True
    def check_proximity(self):
        try:
            if alcoWall.proximity_distance < 5 and alcoWall.proximity_distance >= 0:
                pass
            else:
                pass
        except FileNotFoundError:
            pass

    def check_alcohol(self):
        try:
            if alcoWall.alcohol_level >= 0:
                alcoWall.handle_successful()
            else:
                alcoWall.handle_unsuccessful()
        except FileNotFoundError:
            pass

    def write_results_to_json_file(self):
        data = {
            "device_id": alcoWall.device_id,
            "alcohol_level": alcoWall.alcohol_level,
            "status": "success" if alcoWall.alcohol_level else "failure"
        }

        try:
            with open("jsonFiles/alcohol_results.json", "a") as json_file:
                json.dump(data, json_file)
                json_file.write("\n")  # Write each entry on a new line
            print("Results written to JSON file.")
        except IOError as e:
            print(f"An error occurred while writing to the JSON file: {e}")

    def write_highscore_to_file(self):
        highscore_file = "jsonFiles/highscores.json"
        
        # Initialize highscores
        highscores = {
            "weekly_highscore": 0.0,
            "monthly_highscore": 0.0,
            "highscore": 0.0,
            "last_updated_week": datetime.now().isocalendar()[1],
            "last_updated_month": datetime.now().month
        }

        # Load existing highscores if the file exists
        if os.path.exists(highscore_file):
            try:
                with open(highscore_file, "r") as file:
                    highscores = json.load(file)
            except IOError as e:
                print(f"An error occurred while reading the highscore file: {e}")

        current_week = datetime.now().isocalendar()[1]
        current_month = datetime.now().month

        # Reset weekly or monthly highscore if the period has changed
        if highscores["last_updated_week"] != current_week:
            highscores["weekly_highscore"] = 0.0
            highscores["last_updated_week"] = current_week

        if highscores["last_updated_month"] != current_month:
            highscores["monthly_highscore"] = 0.0
            highscores["last_updated_month"] = current_month

        # Update highscores if the current alcohol level is higher
        if alcoWall.alcohol_level > highscores["weekly_highscore"]:
            highscores["weekly_highscore"] = alcoWall.alcohol_level
            alcoWall.weekly_highscore = alcoWall.alcohol_level
            alcoWall.weekly_highscore_label.setText("weekly highscore" + str(alcoWall.weekly_highscore))

        if alcoWall.alcohol_level > highscores["monthly_highscore"]:
            highscores["monthly_highscore"] = alcoWall.alcohol_level
            alcoWall.monthly_highscore = alcoWall.alcohol_level
            alcoWall.monthly_highscore_label.setText("monthly highscore" + str(alcoWall.monthly_highscore))

        if alcoWall.alcohol_level > highscores["highscore"]:
            highscores["highscore"] = alcoWall.alcohol_level
            alcoWall.highscore = alcoWall.alcohol_level
            alcoWall.highscore_label.setText("highscore" + str(alcoWall.highscore))

        # Write updated highscores back to the file
        try:
            with open(highscore_file, "w") as file:
                json.dump(highscores, file, indent=4)
            print("Highscores updated.")
        except IOError as e:
            print(f"An error occurred while writing to the highscore file: {e}")

    def write_results_to_database(self):
        # Read data from the JSON file and write it to the database
        # If the database is not available, return False
        #else write data and delete content of the file
        return False

    def write_data(self):
        self.write_highscore_to_file()
        self.write_results_to_json_file()
        self.write_results_to_database()