# AlcoholChecked.py

import os
from PySide6.QtCore import QTimer, Qt
from Components.AlcoWall import AlcoWall
from States.state import State
from datetime import datetime, timedelta
from Constants.GENERALCONSTANTS import TIME_IN_ALCOHOL_CHECKED_STATE_FOR_ALCOHOL_SENSOR_COOLDOWN, DEVICE_ID
from PySide6.QtGui import QFontMetrics, QFont
from DatabaseManagement.DataManager import DataManager  # Import DataManager

alcoWall = AlcoWall()

class AlcoholChecked(State):
    def __init__(self):
        """
        Initializes the AlcoholChecked state, hides unnecessary UI elements,
        and sets up a timer for transitioning back to the initial state.
        """
        self.change_current_state_file()
        alcoWall.video_widget.hide()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.show()
        self.alcohol_checked_timer = QTimer()
        self.alcohol_checked_timer.timeout.connect(self.check_next_state)
        self.alcohol_checked_timer.start(TIME_IN_ALCOHOL_CHECKED_STATE_FOR_ALCOHOL_SENSOR_COOLDOWN * 1000)  # Convert seconds to milliseconds
        alcoWall.workingWidget.lcdNumber.setValue(alcoWall.alcohol_level_to_show)
        alcoWall.alcohol_level_to_show = 0
        alcoWall.update_alcohol_level(-1)
        alcoWall.workingWidget.alcoholSensorText.setText("")
        alcoWall.workingWidget.resultLabelText.setText("Alcohol level: ")
        alcoWall.workingWidget.lcdCounter.setText("")
        alcoWall.workingWidget.alcoholSensorText.hide()

        # Create an instance of DataManager
        self.data_manager = DataManager(DEVICE_ID)
        # Call function to get fun fact and display it
        self.get_fun_fact()
        alcoWall.next_add_url = self.data_manager.get_ad_url()
    
    def change_current_state_file(self):
        try:
            with open ("States/current_state.txt", "w") as file:
                file.write("AlcoholChecked")
        except FileNotFoundError:
            pass
    def get_fun_fact(self):
        """
        Fetches a fun fact using DataManager and displays it on the funFactText widget with dynamic font size adjustment.
        """
        fact_sentence = self.data_manager.get_fun_fact()
        alcoWall.workingWidget.funFactText.setWordWrap(True)  # Enable word wrap

        # Set the fun fact text with font adjustment to fit within half the label width
        self.adjust_font_size_to_fit_half_width(alcoWall.workingWidget.funFactText, fact_sentence)

    def adjust_font_size_to_fit_half_width(self, label, text):
        """
        Adjusts the font size of the label dynamically so that the text fits within half of the label's width.
        """
        label.setText(text)
        font = label.font()
        font_size = 30  # Start with a default large size
        font.setPointSize(font_size)
        label.setFont(font)
        font_metrics = QFontMetrics(font)

        # Reduce the font size until the text fits within half of the label's width
        half_width = label.width() // 2
        while (font_metrics.horizontalAdvance(text) > half_width or
               font_metrics.boundingRect(0, 0, half_width, label.height(), Qt.TextWordWrap, text).height() > label.height()) and font_size > 5:
            font_size -= 1
            font.setPointSize(font_size)
            label.setFont(font)
            font_metrics = QFontMetrics(font)

        # Set the final adjusted font
        label.setFont(font)

    def handle_successful(self):
        """
        Handles the successful transition after displaying the alcohol level.
        """
        self.alcohol_checked_timer.stop()
        from States.InitialState import InitialState
        return InitialState()  # Transition back to InitialState

    def handle_unsuccessful(self):
        """
        Handles the unsuccessful attempt to transition from the AlcoholChecked state.
        """
        print("Alcohol level insertion failed")
        return self

    def handle_error(self):
        """
        Handles errors during the AlcoholChecked state.
        """
        self.alcohol_checked_timer.stop()
        from States.InitialState import InitialState
        return InitialState()

    def check_next_state(self):
        """
        Checks for errors and proceeds to transition states if no errors are found.
        """
        if self.check_errors():
            alcoWall.handle_error()
        else:
            alcoWall.handle_successful()

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
