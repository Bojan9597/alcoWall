import os
from PySide6.QtCore import QTimer, Qt, QDateTime
from AlcoWall import AlcoWall
from States.state import State
import json
from datetime import datetime
import requests
from CONSTANTS import BASE_URL, COUNTER_FOR_ALCOHOL_MEASURING, DEVICE_ID
alcoWall = AlcoWall()


class AlcoholCheck(State):
    def __init__(self):
        """
        @brief Initializes the AlcoholCheck state.
        
        This constructor sets up various timers to manage the state transitions and UI updates,
        initializes variables, and configures the user interface elements for the alcohol check process.
        """
        self.start_time = QDateTime.currentDateTime()
        alcoWall.credit -= 1

        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.check_elapsed_time)
        self.elapsed_timer.start(1000)  # Check every 1 second

        self.counterForMeasuring = COUNTER_FOR_ALCOHOL_MEASURING

        alcoWall.video_widget.hide()
        alcoWall.backgroundImageLabel.hide()
        alcoWall.workingWidget.show()

        self.alcohol_results = []

        self.check_proximity_timer = QTimer()
        self.check_proximity_timer.timeout.connect(self.check_proximity)
        self.check_proximity_timer.start(1000)  # Check every 1 second

        self.counterTimer = QTimer()
        self.counterTimer.timeout.connect(self.decreaseCounter)
        self.counterTimer.start(1000)

        # print("AlcoholCheck: __init__")
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
        alcoWall.workingWidget.play_video('videos/beer1.mp4')

    def ensure_directory_exists(self, directory):
        """
        Ensure the given directory exists. If it does not exist, create it.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def handle_successful(self):
        """
        @brief Handles the successful detection of alcohol levels.
        """
        # print("Alcohol level inserted successfully")
        # print(alcoWall.alcohol_level)
        self.write_data()
        from States.AlcoholChecked import AlcoholChecked
        return AlcoholChecked()  # Transition back to InitialState
    
    def decreaseCounter(self):
        self.counterForMeasuring -= 1
        # print(self.counterForMeasuring)
        alcoWall.workingWidget.lcdCounter.setText(str(self.counterForMeasuring))
        if self.counterForMeasuring == 0:
            self.counterTimer.stop()
            alcoWall.handle_successful()

    def handle_unsuccessful(self):
        """
        @brief Handles the unsuccessful detection of alcohol levels.
        """
        print("Alcohol level insertion failed")
        return self

    def handle_error(self):
        """
        @brief Handles errors during the alcohol check process.
        """
        from States.InitialState import InitialState
        return InitialState()

    def check_next_state(self):
        """
        @brief Checks for errors and proceeds to check the alcohol level if no errors are found.
        """
        if self.check_errors():
            alcoWall.handle_error()
        else:
            self.check_alcohol()

    def check_errors(self):
        """
        @brief Checks for any errors such as open service or coin doors, or coin stuck.
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
        """
        try:
            if self.counterForMeasuring < 1:
                if self.alcohol_local_maximum > 0.1 and not self.alcohol_local_maximum_updated:
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
        """
        timestamp = datetime.now().isoformat()
        data = {
            "device_id": alcoWall.device_id,
            "alcohol_level": alcoWall.alcohol_level,
            "datetime": timestamp
        }

        # Ensure the directory exists
        self.ensure_directory_exists("jsonFiles")

        try:
            with open("jsonFiles/alcohol_results.json", "a") as json_file:
                json.dump(data, json_file)
                json_file.write("\n")  # Write each entry on a new line
            # print("Results written to JSON file.")
        except IOError as e:
            print(f"An error occurred while writing to the JSON file: {e}")

    def write_highscore_to_file_and_update_database(self):
        """
        Writes the highscore to a JSON file. 
        1. Try to send the alcohol level to the database.
        2. If successful, try to get the highscore from the database.
        3. If successful, update the local highscore JSON file with the fetched highscore.
        4. If any step fails, update the local highscore JSON file only if the current alcohol level is higher than the saved highscore.
        """
        highscore_file = "jsonFiles/highscores.json"
        
        self.ensure_directory_exists("jsonFiles")
        highscores = self.load_existing_highscores(highscore_file)

        success = True
        self.write_results_to_json_file()
        
        # Load alcohol results
        with open("jsonFiles/alcohol_results.json", "r") as json_file:
            for line in json_file:
                data = json.loads(line)
                # Store device_id, alcohol_level, and timestamp
                alcoWall.alcohol_level = data["alcohol_level"]
                self.alcohol_results.append({
                    "device_id": DEVICE_ID,
                    "alcohol_level": data["alcohol_level"],
                    "datetime": data["datetime"]
                })
        
        # Try sending results to the database
        for result in list(self.alcohol_results):  # Use a copy to modify the list while iterating
            success = self.send_alcohol_level_to_database(result)
            if not success:
                break  # Stop sending on failure
            else:
                self.alcohol_results.remove(result)  # Remove this specific result from the list
                
        if os.path.exists("jsonFiles/alcohol_results.json"):
            with open("jsonFiles/alcohol_results.json", "w") as json_file:
                for result in self.alcohol_results:
                    json.dump(result, json_file)
                    json_file.write("\n")
    
        if success:
            database_highscore = self.get_highscore_from_database()
            if database_highscore is not None:
                self.update_highscores(highscores, database_highscore)
            else:
                self.check_and_update_local_highscore(highscores)
        else:
            print("Failed to send alcohol level to database.")
            self.check_and_update_local_highscore(highscores)

        self.update_local_highscore(highscores, highscore_file)


    def send_alcohol_level_to_database(self, result):
        """
        Sends the alcohol level to the database.
        Returns True if successful, False otherwise.
        """
        url = f"{BASE_URL}/measurements/add_measurement"
        payload = {
            "device_id": result["device_id"],
            "alcohol_percentage": result["alcohol_level"],
            "measurement_date": result["datetime"]  # Use the datetime from the result
        }

        try:
            response = requests.post(url, json=payload)
            response_data = response.json()
            if response.status_code == 201 and 'measurement_id' in response_data:
                print(f"Measurement added successfully. Measurement ID: {response_data['measurement_id']}")
                return True
            elif 'error' in response_data:
                print(f"Error in measurement submission: {response_data['error']}")
                return False
            else:
                print(f"Failed to send alcohol level to the database. Status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"Request to send alcohol level failed: {e}")
            return False


    def get_highscore_from_database(self):
        """
        Tries to retrieve the highscore from the database.
        Returns the highscore value if successful, None otherwise.
        """
        url = f"{BASE_URL}/measurements/highscore_global"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                highscores = response.json()
                if highscores:
                    return float(highscores[0]["alcohol_percentage"])
            return None
        except requests.RequestException as e:
            print(f"Error retrieving highscore from the database: {e}")
            return None

    def load_existing_highscores(self, highscore_file):
        """
        Loads the existing highscores from the local JSON file, or initializes a new structure if not found.
        """
        highscores = {
            "weekly_highscore": 0.0,
            "monthly_highscore": 0.0,
            "highscore": 0.0,
            "last_updated_week": datetime.now().isocalendar()[1],
            "last_updated_month": datetime.now().month
        }

        if os.path.exists(highscore_file):
            try:
                with open(highscore_file, "r") as file:
                    highscores = json.load(file)
            except IOError as e:
                print(f"An error occurred while reading the highscore file: {e}")
        
        return highscores

    def check_and_update_local_highscore(self, highscores):
        """
        Updates the highscores if the current alcohol level is higher than the locally stored highscore.
        """
        if alcoWall.alcohol_level > highscores["weekly_highscore"]:
            highscores["weekly_highscore"] = alcoWall.alcohol_level
            alcoWall.weekly_highscore = alcoWall.alcohol_level

        if alcoWall.alcohol_level > highscores["monthly_highscore"]:
            highscores["monthly_highscore"] = alcoWall.alcohol_level
            alcoWall.monthly_highscore = alcoWall.alcohol_level

        if alcoWall.alcohol_level > highscores["highscore"]:
            highscores["highscore"] = alcoWall.alcohol_level
            alcoWall.highscore = alcoWall.alcohol_level

    def update_highscores(self, highscores, database_highscore):
        """
        Updates the highscores dictionary based on the database highscore.
        """
        current_week = datetime.now().isocalendar()[1]
        current_month = datetime.now().month

        # Reset weekly or monthly highscore if the period has changed
        if highscores["last_updated_week"] != current_week:
            highscores["weekly_highscore"] = 0.0
            highscores["last_updated_week"] = current_week

        if highscores["last_updated_month"] != current_month:
            highscores["monthly_highscore"] = 0.0
            highscores["last_updated_month"] = current_month

        # Update highscores if the database highscore is higher
        if database_highscore > highscores["weekly_highscore"]:
            highscores["weekly_highscore"] = database_highscore
            alcoWall.weekly_highscore = database_highscore

        if database_highscore > highscores["monthly_highscore"]:
            highscores["monthly_highscore"] = database_highscore
            alcoWall.monthly_highscore = database_highscore

        if database_highscore > highscores["highscore"]:
            highscores["highscore"] = database_highscore
            alcoWall.highscore = database_highscore

    def update_local_highscore(self, highscores, highscore_file):
        """
        Updates the local JSON file with the provided highscores.
        """
        try:
            with open(highscore_file, "w") as file:
                json.dump(highscores, file, indent=4)
            # print("Highscores updated and saved to local file.")
        except IOError as e:
            print(f"An error occurred while writing the highscore file: {e}")

    def ensure_directory_exists(self, directory):
        """
        Ensures that the directory exists, creates it if it doesn't.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def ensure_directory_exists(self, directory):
        """
        Ensures that the directory exists, creates it if it doesn't.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def write_data(self):
        """
        @brief Writes data to the highscore file, JSON file, and database.
        """
        self.write_highscore_to_file_and_update_database()

    def check_elapsed_time(self):
        """
        @brief Checks the elapsed time since the start of the alcohol check.
        """
        elapsed = self.start_time.secsTo(QDateTime.currentDateTime())
        if elapsed >= 20:  # 20 seconds
            alcoWall.handle_error()

    def check_local_maximum(self):
        """
        @brief Checks and updates the local maximum alcohol level detected.
        """
        if alcoWall.alcohol_level > self.alcohol_local_maximum:
            self.alcohol_local_maximum = max(self.alcohol_local_maximum, alcoWall.alcohol_level)
            self.alcohol_local_maximum_updated = True
        else:
            self.alcohol_local_maximum_updated = False
        alcoWall.workingWidget.lcdNumber.setValue(self.alcohol_local_maximum)
