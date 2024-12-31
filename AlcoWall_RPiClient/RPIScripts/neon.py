from rpi_ws281x import PixelStrip, Color
import time

# LED strip configuration:
LED_COUNT = 80      # Number of LED pixels.
LED_PIN = 18        # GPIO pin connected to the pixels (must support PWM!).
BRIGHTNESS = 128    # Brightness level (0-255)

# Create PixelStrip object:
strip = PixelStrip(LED_COUNT, LED_PIN)
strip.setBrightness(BRIGHTNESS)  # Set initial brightness
strip.begin()

# Define colors
INDIGO = Color(31, 9, 84)  # Indigo color (adjust as needed)

# Helper function: Color wheel
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

# Pattern 0: Rainbow Cycle
def pattern_rainbow_cycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow colors that uniformly wrap around the strip."""
    for j in range(256 * iterations):  # Iterations define how many full cycles to run
        for i in range(strip.numPixels()):
            pixel_index = (i * 256 // strip.numPixels()) + j
            strip.setPixelColor(i, wheel(pixel_index & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Pattern 1: Theater Chase
def pattern_theater_chase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

# Pattern 2: Twinkling Stars
def pattern_twinkling_stars(strip, color, star_count=10, wait_ms=100):
    """Create a twinkling stars effect."""
    for _ in range(star_count):
        # Pick random pixels to light up
        star_pixels = [random.randint(0, strip.numPixels() - 1) for _ in range(star_count)]
        for i in star_pixels:
            strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)
        for i in star_pixels:
            strip.setPixelColor(i, 0)
        strip.show()

# Existing Patterns (already in your code)

# Pattern 3: Turn on all LEDs with indigo color
def pattern_all_on(strip, color, duration=10):
    """Turn on all LEDs with a given color and hold for the specified duration."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(duration)

# Pattern 4: Turn LEDs on and off one by one
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

# Pattern 5: Create a circular effect
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
        segment_size += 6  # Increase segment size for the next iteration

# Main loop to execute the patterns in sequence
def main():
    while True:
        print("Running Pattern 0: Rainbow Cycle")
        pattern_rainbow_cycle(strip, wait_ms=20, iterations=5)

        print("Running Pattern 1: Theater Chase")
        pattern_theater_chase(strip, INDIGO, wait_ms=50, iterations=10)

        print("Running Pattern 2: Twinkling Stars")
        pattern_twinkling_stars(strip, INDIGO, star_count=10, wait_ms=100)

        print("Running Pattern 3: Circular Effect")
        pattern_circular(strip, INDIGO, initial_segment_size=1, max_segment_size=80, wait_ms=50)

        print("Running Pattern 4: Turn LEDs On/Off One by One")
        pattern_turn_on_off(strip, INDIGO, wait_ms=50)

        print("Running Pattern 5: All LEDs On")
        pattern_all_on(strip, INDIGO, duration=10)

if __name__ == "__main__":
    main()
