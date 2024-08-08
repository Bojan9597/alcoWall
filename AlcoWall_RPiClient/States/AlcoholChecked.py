import os
from PySide6.QtCore import QTimer, Qt
from AlcoWall import AlcoWall
from States.state import State
import json
from datetime import datetime, timedelta
# from InitialState import InitialState

alcoWall = AlcoWall()

class AlcoholChecked(State):
    def __init__(self):
        """
        @brief Initializes the AlcoholChecked state.

        This constructor sets up the AlcoholChecked state by hiding unnecessary UI elements,
        showing the working widget, setting up a timer for state transition, and displaying the
        detected alcohol level.

        Detailed Steps:
        1. Hide the video widget to remove distractions from the alcohol check results.
        2. Hide the background image label for a clean display.
        3. Show the working widget to display the results.
        4. Initialize `alcohol_checked_timer` to a QTimer object.
        5. Connect the `timeout` signal of `alcohol_checked_timer` to the `check_next_state` method. 
           This means that `check_next_state` will be called every time the timer times out.
        6. Start the `alcohol_checked_timer` with a timeout interval of 5000 milliseconds (5 seconds).
        7. Clear the text of label1 and label2 of the working widget.
        8. Set the text of label3 to display "Alcohol level: ".
        9. Display the current alcohol level on the LCD number display of the working widget.

        This setup ensures that the alcohol level is displayed to the user for a certain period
        before transitioning back to the initial state.
        """
        alcoWall.video_widget.hide()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.show()   
        self.alcohol_checked_timer = QTimer()
        self.alcohol_checked_timer.timeout.connect(self.check_next_state)
        self.alcohol_checked_timer.start(10000)  # Check every 5 seconds
        alcoWall.workingWidget.lcdNumber.setValue(alcoWall.alcohol_level)
        alcoWall.workingWidget.alcoholSensorText.setText("")
        alcoWall.workingWidget.proximitySensorText.setText("")
        alcoWall.workingWidget.resultLabelText.setText("Alcohol level: ")
        alcoWall.workingWidget.lcdCounter.setText("")

        print("AlcoholChecked: __init__")
    
    def handle_successful(self):
        """
        @brief Handles the successful transition after displaying the alcohol level.

        This function stops the alcohol checked timer and transitions back to the InitialState.

        @return InitialState: The next state to transition to.
        """
        self.alcohol_checked_timer.stop()
        from States.InitialState import InitialState
        return InitialState()  # Transition back to InitialState

    def handle_unsuccessful(self):
        """
        @brief Handles the unsuccessful attempt to transition from the AlcoholChecked state.

        This function prints an error message indicating that the alcohol level insertion failed.
        
        @return AlcoholChecked: The current state to remain in.
        """
        print("Alcohol level insertion failed")
        return self

    def handle_error(self):
        """
        @brief Handles errors during the AlcoholChecked state.

        This function stops the alcohol checked timer and transitions back to the InitialState.

        @return InitialState: The next state to transition to.
        """
        self.alcohol_checked_timer.stop()
        from States.InitialState import InitialState
        return InitialState()

    def check_next_state(self):
        """
        @brief Checks for errors and proceeds to transition states if no errors are found.

        This function is called periodically by a timer to determine whether to transition
        to the next state or handle an error.
        """
        if self.check_errors():
            alcoWall.handle_error()
        else:
            alcoWall.handle_successful()

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
