from PySide6.QtWidgets import QLCDNumber, QApplication
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt
import sys
from ComponentsConstants.LCDNumberConstants import *

class LCDNumber(QLCDNumber):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDigitCount(DIGIT_COUNT)
        self.setFixedHeight(WIDGET_HEIGHT)
        self.setFixedWidth(WIDGET_WIDTH)
        self.setStyleSheet("border: none;")
        self.value = 0.0

        # Make the widget background transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def setValue(self, value):
        self.value = value
        self.display(f"{value:.2f}")  # Display the value with two decimal places
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        # Determine the color based on the value
        if self.value < LOW_THRESHOLD:
            color = COLOR_GREEN
        elif LOW_THRESHOLD <= self.value <= HIGH_THRESHOLD:
            color = COLOR_ORANGE
        else:
            color = COLOR_RED

        # Set the color for the text
        painter.setPen(color)

        # Adjust font size to fit the widget
        font = painter.font()
        font.setPointSize(FONT_SIZE)  # Use the constant font size
        painter.setFont(font)

        # Draw the number centered with two decimal places
        painter.drawText(rect, Qt.AlignCenter, f"{self.value:.2f}")

        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = LCDNumber()
    widget.setValue(0.55)  # Example usage
    widget.show()
    sys.exit(app.exec())