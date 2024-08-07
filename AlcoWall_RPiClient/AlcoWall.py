from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QUrl, Qt, QTimer
from PySide2.QtMultimediaWidgets import QVideoWidget
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtGui import QPixmap
from VideoWidget import VideoWidget

class AlcoWall(QWidget):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        super().__init__()
        self.credit = 0
        self.weekly_highscore = 0
        self.monthly_highscore = 0
        self.highscore = 0
        self.device_id = "alcoWall_01"

        self.credit = 0
        self.alcohol_level = -1
        self.proximity_distance = -1

        self.service_door_open = False
        self.coins_door_open = False
        self.coin_stuck = False
        
        # Load the UI file
        loader = QUiLoader()
        file = QFile("UIFiles/VideoWidget.ui")
        if not file.open(QFile.ReadOnly):
            print(f"Cannot open {file.fileName()}: {file.errorString()}")
            exit(-1)
        self.ui = loader.load(file, self)
        file.close()
        
        video_container = self.ui.findChild(QWidget, "videoContainer")
        self.backgroundImageLabel = self.ui.findChild(QLabel, "backgroundImageLabel")
        self.video_widget = QVideoWidget(video_container)
        self.set_background_image(self.backgroundImageLabel, 'images/breathalyzerImage.jpg')

        self.main_videos_widget = self.ui.findChild(QWidget, "backgroundContainer")
        self.workingWidget = VideoWidget('videos/beer1.mp4', self)
        self.main_videos_widget.layout().addWidget(self.workingWidget)


        self.video_widget = VideoWidget('videos/AI.mp4', self)
        self.video_widget.alcoholSensorText.hide()
        self.video_widget.proximitySensorText.hide()
        self.video_widget.resultLabelText.hide()
        self.video_widget.lcdCounter.hide()
        self.video_widget.lcdNumber.hide()
        self.main_videos_widget.layout().addWidget(self.video_widget)

        self.backgroundImageLabel.hide()
        self.video_widget.show()

        self._initialized = True
        self.current_state = None

    def set_background_image(self, widget, image_path):
        pixmap = QPixmap(image_path)
        widget.setPixmap(pixmap)
        widget.setScaledContents(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.backgroundImageLabel.hide()
            self.video_widget.show()
        elif event.key() == Qt.Key_B:
            self.video_widget.hide()
            self.backgroundImageLabel.show()

    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
        if status == QMediaPlayer.InvalidMedia:
            self.retry_timer.start(self.retry_interval)
            self.video_widget.hide()
            self.backgroundImageLabel.show()
        if status == QMediaPlayer.LoadedMedia:
            self.retry_timer.stop()

    def change_state(self, state):
        print(f"Changed state to {type(state).__name__}")  # Debug print to check state changes
        self.current_state = state

    def handle_successful(self):
        self.change_state(self.current_state.handle_successful())

    def handle_unsuccessful(self):
        self.change_state(self.current_state.handle_unsuccessful())
    
    def handle_error(self):
        self.change_state(self.current_state.handle_error())
        

