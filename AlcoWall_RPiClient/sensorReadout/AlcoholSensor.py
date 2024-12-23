import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import threading
from Constants.GENERALCONSTANTS import ALCOHOL_LEVEL_MEASUREMENT_TIME_INTERVAL

class AlcoholSensor:
    def __init__(self):

        # Initialize I2C and ADS1115
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        # Define the analog input channel
        self.channel = AnalogIn(self.ads, ADS.P0)
        self.set_alcohol_level(0)
    
    def measure(self):
        """Measures the analog value and voltage from the sensor."""
        analog_value = self.channel.value
        voltage = self.channel.voltage
        self.set_alcohol_level(voltage)
        return analog_value, voltage
    
    def run(self, interval=ALCOHOL_LEVEL_MEASUREMENT_TIME_INTERVAL):
        """Runs the measurement loop and prints values continuously."""
        try:
            while True:
                self.measure()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Measurement stopped by user.")

    def get_alcohol_level(self):
        """Returns the last measured alcohol level."""
        with threading.Lock():
            return self.alcohol_level
        
    def set_alcohol_level(self, alcohol_level):
        """Sets the alcohol level value."""
        with threading.Lock():
            self.alcohol_level = alcohol_level
    
    def update_alcohol_level(self):
        """Updates the alcohol level value."""
        self.alcohol_level = self.measure()

# Main entry point of the program
if __name__ == "__main__":
    
    # Create an instance of the AlcoholSensor class
    sensor = AlcoholSensor()
    
    # Run the sensor measurement in a loop
    sensor.run()
