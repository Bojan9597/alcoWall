
import os
from PySide6.QtCore import QTimer, Qt
from AlcoWall import AlcoWall
from States.state import State
import json
from datetime import datetime, timedelta

alcoWall = AlcoWall()
from States.AlcoholCheck import AlcoholCheck

class InitialState(State):
    def __init__(self):
        print("InitialState: __init__")
        alcoWall.video_widget.show()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.hide()   
        self.get_highscores()
        self.coin_check_timer = QTimer()
        self.coin_check_timer.timeout.connect(self.check_next_state)
        self.coin_check_timer.start(1000) 

    def handle_successful(self):
        alcoWall.credit -= 1
        alcoWall.credit_label.setText(str(alcoWall.credit))
        print("InitialState: handle_successful")
        self.coin_check_timer.stop()
        return AlcoholCheck()  # Transition to CoinInsertedState

    def handle_unsuccessful(self):
        print("InitialState: handle_unsuccessful")
        return InitialState()
    
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
            print("Checking coin inserted")
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
        # Get highscores from the database
        # If the database is not available, return False
        return False
    
    def load_highscores(self):
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

        # Update the highscore variables and labels
        alcoWall.weekly_highscore = highscores.get("weekly_highscore", 0.0)
        alcoWall.monthly_highscore = highscores.get("monthly_highscore", 0.0)
        alcoWall.highscore = highscores.get("highscore", 0.0)
        alcoWall.weekly_highscore_label.setText("weekly highscore" + str(alcoWall.weekly_highscore))
        alcoWall.monthly_highscore_label.setText("monthly highscore" + str(alcoWall.monthly_highscore))
        alcoWall.highscore_label.setText("highscore" + str(alcoWall.highscore))

        alcoWall.weekly_highscore
