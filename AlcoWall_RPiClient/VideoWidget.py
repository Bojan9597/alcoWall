import sys
import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPainter, QFont
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QSizePolicy, QHBoxLayout
from PySide6.QtWidgets import QLabel, QLCDNumber
import imageio
from LCDNumber import LCDNumber

class VideoWidget(QWidget):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)

        # Open the video using imageio
        self.cap = imageio.get_reader(video_path)
        self.frame_rate = self.cap.get_meta_data()['fps']
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setGeometry(0, 0, 1024, 600)

        self.last_time = time.time()

        self.alcoholSensorText = QLabel("g")
        self.alcoholSensorText.setStyleSheet("color: white; font-size: 40px;")
        self.proximitySensorText = QLabel()
        self.proximitySensorText.setStyleSheet("color: white; font-size: 40px;")
        self.resultLabelText = QLabel()
        self.resultLabelText.setStyleSheet("color: white; font-size: 40px;")
        self.lcdCounter = QLabel()
        self.lcdCounter.setStyleSheet("color: white; font-size: 80px;")
        self.lcdCounter.setAlignment(Qt.AlignRight)
        
        self.lcdNumber = LCDNumber()
        self.lcdNumber.setStyleSheet("border: none;")
        
        self.widget = QWidget()
        layout1 = QHBoxLayout()
        layout1.addWidget(self.lcdNumber)
        layout1.addWidget(self.lcdCounter)
        self.widget.setLayout(layout1)

        layout = QVBoxLayout()
        layout.addWidget(self.alcoholSensorText)
        layout.addWidget(self.proximitySensorText)
        layout.addWidget(self.resultLabelText)
        layout.addWidget(self.widget)
        
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // 30)  # Targeting approximately 30 FPS
        self.text = "Blow into the alcohol sensor to start"

    def update_frame(self):
        try:
            frame = self.cap.get_next_data()
        except IndexError:
            # If the video has ended, reset the frame position to loop
            self.cap.set_image_index(0)  # Reset to the first frame
            frame = self.cap.get_next_data()

        self.frame = frame
        self.calculate_frame_rate()
        self.repaint()

    def calculate_frame_rate(self):
        current_time = time.time()
        delta = current_time - self.last_time
        if delta > 0:
            self.frame_rate = 1 / delta
        self.last_time = current_time

    def paintEvent(self, event):
        if hasattr(self, 'frame'):
            frame_rgb = self.frame
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            painter = QPainter(self)
            painter.drawImage(0, 0, qt_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

            painter.setFont(QFont("Arial", 30, QFont.Bold))
            painter.setPen(Qt.white)
            painter.setOpacity(1)
            painter.end()

    def closeEvent(self, event):
        self.cap.close()  # Properly close the video reader
        event.accept()

    def loop_video(self):
        self.cap.set_image_index(0)  # Reset to the first frame when looping
