import RPi.GPIO as GPIO
import time

# Constants
PWM_PIN = 12  # GPIO Pin 12 corresponds to physical pin 32
FREQ = 2500  # PWM Frequency in Hz (25kHz for fan control)

def setup_pwm():
    """Setup the PWM pin."""
    GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
    GPIO.setup(PWM_PIN, GPIO.OUT)  # Set pin as output
    pwm = GPIO.PWM(PWM_PIN, FREQ)  # Initialize PWM on the specified pin and frequency
    pwm.start(0)  # Start PWM with 0% duty cycle (fan off)
    return pwm

def set_fan_speed(pwm, duty_cycle):
    """Set the fan speed with the given duty cycle (0-100%)."""
    pwm.ChangeDutyCycle(duty_cycle)  # Adjust the duty cycle

def main():
    pwm = setup_pwm()
    try:
        print("Running fan at 60% speed")
        while True:  # Continuous loop
            set_fan_speed(pwm, 60)  # Set fan speed to 80%
            time.sleep(1)  # Add a delay to reduce CPU usage
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        set_fan_speed(pwm, 0)  # Turn off the fan
        pwm.stop()  # Stop PWM
        GPIO.cleanup()  # Cleanup GPIO settings

if __name__ == "__main__":
    main()
