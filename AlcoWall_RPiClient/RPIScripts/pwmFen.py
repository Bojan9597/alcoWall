import pigpio
import time

# Constants
PWM_PIN = 13  # GPIO33 in BCM mode
FREQ = 25000  # PWM frequency (25kHz is standard for fans)

def setup_pwm(pi, pin, freq):
    """Setup the PWM on the given pin with the specified frequency."""
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.set_PWM_frequency(pin, freq)
    print(f"Initialized PWM on GPIO{pin} at {freq} Hz.")

def set_fan_speed(pi, pin, duty_cycle):
    """Set the fan speed with the given duty cycle (0-100%)."""
    pwm_value = int(duty_cycle * 255 / 100)  # Convert duty cycle to range 0-255
    pi.set_PWM_dutycycle(pin, pwm_value)  # Set PWM duty cycle
    print(f"Set fan speed to {duty_cycle}% (PWM value: {pwm_value}).")

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Failed to connect to pigpio daemon.")
        return

    try:
        setup_pwm(pi, PWM_PIN, FREQ)

        print("Setting fan to half speed (50%)")
        set_fan_speed(pi, PWM_PIN, 50)  # Half speed
        time.sleep(10)

        print("Setting fan to full speed (100%)")
        set_fan_speed(pi, PWM_PIN, 100)  # Full speed
        time.sleep(10)

        print("Turning off the fan")
        set_fan_speed(pi, PWM_PIN, 0)  # Turn off
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        set_fan_speed(pi, PWM_PIN, 0)  # Ensure fan is off
        pi.stop()

if __name__ == "__main__":
    main()
