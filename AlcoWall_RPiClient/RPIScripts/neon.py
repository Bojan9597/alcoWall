from rpi_ws281x import PixelStrip, Color
import time
import random  # Needed for Twinkling Stars pattern

# LED strip configuration:
LED_COUNT = 80          # Number of LED pixels.
LED_PIN = 18            # GPIO pin connected to the pixels (must support PWM!).
BRIGHTNESS = 128        # Brightness level (0-255)

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
        time.sleep(wait_ms / 1000.0)

# Pattern 3: Color Wipe
def pattern_color_wipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time, then wipe off."""
    # Wipe on
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)
    # Wipe off
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, 0)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Pattern 4: Color Bounce
def pattern_color_bounce(strip, color, wait_ms=50):
    """Bounce color back and forth along the strip."""
    # Forward direction
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)
        strip.setPixelColor(i, 0)
    # Backward direction
    for i in range(strip.numPixels() - 1, -1, -1):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)
        strip.setPixelColor(i, 0)

# Pattern 5: Breathing Effect
def pattern_breathing(strip, color, wait_ms=20, breaths=3):
    """Create a breathing (fade in and out) effect."""
    for _ in range(breaths):
        # Fade in
        for brightness in range(0, BRIGHTNESS + 1, 5):
            strip.setBrightness(brightness)
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
        # Fade out
        for brightness in range(BRIGHTNESS, -1, -5):
            strip.setBrightness(brightness)
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
    # Reset brightness to initial value
    strip.setBrightness(BRIGHTNESS)
    strip.show()

# Existing Patterns

# Pattern 6: Circular Effect
def pattern_circular(strip, color, initial_segment_size=1, max_segment_size=80, wait_ms=50):
    """Create a circular effect with a progressively larger segment size."""
    segment_size = initial_segment_size
    while segment_size <= max_segment_size:
        for offset in range(strip.numPixels()):
            for i in range(strip.numPixels()):
                if offset <= i < offset + segment_size:
                    strip.setPixelColor(i % strip.numPixels(), color)
                else:
                    strip.setPixelColor(i, 0)
            strip.show()
            time.sleep(wait_ms / 1000.0)
        segment_size += 6  # Increase segment size for the next iteration

# Pattern 7: Turn LEDs On/Off One by One
def pattern_turn_on_off(strip, color, wait_ms=50):
    """Turn LEDs on one by one, then off one by one."""
    # Turn LEDs on one by one
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)
    # Turn LEDs off one by one
    for i in range(strip.numPixels() - 1, -1, -1):
        strip.setPixelColor(i, 0)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Pattern 8: All LEDs On
def pattern_all_on(strip, color, duration=10):
    """Turn on all LEDs with a given color and hold for the specified duration."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(duration)

# Main loop to execute the patterns in sequence
def main():
    while True:
        print("Running Pattern 0: Rainbow Cycle")
        pattern_rainbow_cycle(strip, wait_ms=20, iterations=5)

        print("Running Pattern 1: Theater Chase")
        pattern_theater_chase(strip, INDIGO, wait_ms=50, iterations=10)

        print("Running Pattern 2: Twinkling Stars")
        pattern_twinkling_stars(strip, INDIGO, star_count=10, wait_ms=100)

        print("Running Pattern 3: Color Wipe")
        pattern_color_wipe(strip, INDIGO, wait_ms=50)

        print("Running Pattern 4: Color Bounce")
        pattern_color_bounce(strip, INDIGO, wait_ms=50)

        print("Running Pattern 5: Breathing Effect")
        pattern_breathing(strip, INDIGO, wait_ms=20, breaths=3)

        print("Running Pattern 6: Circular Effect")
        pattern_circular(strip, INDIGO, initial_segment_size=1, max_segment_size=80, wait_ms=50)

        print("Running Pattern 7: Turn LEDs On/Off One by One")
        pattern_turn_on_off(strip, INDIGO, wait_ms=50)

        print("Running Pattern 8: All LEDs On")
        pattern_all_on(strip, INDIGO, duration=10)

# Entry point
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program...")
        # Turn off all LEDs before exiting
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, 0)
        strip.show()
        GPIO.cleanup()  # If using RPi.GPIO elsewhere
