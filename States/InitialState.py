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
        print("InitialState: __init__")
        alcoWall.video_widget.show()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.hide()   
        self.get_highscores()
        self.coin_check_timer = QTimer()
        self.coin_check_timer.timeout.connect(self.check_next_state)
        self.coin_check_timer.start(1000)  # Check every 1 second

    def handle_successful(self):
        """
        @brief Handles the successful insertion of a coin.

        This function is called when a coin is successfully inserted. It decreases the credit,
        updates the credit label, stops the coin check timer, and transitions to the AlcoholCheck state.

        @return AlcoholCheck: The next state to transition to.
        """
        alcoWall.credit -= 1
        alcoWall.credit_label.setText(str(alcoWall.credit))
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
        return InitialState()
    
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
        print("Checking next state")
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
            print("Checking coin inserted")
            if alcoWall.credit >= 1:
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

        # Update the highscore variables and labels
        alcoWall.weekly_highscore = highscores.get("weekly_highscore", 0.0)
        alcoWall.monthly_highscore = highscores.get("monthly_highscore", 0.0)
        alcoWall.highscore = highscores.get("highscore", 0.0)
        alcoWall.weekly_highscore_label.setText("weekly highscore" + str(alcoWall.weekly_highscore))
        alcoWall.monthly_highscore_label.setText("monthly highscore" + str(alcoWall.monthly_highscore))
        alcoWall.highscore_label.setText("highscore" + str(alcoWall.highscore))
