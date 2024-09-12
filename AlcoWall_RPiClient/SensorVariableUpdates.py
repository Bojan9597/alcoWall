from AlcoWall import AlcoWall
from PySide6.QtCore import QTimer
import json
import platform
import threading

alcoWall = AlcoWall()

class SensorVariableUpdates:
    def __init__(self):
        self.coin_check_timer = QTimer()
        self.coin_check_timer.timeout.connect(self.check_variable_updates)
        self.coin_check_timer.start(1000)
        self.distanceSensor = None
        self.alcoholSensor = None
        self.coinAcceptor = None

        # Check if the code is running on Raspberry Pi
        print(platform.machine())
        if platform.system() == "Linux" and "aarch644" in platform.machine():
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
        else:
            self.coinAcceptor = None

    def check_variable_updates(self):
        # If running on Raspberry Pi, use CoinAcceptor
        if self.coinAcceptor:
            alcoWall.credit += self.coinAcceptor.credit
            self.coinAcceptor.credit = 0
        else:
            # If not running on Raspberry Pi, read from the file
            try:
                with open("testFiles/coinInserted.txt", "r") as file:
                    content = file.read().strip()
                if content != "":
                    alcoWall.credit += float(content)  # Assuming the file contains credit amount
            except FileNotFoundError:
                pass
        if self.distanceSensor:
            alcoWall.proximity_distance = self.distanceSensor.distance
        else:
            try:
                with open("testFiles/proximityCheck.txt", "r") as file:
                    content = file.read().strip()
                if content != "":
                    alcoWall.proximity_distance = int(content)
            except FileNotFoundError:
                pass
        if self.alcoholSensor:
            alcoWall.alcohol_level = self.alcoholSensor.alcohol_level
        else:
            try:
                with open("testFiles/alcoholCheck.txt", "r") as file:
                    content = file.readlines()
                    content = [line.strip() for line in content]
                if content != "" and content[0] == "yes":
                    alcoWall.alcohol_level = float(content[1])
                    print(f"Alcohol level: {alcoWall.alcohol_level}")
            except FileNotFoundError:
                pass

        try:
            with open("jsonFiles/errors.json", "r") as file:
                error_data = json.load(file)
                alcoWall.service_door_open = error_data["service_door_open"]
                alcoWall.coins_door_open = error_data["coins_door_open"]
                alcoWall.coin_stuck = error_data["coin_stuck"]
        except FileNotFoundError:
            pass

