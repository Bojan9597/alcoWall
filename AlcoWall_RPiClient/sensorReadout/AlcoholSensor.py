import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import threading
from Constants.GENERALCONSTANTS import ALCOHOL_LEVEL_MEASUREMENT_TIME_INTERVAL

class SensorReadException(Exception):
    """Custom exception to signal sensor reading issues."""
    pass

class AlcoholSensor:
    def __init__(self):
        # Initialize I2C and ADS1115
        self._initialize_sensor()
        self.set_alcohol_level(0)
    
    def _initialize_sensor(self):
        """
        Initializes or re-initializes the I2C bus and ADS1115.
        """
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.channel = AnalogIn(self.ads, ADS.P0)

    def measure(self):
        """
        Measures the analog value and voltage from the sensor.
        Raises a SensorReadException if reading fails.
        """
        try:
            analog_value = self.channel.value
            voltage = self.channel.voltage
            self.set_alcohol_level(voltage)
            return analog_value, voltage
        except Exception as e:
            # Raise a custom exception so we can handle sensor failures gracefully
            raise SensorReadException(f"Failed to read sensor data: {e}") from e
    
    def run(self, interval=ALCOHOL_LEVEL_MEASUREMENT_TIME_INTERVAL):
        """
        Runs the measurement loop and continuously measures the sensor data.
        If a sensor read fails, waits 10 seconds, re-initializes the sensor,
        then continues reading without crashing the application.
        """
        try:
            while True:
                try:
                    analog_value, voltage = self.measure()
                    # You could log or print here, e.g.:
                    # print(f"Analog Value: {analog_value}, Voltage: {voltage}")
                except SensorReadException as e:
                    print(f"Sensor read error: {e}")
                    print("Waiting 10 seconds before attempting to reinitialize sensor.")
                    time.sleep(10)
                    self._initialize_sensor()

                time.sleep(interval)
        except KeyboardInterrupt:
            print("Measurement stopped by user.")

    def get_alcohol_level(self):
        """Returns the last measured alcohol level in a thread-safe manner."""
        with threading.Lock():
            return self.alcohol_level
        
    def set_alcohol_level(self, alcohol_level):
        """Sets the alcohol level value in a thread-safe manner."""
        with threading.Lock():
            self.alcohol_level = alcohol_level
    
    def update_alcohol_level(self):
        """
        Updates the alcohol level value (stored in self.alcohol_level).
        This function calls `measure()` and updates the class attribute.
        """
        try:
            _, voltage = self.measure()
            self.set_alcohol_level(voltage)
        except SensorReadException as e:
            # Handle or log the exception if needed
            print(f"Failed to update alcohol level: {e}")

# Main entry point of the program
if __name__ == "__main__":
    # Create an instance of the AlcoholSensor class
    sensor = AlcoholSensor()
    # Run the sensor measurement loop
    sensor.run()
