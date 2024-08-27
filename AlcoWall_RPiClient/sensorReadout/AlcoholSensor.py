import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class AlcoholSensor:
    def __init__(self):

        # Initialize I2C and ADS1115
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        # Define the analog input channel
        self.channel = AnalogIn(self.ads, ADS.P0)
        self.alcohol_level = 0
    
    def measure(self):
        """Measures the analog value and voltage from the sensor."""
        analog_value = self.channel.value
        voltage = self.channel.voltage
        return analog_value, voltage
    
    def run(self, interval=0.2):
        """Runs the measurement loop and prints values continuously."""
        try:
            while True:
                analog_value, voltage = self.measure()
                self.alcohol_level = voltage
                print(f"Analog Value: {analog_value}, Voltage: {voltage:.3f}V")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Measurement stopped by user.")

# Main entry point of the program
if __name__ == "__main__":
    
    # Create an instance of the AlcoholSensor class
    sensor = AlcoholSensor()
    
    # Run the sensor measurement in a loop
    sensor.run()
