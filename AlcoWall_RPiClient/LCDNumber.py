from PySide6.QtWidgets import QLCDNumber, QApplication
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt
import sys

class LCDNumber(QLCDNumber):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDigitCount(5)  # Adjust the number of digits as needed (including decimal point and two decimals)
        self.setFixedHeight(200)
        self.setFixedWidth(300)
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
        if self.value < 0.3:
            color = QColor(0, 255, 0)  # Green
        elif 0.3 <= self.value <= 0.8:
            color = QColor(255, 165, 0)  # Orange
        else:
            color = QColor(255, 0, 0)  # Red

        # Set the color for the text
        painter.setPen(color)

        # Adjust font size to fit the widget
        font = painter.font()
        font.setPointSize(100)  # Adjust this size to fit the display area
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
