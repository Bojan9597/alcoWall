import os
from PySide6.QtCore import QTimer, Qt, QDateTime
from AlcoWall import AlcoWall
from States.state import State
import json
from datetime import datetime, timedelta

alcoWall = AlcoWall()

class AlcoholCheck(State):
    def __init__(self):
        """
        @brief Initializes the AlcoholCheck state.
        
        This constructor sets up various timers to manage the state transitions and UI updates,
        initializes variables, and configures the user interface elements for the alcohol check process.

        - Initializes the start time for elapsed time tracking.
        - Sets up a timer to check elapsed time every second.
        - Configures UI elements to hide video and background images and show the working widget.
        - Sets up a timer to check user proximity every second.
        - Sets up a timer to check the next state transition every 2 seconds.
        - Initializes text labels to guide the user.
        - Initializes variables for tracking the local maximum alcohol level.
        - Sets up a timer to update the local maximum alcohol level every 300 milliseconds.
        - Initializes a counter to track the user's proximity and blowing activity.
        """
        self.start_time = QDateTime.currentDateTime()
        alcoWall.credit -= 1

        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.check_elapsed_time)
        self.elapsed_timer.start(1000)  # Check every 1 second

        self.counterForMeasuring = 10

        alcoWall.video_widget.hide()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.show()

        self.check_proximity_timer = QTimer()
        self.check_proximity_timer.timeout.connect(self.check_proximity)
        self.check_proximity_timer.start(1000)  # Check every 1 second

        self.counterTimer = QTimer()
        self.counterTimer.timeout.connect(self.decreaseCounter)
        self.counterTimer.start(1000)

        print("AlcoholCheck: __init__")
        alcoWall.workingWidget.alcoholSensorText.setText("Blow into the alcohol \n sensor until the beep")
        alcoWall.workingWidget.proximitySensorText.setText("")
        alcoWall.workingWidget.resultLabelText.setText("Alcohol level: ")
        alcoWall.workingWidget.lcdNumber.setValue(0)
        alcoWall.workingWidget.lcdCounter.setText(str(self.counterForMeasuring))

        self.alcohol_local_maximum = 0
        self.alcohol_local_maximum_updated = False

        self.alcohol_local_maximum_timer = QTimer()
        self.alcohol_local_maximum_timer.timeout.connect(self.check_local_maximum)
        self.alcohol_local_maximum_timer.start(300)  # Check every 300 milliseconds
        alcoWall.workingWidget.play_video('videos/Heineken.mp4')


    def handle_successful(self):
        """
        @brief Handles the successful detection of alcohol levels.

        This function is called when an acceptable alcohol level is detected.
        It writes the data to the appropriate storage and transitions to the AlcoholChecked state.
        
        @return AlcoholChecked: The next state to transition to.
        """
        print("Alcohol level inserted successfully")
        print(alcoWall.alcohol_level)
        self.write_data()
        from States.AlcoholChecked import AlcoholChecked
        return AlcoholChecked()  # Transition back to InitialState
    
    def decreaseCounter(self):
        self.counterForMeasuring -= 1
        print(self.counterForMeasuring)
        alcoWall.workingWidget.lcdCounter.setText(str(self.counterForMeasuring))
        if self.counterForMeasuring == 0:
            self.counterTimer.stop()
            alcoWall.handle_successful()

    def handle_unsuccessful(self):
        """
        @brief Handles the unsuccessful detection of alcohol levels.

        This function is called when an acceptable alcohol level is not detected.
        It simply returns the current state to retry the process.
        
        @return self: The current state to remain in.
        """
        print("Alcohol level insertion failed")
        return self

    def handle_error(self):
        """
        @brief Handles errors during the alcohol check process.

        This function is called when an error is detected in the process.
        It transitions to the InitialState to handle the error appropriately.
        
        @return InitialState: The next state to transition to.
        """
        from States.InitialState import InitialState
        return InitialState()

    def check_next_state(self):
        """
        @brief Checks for errors and proceeds to check the alcohol level if no errors are found.

        This function is called periodically by a timer to determine whether to transition
        to the next state or handle an error.
        """
        if self.check_errors():
            alcoWall.handle_error()
        else:
            self.check_alcohol()

    def check_errors(self):
        """
        @brief Checks for any errors such as open service or coin doors, or coin stuck.

        This function checks various error conditions that might prevent the alcohol check process
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

    def check_proximity(self):
        """
        @brief Checks the proximity of the user to ensure they are close enough for a precise measurement.

        This function uses the proximity sensor to check if the user is within the required distance
        for an accurate breathalyzer reading. It updates the UI and a proximity blowing counter accordingly.
        """
        try:
            if alcoWall.proximity_distance < 20 and alcoWall.proximity_distance >= 0:
                alcoWall.workingWidget.proximitySensorText.setText("")
            else:
                alcoWall.workingWidget.proximitySensorText.setText("Come closer for a \nprecise measurement")
        except FileNotFoundError:
            pass

    def check_alcohol(self):
        """
        @brief Checks the alcohol level and transitions if the level is sufficient or enough time has passed.

        This function checks the detected alcohol level and decides whether to handle it as successful
        or prompt the user to continue blowing. It also transitions based on the proximity blowing counter.
        """
        try:
            if self.counterForMeasuring < 1:
                if self.alcohol_local_maximum > 0.1 and self.alcohol_local_maximum_updated == False:
                    alcoWall.handle_successful()
                elif self.alcohol_local_maximum <= 0.1:
                    alcoWall.handle_successful()
            else:
                alcoWall.workingWidget.alcoholSensorText.setText("Blow into the alcohol \n sensor until the beep")
        except FileNotFoundError:
            pass

    def write_results_to_json_file(self):
        """
        @brief Writes the results of the alcohol check to a JSON file.

        This function saves the alcohol level and status (success or failure) to a JSON file
        for record-keeping and later analysis.
        """
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
        """
        @brief Writes the highscore to a JSON file.

        This function updates and saves the weekly, monthly, and all-time highscores
        based on the detected alcohol levels. It resets the scores if the week or month has changed.
        """
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

        if alcoWall.alcohol_level > highscores["monthly_highscore"]:
            highscores["monthly_highscore"] = alcoWall.alcohol_level
            alcoWall.monthly_highscore = alcoWall.alcohol_level

        if alcoWall.alcohol_level > highscores["highscore"]:
            highscores["highscore"] = alcoWall.alcohol_level
            alcoWall.highscore = alcoWall.alcohol_level

        # Write updated highscores back to the file
        try:
            with open(highscore_file, "w") as file:
                json.dump(highscores, file, indent=4)
            print("Highscores updated.")
        except IOError as e:
            print(f"An error occurred while writing to the highscore file: {e}")

    def write_results_to_database(self):
        """
        @brief Writes the results of the alcohol check to the database.

        This function reads the data from the JSON file and attempts to write it to the database.
        If the database is not available, it returns False.

        @return bool: False if the database is not available.
        """
        # Read data from the JSON file and write it to the database
        # If the database is not available, return False
        # else write data and delete content of the file
        return False

    def write_data(self):
        """
        @brief Writes data to the highscore file, JSON file, and database.

        This function is responsible for ensuring that all relevant data is saved
        to the appropriate storage mechanisms.
        """
        self.write_highscore_to_file()
        self.write_results_to_json_file()
        self.write_results_to_database()

    def check_elapsed_time(self):
        """
        @brief Checks the elapsed time since the start of the alcohol check.

        This function is called periodically by a timer to check if the elapsed time
        has exceeded a certain threshold (20 seconds). If so, it handles the error.

        @return None
        """
        elapsed = self.start_time.secsTo(QDateTime.currentDateTime())
        if elapsed >= 20:  # 20 seconds
            alcoWall.handle_error()

    def check_local_maximum(self):
        """
        @brief Checks and updates the local maximum alcohol level detected.

        This function periodically checks if the current alcohol level is higher than the previous
        local maximum and updates it if necessary. It also flags if the local maximum has been updated.

        @return None
        """
        if alcoWall.alcohol_level > self.alcohol_local_maximum:
            self.alcohol_local_maximum = max(self.alcohol_local_maximum, alcoWall.alcohol_level)
            self.alcohol_local_maximum_updated = True
        else:
            self.alcohol_local_maximum_updated = False
        alcoWall.workingWidget.lcdNumber.setValue(self.alcohol_local_maximum)
