import os
from PySide6.QtCore import QTimer, Qt
from AlcoWall import AlcoWall
from States.state import State
import requests
from datetime import datetime, timedelta
from CONSTANTS import TIME_IN_ALCOHOL_CHECKED_STATE_FOR_ALCOHOL_SENSOR_COOLDOWN
from PySide6.QtGui import QFontMetrics, QFont
alcoWall = AlcoWall()

class AlcoholChecked(State):
    def __init__(self):
        """
        Initializes the AlcoholChecked state, hides unnecessary UI elements,
        and sets up a timer for transitioning back to the initial state.
        """
        alcoWall.video_widget.hide()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.show()   
        self.alcohol_checked_timer = QTimer()
        self.alcohol_checked_timer.timeout.connect(self.check_next_state)
        self.alcohol_checked_timer.start(TIME_IN_ALCOHOL_CHECKED_STATE_FOR_ALCOHOL_SENSOR_COOLDOWN * 1000)  # Check every 5 seconds
        alcoWall.workingWidget.lcdNumber.setValue(alcoWall.alcohol_level_to_show)
        alcoWall.alcohol_level_to_show = 0
        alcoWall.update_alcohol_level(-1)
        alcoWall.workingWidget.alcoholSensorText.setText("")
        alcoWall.workingWidget.proximitySensorText.setText("")
        alcoWall.workingWidget.resultLabelText.setText("Alcohol level: ")
        alcoWall.workingWidget.lcdCounter.setText("")
        alcoWall.workingWidget.alcoholSensorText.hide()
        
        # Call function to get fun fact and display it
        self.get_fun_fact()

    def get_fun_fact(self):
        """
        Fetches a fun fact from the API and displays it on the proximitySensorText widget with dynamic font size adjustment.
        If fetching fails, it will display a default fun fact.
        """
        fallback_fact = ("Tokom prohibicije u Sjedinjenim Državama, ljudi su pili \"lekovitu\" viskiju "
                        "koju su im lekari prepisivali kao način da legalno dođu do alkohola.")

        try:
            response = requests.post("https://node.alkowall.indigoingenium.ba/facts/general_fact")
            if response.status_code == 200:
                fact_data = response.json()
                
                # Check if fact_data is a list, then access the first element
                if isinstance(fact_data, list) and len(fact_data) > 0:
                    fact_sentence = fact_data[0].get("sentence", fallback_fact)
                elif isinstance(fact_data, dict):
                    fact_sentence = fact_data.get("sentence", fallback_fact)
                else:
                    fact_sentence = fallback_fact

                # Update the proximitySensorText with the received fun fact
                alcoWall.workingWidget.proximitySensorText.setWordWrap(True)  # Enable word wrap

                # Set the fun fact text with font adjustment to fit within half the label width
                self.adjust_font_size_to_fit_half_width(alcoWall.workingWidget.proximitySensorText, fact_sentence)

            else:
                # If there's an error, set the default fallback fun fact
                alcoWall.workingWidget.proximitySensorText.setText(fallback_fact)
        except requests.RequestException as e:
            # In case of network error, display the fallback fun fact
            alcoWall.workingWidget.proximitySensorText.setText(fallback_fact)

    def adjust_font_size_to_fit_half_width(self, label, text):
        """
        Adjusts the font size of the label dynamically so that the text fits within half of the label's width.
        """
        label.setText(text)
        font = label.font()
        font_metrics = QFontMetrics(font)
        
        # Start with a large font size and decrease if necessary
        font_size = 30  # Start with a default large size
        label.setFont(font)

        # Reduce the font size until the text fits within half of the label's width
        half_width = label.width() // 2
        while font_metrics.horizontalAdvance(text) > half_width or font_metrics.boundingRect(0, 0, half_width, label.height(), Qt.TextWordWrap, text).height() > label.height():
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
