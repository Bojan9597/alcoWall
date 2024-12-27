# AlcoholCheck.py

import os
from PySide6.QtCore import QTimer, Qt, QDateTime
from Components.AlcoWall import AlcoWall
from States.state import State
from datetime import datetime
from Constants.GENERALCONSTANTS import COUNTER_FOR_ALCOHOL_MEASURING, DEVICE_ID, ALCOHOL_LEVEL_ALLOWED_ERROR, ERROR_TO_MUCH_TIME_IN_ALCOHOL_CHECK
from DatabaseManagement.DataManager import DataManager  # Import the DataManager

alcoWall = AlcoWall()

class AlcoholCheck(State):
    def __init__(self):
        """
        Initializes the AlcoholCheck state.
        """
        alcoWall.workingWidget.funFactText.setText("")
        self.change_current_state_file()

        self.start_time = QDateTime.currentDateTime()
        alcoWall.update_credit(-100)

        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.check_elapsed_time)
        self.elapsed_timer.start(1000)  # Check every 1 second

        self.counterForMeasuring = COUNTER_FOR_ALCOHOL_MEASURING

        alcoWall.video_widget.hide()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.show()

        self.counterTimer = QTimer()
        self.counterTimer.timeout.connect(self.decreaseCounter)
        self.counterTimer.start(1000)

        alcoWall.workingWidget.alcoholSensorText.hide()

        alcoWall.workingWidget.alcoholSensorText.setText("Blow into the alcohol \n sensor until the beep")
        alcoWall.workingWidget.resultLabelText.setText("Alcohol level: ")
        alcoWall.workingWidget.lcdNumber.setValue(0)
        alcoWall.workingWidget.lcdCounter.setText(str(self.counterForMeasuring))

        self.alcohol_local_starting_value = alcoWall.get_alcohol_level()
        self.alcohol_local_maximum = alcoWall.get_alcohol_level()
        self.alcohol_local_maximum_updated = False

        self.alcohol_local_maximum_timer = QTimer()
        self.alcohol_local_maximum_timer.timeout.connect(self.check_local_maximum)
        self.alcohol_local_maximum_timer.start(300)  # Check every 300 milliseconds
        alcoWall.workingWidget.play_video('Media/videos/beer1.mp4')

        # Create an instance of DataManager
        self.data_manager = DataManager(DEVICE_ID)
    
    def change_current_state_file(self):
        try:
            with open ("States/current_state.txt", "w") as file:
                file.write("AlcoholCheck")
        except FileNotFoundError:
            pass

    def handle_successful(self):
        """
        Handles the successful detection of alcohol levels.
        """
        from States.AlcoholChecked import AlcoholChecked
        return AlcoholChecked()  # Transition to AlcoholChecked state

    def decreaseCounter(self):
        self.counterForMeasuring -= 1
        alcoWall.workingWidget.lcdCounter.setText(str(self.counterForMeasuring))
        if self.counterForMeasuring == 0:
            self.counterTimer.stop()
            alcoWall.handle_successful()

    def handle_unsuccessful(self):
        """
        Handles the unsuccessful detection of alcohol levels.
        """
        print("Alcohol level insertion failed")
        return self

    def handle_error(self):
        """
        Handles errors during the alcohol check process.
        """
        from States.InitialState import InitialState
        return InitialState()

    def check_next_state(self):
        """
        Checks for errors and proceeds to check the alcohol level if no errors are found.
        """
        if self.check_errors():
            alcoWall.handle_error()
        else:
            self.check_alcohol()

    def check_errors(self):
        """
        Checks for any errors such as open service or coin doors, or coin stuck.
        """
        try:
            if alcoWall.service_door_open or alcoWall.coins_door_open or alcoWall.coin_stuck:
                return True
            else:
                return False
        except FileNotFoundError:
            return True

    def check_alcohol(self):
        """
        Checks the alcohol level and transitions if the level is sufficient or enough time has passed.
        """
        try:
            if self.counterForMeasuring < 1:
                if alcoWall.alcohol_level_to_show > 0.1 and not self.alcohol_local_maximum_updated:
                    alcoWall.handle_successful()
                elif alcoWall.alcohol_level_to_show <= 0.1:
                    alcoWall.handle_successful()
            else:
                alcoWall.workingWidget.alcoholSensorText.setText("Blow into the alcohol \n sensor until the beep")
        except FileNotFoundError:
            pass

    def check_elapsed_time(self):
        """
        Checks the elapsed time since the start of the alcohol check.
        """
        elapsed = self.start_time.secsTo(QDateTime.currentDateTime())
        if elapsed >= ERROR_TO_MUCH_TIME_IN_ALCOHOL_CHECK:  # 20 seconds
            alcoWall.handle_error()

    def check_local_maximum(self):
        """
        Checks and updates the local maximum alcohol level detected.
        """
        current_alcohol_level = alcoWall.get_alcohol_level()
        if current_alcohol_level > self.alcohol_local_maximum:
            self.alcohol_local_maximum = current_alcohol_level
            self.alcohol_local_maximum_updated = True
        else:
            self.alcohol_local_maximum_updated = False

        if self.alcohol_local_maximum - self.alcohol_local_starting_value > ALCOHOL_LEVEL_ALLOWED_ERROR:
            alcoWall.alcohol_level_to_show = self.alcohol_local_maximum - self.alcohol_local_starting_value

        alcoWall.workingWidget.lcdNumber.setValue(alcoWall.alcohol_level_to_show)
