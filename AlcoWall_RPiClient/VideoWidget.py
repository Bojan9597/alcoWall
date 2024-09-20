import sys
import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPainter, QFont
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QSizePolicy, QHBoxLayout
from PySide6.QtWidgets import QLabel, QLCDNumber
import imageio
from LCDNumber import LCDNumber
from CONSTANTS import VIDEO_WIDTH, VIDEO_HEIGHT
from PySide6.QtCore import Signal

class VideoWidget(QWidget):
    video_finished = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setGeometry(0, 0, VIDEO_WIDTH, VIDEO_HEIGHT)

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
        self.text = "Blow into the alcohol sensor to start"

    def play_video(self, video_path):
        # Open the video using imageio
        self.cap = imageio.get_reader(video_path)
        self.frame_rate = self.cap.get_meta_data()['fps']
        self.timer.start(1000 // self.frame_rate)  # Targeting approximately 30 FPS

    def update_frame(self):
        try:
            frame = self.cap.get_next_data()
        except IndexError:
            # If the video has ended, reset the frame position to loop
            self.video_finished.emit()
            self.cap.set_image_index(0)  # Reset to the first frame
            frame = self.cap.get_next_data()

        self.frame = frame
        self.repaint()

    def paintEvent(self, event):
        if hasattr(self, 'frame'):
            frame_rgb = self.frame
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            painter = QPainter(self)
            painter.drawImage(0, 0, qt_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def closeEvent(self, event):
        self.cap.close()  # Properly close the video reader
        event.accept()

    def loop_video(self):
        self.cap.set_image_index(0)  # Reset to the first frame when looping
