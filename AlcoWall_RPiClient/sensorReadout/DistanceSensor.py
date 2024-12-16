# import RPi.GPIO as GPIO
# import time
# import threading

# class DistanceSensor:
#     def __init__(self):
#         # Set the GPIO pins for the sensor
#         self.TRIG_PIN = 23  # Trigger pin connected to GPIO 23
#         self.ECHO_PIN = 24  # Echo pin connected to GPIO 24
#         self.distance = 0
#         # Setup
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.TRIG_PIN, GPIO.OUT)
#         GPIO.setup(self.ECHO_PIN, GPIO.IN)

#     def measure_distance(self):
#         """Measures the distance using the ultrasonic sensor."""
#         # Ensure the trigger pin is low
#         GPIO.output(self.TRIG_PIN, False)
#         time.sleep(0.1)  # Small delay to stabilize the sensor

#         # Send a short pulse to trigger the sensor
#         GPIO.output(self.TRIG_PIN, True)
#         time.sleep(0.00001)  # Pulse duration: 10 microseconds
#         GPIO.output(self.TRIG_PIN, False)

#         # Measure the duration of the echo pulse
#         pulse_start = 0
#         pulse_end = 0

#         # Wait for the echo to go high
#         while GPIO.input(self.ECHO_PIN) == 0:
#             pulse_start = time.time()

#         # Wait for the echo to go low
#         while GPIO.input(self.ECHO_PIN) == 1:
#             pulse_end = time.time()

#         # Calculate pulse duration
#         pulse_duration = pulse_end - pulse_start

#         # Calculate distance (speed of sound is approximately 343 meters per second)
#         self.set_distance(round(pulse_duration * 17150,2))

#     def get_distance(self):
#         """Returns the last measured distance."""
#         with threading.Lock():
#             return self.distance
#     def set_distance(self, distance):
#         """Sets the distance value."""
#         with threading.Lock():
#             self.distance = distance
#     def update_distance(self):
#         """Updates the distance value."""
#         self.distance = self.measure_distance()

#     def run(self, interval=1):
#         """Continuously measures and prints the distance."""
#         try:
#             while True:
#                 self.measure_distance()
#                 # print(f"Distance: {self.distance} cm")
#                 time.sleep(interval)
#         except KeyboardInterrupt:
#             print("Measurement stopped by User")
#         finally:
#             GPIO.cleanup()

# # Main entry point of the program
# if __name__ == "__main__":
#     sensor = DistanceSensor()
#     sensor.run()
