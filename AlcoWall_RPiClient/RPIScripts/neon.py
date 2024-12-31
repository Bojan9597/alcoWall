from rpi_ws281x import PixelStrip, Color
import time

# LED strip configuration:
LED_COUNT = 80      # Number of LED pixels.
LED_PIN = 18        # GPIO pin connected to the pixels (must support PWM!).

# Create PixelStrip object:
strip = PixelStrip(LED_COUNT, LED_PIN)
strip.begin()

# Define colors
INDIGO = Color(31, 9, 84)  # Indigo color (adjust as needed)

# Pattern 1: Turn on all LEDs with indigo color
def pattern_all_on(strip, color, duration=10):
    """Turn on all LEDs with a given color and hold for the specified duration."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(duration)

# Pattern 2: Turn LEDs on and off one by one
def pattern_turn_on_off(strip, color, wait_ms=50):
    """Turn LEDs on one by one, then off one by one."""
    # Turn LEDs on one by one
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

    # Turn LEDs off one by one
    for i in range(strip.numPixels() - 1, -1, -1):
        strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Pattern 3: Create a circular effect
def pattern_circular(strip, color, initial_segment_size=1, max_segment_size=80, wait_ms=50):
    """Create a circular effect with a progressively larger segment size."""
    segment_size = initial_segment_size
    while segment_size <= max_segment_size:
        for offset in range(strip.numPixels()):
            for i in range(strip.numPixels()):
                if i >= offset and i < offset + segment_size:
                    strip.setPixelColor(i % strip.numPixels(), color)
                else:
                    strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
            time.sleep(wait_ms / 1000.0)
        segment_size += 2  # Increase segment size for the next iteration

# Main loop to execute the patterns in sequence
def main():
    while True:
        print("Running Pattern 3: Circular Effect")
        pattern_circular(strip, INDIGO, initial_segment_size=1, max_segment_size=80, wait_ms=50)

        print("Running Pattern 2: Turn LEDs On/Off One by One")
        pattern_turn_on_off(strip, INDIGO, wait_ms=50)

        print("Running Pattern 1: All LEDs On")
        pattern_all_on(strip, INDIGO, duration=10)

if __name__ == "__main__":
    main()
