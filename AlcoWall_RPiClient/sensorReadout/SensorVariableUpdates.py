import platform
import json
import threading
import requests
from datetime import datetime
from PySide6.QtCore import QTimer
from Components.AlcoWall import AlcoWall
import os
from Constants.GENERALCONSTANTS import TARGET_PLATFORM_ARCHITECTURE, TARGET_PLATFORM_SYSTEM, DEVICE_ID
from PySide6.QtCore import Slot
from PySide6.QtCore import QObject
alcoWall = AlcoWall()

class SensorVariableUpdates(QObject):
    def __init__(self):
        self.alcoholSensor = None
        self.coin_insertions = []

        # Start a new thread to handle sensor updates and network requests
        self.thread = threading.Thread(target=self.run_sensor_updates, daemon=True)
        self.thread.start()

        # Check if the code is running on Raspberry Pi
        if platform.system() == TARGET_PLATFORM_SYSTEM and TARGET_PLATFORM_ARCHITECTURE in platform.machine():
            from sensorReadout.AlcoholSensor import AlcoholSensor
            self.alcoholSensor = AlcoholSensor()
            self.alcoholSensorThread = threading.Thread(target=self.alcoholSensor.run, daemon=True)
            self.alcoholSensorThread.start()

            from sensorReadout.CoinAcceptor_New import CoinAcceptor
            self.coinAcceptor = CoinAcceptor()
            self.coin_thread = threading.Thread(target=self.coinAcceptor.get_coin_type, daemon=True)
            self.coin_thread.start()

    def run_sensor_updates(self):
        while True:
            self.check_variable_updates()
            threading.Event().wait(1)
    
    @Slot(int)
    def update_credit(self, credit):
            alcoWall.update_credit(credit)

    def check_variable_updates(self):
        if self.coinAcceptor and self.coinAcceptor.get_credit() > 0:
            alcoWall.update_credit(self.coinAcceptor.get_credit())
            print(f"Credit: {alcoWall.get_credit()}")
            self.coinAcceptor.set_credit(0)

        if self.alcoholSensor:
            alcoWall.update_alcohol_level(self.alcoholSensor.get_alcohol_level())

        # Checking errors
        try:
            with open("DatabaseManagement/jsonFiles/errors.json", "r") as file:
                error_data = json.load(file)
                alcoWall.service_door_open = error_data["service_door_open"]
                alcoWall.coins_door_open = error_data["coins_door_open"]
                alcoWall.coin_stuck = error_data["coin_stuck"]
        except FileNotFoundError:
            pass
    
    def write_credit_to_json_file(self, credit):
        """
        @brief Writes the results of the alcohol check to a JSON file.
        """
        data = {
            "device_id": alcoWall.device_id,  # Replace with actual device ID if needed
            "cash_value": credit,
            "date": datetime.now().isoformat()  # Use current timestamp
        }
        # Ensure the directory exists
        self.ensure_directory_exists("jsonFiles")

        try:
            with open("DatabaseManagement/jsonFiles/coinInserted.json", "a") as json_file:
                json.dump(data, json_file)
                json_file.write("\n")  # Write each entry on a new line
        except IOError as e:
            print(f"An error occurred while writing to the JSON file: {e}")
    
    def ensure_directory_exists(self, directory):
        """
        Ensure the given directory exists. If it does not exist, create it.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def send_coin_insertions(self, credit):
        """Try sending the coin insertions to the server."""
        self.coin_insertions.clear()
        self.write_credit_to_json_file(float(credit))

        with open("DatabaseManagement/jsonFiles/coinInserted.json", "r") as json_file:
            for line in json_file:
                data = json.loads(line)
                # Store device_id, alcohol_level, and timestamp
                self.coin_insertions.append({
                    "device_id": alcoWall.device_id,
                    "cash_value": credit,
                    "date": data["date"]
                })
        
        self.send_coin_insertions_to_database(self.coin_insertions)
                
        if os.path.exists("DatabaseManagement/jsonFiles/coinInserted.json"):
            with open("DatabaseManagement/jsonFiles/coinInserted.json", "w") as json_file:
                for credit in self.coin_insertions:
                    json.dump(credit, json_file)
                    json_file.write("\n")
        

    def send_coin_insertions_to_database(self, credit):
        success = False
        try:
            response = requests.post("https://node.alkowall.indigoingenium.ba/cash/add_cash_multiple", json=self.coin_insertions)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("message") == "Cash status updated successfully for multiple devices.":
                    success = True
                    self.coin_insertions.clear()  # Clear the list after successful sending

                else:
                    print(f"Unexpected response from the server: {response_data}")
                    success = False
            else:
                print(f"Failed to send coin insertions. Status code: {response.status_code}")
                success = False
        except requests.RequestException as e:
            success = False
            return success
        return success
        
            # print(f"Error while sending coin insertions: {e}")
