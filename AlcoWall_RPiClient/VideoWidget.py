import sys
import cv2
import time
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QImage, QPainter, QFont
from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QSizePolicy, QHBoxLayout
from PySide2.QtWidgets import QLabel, QLCDNumber
from LCDNumber import LCDNumber

class VideoWidget(QWidget):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(video_path)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setGeometry(0, 0, 1024, 600)
        self.frame_rate = 0
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
        self.timer.start(1000 // 30)
        self.text = "Blow into the alcohol sensor to start"

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame
            self.calculate_frame_rate()
            self.repaint()
        if not ret:
            self.loop_video()

    def calculate_frame_rate(self):
        current_time = time.time()
        delta = current_time - self.last_time
        if delta > 0:
            self.frame_rate = 1 / delta
        self.last_time = current_time

    def paintEvent(self, event):
        if hasattr(self, 'frame'):
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            painter = QPainter(self)
            painter.drawImage(0, 0, qt_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

            painter.setFont(QFont("Arial", 30, QFont.Bold))
            painter.setPen(Qt.white)
            painter.setOpacity(1)
            # text_rect = painter.boundingRect(self.rect(), Qt.AlignCenter, self.text)
            # painter.drawText(text_rect, Qt.AlignCenter, self.text)
            painter.end()

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

    def loop_video(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
