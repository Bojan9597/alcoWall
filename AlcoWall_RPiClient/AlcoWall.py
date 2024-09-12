from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QUrl, Qt, QTimer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtGui import QPixmap
from VideoWidget import VideoWidget
#checking update script  sss
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
        self.video_widget = VideoWidget(self)
        self.video_widget.alcoholSensorText.hide()
        self.video_widget.proximitySensorText.hide()
        self.video_widget.lcdCounter.hide()
        self.video_widget.lcdNumber.hide()
        self.set_background_image(self.backgroundImageLabel, 'images/breathalyzerImage.jpg')

        self.main_videos_widget = self.ui.findChild(QWidget, "backgroundContainer")
        self.workingWidget = VideoWidget(self)
        self.main_videos_widget.layout().addWidget(self.workingWidget)

        layout = video_container.layout()
        if layout is None:
            layout = QVBoxLayout(video_container)
        layout.addWidget(self.video_widget)

        self.backgroundImageLabel.hide()
        self.video_widget.show()


        self.retry_timer = QTimer(self)
        self.retry_timer.timeout.connect(self.retry_load_video)
        self.retry_interval = 5000

        self._initialized = True
        self.current_state = None

    def retry_load_video(self):
        self.media_player.setSource(QUrl.fromLocalFile('videos/AI.mp4'))
        self.backgroundImageLabel.show()
        self.media_player.play()

    def set_background_image(self, widget, image_path):
        pixmap = QPixmap(image_path)
        widget.setPixmap(pixmap)
        widget.setScaledContents(True)

    def change_state(self, state):
        #print(f"Changed state to {type(state).__name__}")  # Debug print to check state changes
        self.current_state = state

    def handle_successful(self):
        self.change_state(self.current_state.handle_successful())

    def handle_unsuccessful(self):
        self.change_state(self.current_state.handle_unsuccessful())
    
    def handle_error(self):
        self.change_state(self.current_state.handle_error())
        

