from PySide6.QtGui import QColor
# Constants for magic numbers
DIGIT_COUNT = 5  # Number of digits to display (including decimal places)
WIDGET_HEIGHT = 200  # Height of the widget
WIDGET_WIDTH = 300  # Width of the widget
FONT_SIZE = 100  # Font size for the number display
LOW_THRESHOLD = 0.3  # Threshold for green color
HIGH_THRESHOLD = 0.8  # Threshold for red color
COLOR_GREEN = QColor(0, 255, 0)  # Green color for low values
COLOR_ORANGE = QColor(255, 165, 0)  # Orange color for medium values
COLOR_RED = QColor(255, 0, 0)  # Red color for high values