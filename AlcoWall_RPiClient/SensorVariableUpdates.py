from AlcoWall import AlcoWall
from PySide6.QtCore import QTimer
import json
from sensorReadout.CoinAcceptor import CoinAcceptor
alcoWall = AlcoWall()

class SensorVariableUpdates:
    def __init__(self):
        self.coin_check_timer = QTimer()
        self.coin_check_timer.timeout.connect(self.check_variable_updates)
        self.coin_check_timer.start(1000) 
        self.coinAcceptor = CoinAcceptor()
        self.coinAcceptor.run()

    def check_variable_updates(self):
        alcoWall.credit += self.coinAcceptor.credit
        self.coinAcceptor.credit = 0
        try:
            with open("testFiles/proximityCheck.txt", "r") as file:
                content = file.read().strip()
            if content != "":
                alcoWall.proximity_distance = int(content)
        except FileNotFoundError:
            pass
        try:
            with open("testFiles/alcoholCheck.txt", "r") as file:
                content = file.readlines()
                content = [line.strip() for line in content]
            if content != "" and content[0] == "yes":
                alcoWall.alcohol_level = float(content[1])
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

                    
                
