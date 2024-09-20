import platform
import json
import threading
import requests
from datetime import datetime
from PySide6.QtCore import QTimer
from AlcoWall import AlcoWall
import os
from CONSTANTS import TARGET_PLATFORM_ARCHITECTURE, TARGET_PLATFORM_SYSTEM, DEVICE_ID

alcoWall = AlcoWall()

class SensorVariableUpdates:
    def __init__(self):
        self.counter = 0
        # self.coin_check_timer = QTimer()
        # self.coin_check_timer.timeout.connect(self.check_variable_updates)
        # self.coin_check_timer.start(1000)
        self.distanceSensor = None
        self.alcoholSensor = None
        self.coinAcceptor = None
        self.coin_insertions = []

        # Start a new thread to handle sensor updates and network requests
        self.thread = threading.Thread(target=self.run_sensor_updates, daemon=True)
        self.thread.start()

        # Check if the code is running on Raspberry Pi
        if platform.system() == TARGET_PLATFORM_SYSTEM and TARGET_PLATFORM_ARCHITECTURE in platform.machine():
            from sensorReadout.DistanceSensor import DistanceSensor
            self.distanceSensor = DistanceSensor()
            self.distanceSensorThread = threading.Thread(target=self.distanceSensor.run, daemon=True)
            self.distanceSensorThread.start()

            from sensorReadout.AlcoholSensor import AlcoholSensor
            self.alcoholSensor = AlcoholSensor()
            self.alcoholSensorThread = threading.Thread(target=self.alcoholSensor.run, daemon=True)
            self.alcoholSensorThread.start()

            from sensorReadout.CoinAcceptor import CoinAcceptor
            self.coinAcceptor = CoinAcceptor()
            self.coin_thread = threading.Thread(target=self.coinAcceptor.run, daemon=True)
            self.coin_thread.start()

    def run_sensor_updates(self):
        """Separate thread for checking sensor updates and sending data."""
        while True:
            self.check_variable_updates()
            threading.Event().wait(1)

    def check_variable_updates(self):
        # Handling coin acceptor
        if self.coinAcceptor:
            if self.coinAcceptor.get_credit() > 0:
                self.record_coin_insertion(self.coinAcceptor.get_credit()) 
                alcoWall.update_credit(self.coinAcceptor.get_credit())
                self.coinAcceptor.set_credit(0)
        else:
            try:
                with open("testFiles/coinInserted.txt", "r") as file:
                    content = file.read().strip()
                if content != "" and content != "0":
                    self.send_coin_insertions(float(content))
                    alcoWall.update_credit(float(content))
            except FileNotFoundError:
                pass

        # Handling other sensors
        if self.distanceSensor:
            alcoWall.update_proximity_distance(self.distanceSensor.get_distance())
        else:
            try:
                with open("testFiles/proximityCheck.txt", "r") as file:
                    content = file.read().strip()
                if content != "":
                    alcoWall.update_proximity_distance(int(content))
            except FileNotFoundError:
                pass
        if self.alcoholSensor:
            alcoWall.update_alcohol_level(self.alcoholSensor.get_alcohol_level())
        else:
            try:
                with open("testFiles/alcoholCheck.txt", "r") as file:
                    content = file.readlines()
                    content = [line.strip() for line in content]
                if content != "" and content[0] == "yes":
                    alcoWall.update_alcohol_level(float(content[1]))
            except FileNotFoundError:
                pass

        # Checking errors
        try:
            with open("jsonFiles/errors.json", "r") as file:
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
            "device_id": 1,  # Replace with actual device ID if needed
            "cash_value": credit,
            "date": datetime.now().isoformat()  # Use current timestamp
        }
        # Ensure the directory exists
        self.ensure_directory_exists("jsonFiles")

        try:
            with open("jsonFiles/coinInserted.json", "a") as json_file:
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

        with open("jsonFiles/coinInserted.json", "r") as json_file:
            for line in json_file:
                data = json.loads(line)
                # Store device_id, alcohol_level, and timestamp
                self.coin_insertions.append({
                    "device_id": DEVICE_ID,
                    "cash_value": credit,
                    "date": data["date"]
                })
        
        self.send_coin_insertions_to_database(self.coin_insertions)
                
        if os.path.exists("jsonFiles/coinInserted.json"):
            with open("jsonFiles/coinInserted.json", "w") as json_file:
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
                    print("Coin insertions sent successfully.")
                    print(self.coin_insertions)
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
        print("Coin insertions sent successfully.")
        return success
        
            # print(f"Error while sending coin insertions: {e}")
