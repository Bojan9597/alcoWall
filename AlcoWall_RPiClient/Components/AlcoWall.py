from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QUrl, Qt, QTimer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtGui import QPixmap
from Components.VideoWidget import VideoWidget
from Constants.GENERALCONSTANTS import DEVICE_ID_FILE, PERCENTAGE_OF_SCREEN_WIDTH_THAT_PROXIMITY_SENSOR_TEXT_TAKES
import threading
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
        self.weekly_highscore = 0
        self.monthly_highscore = 0
        self.highscore = 0
        self.device_id = self.read_device_id()

        self.credit = 0
        self.alcohol_level = -1

        self.service_door_open = False
        self.coins_door_open = False
        self.coin_stuck = False
        
        self.alcohol_level_to_show = 0

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
        self.video_widget.lcdCounter.hide()
        self.video_widget.lcdNumber.hide()
        self.set_background_image(self.backgroundImageLabel, 'Media/images/breathalyzerImage.jpg')

        self.main_videos_widget = self.ui.findChild(QWidget, "backgroundContainer")
        self.workingWidget = VideoWidget(self)
        half_width = PERCENTAGE_OF_SCREEN_WIDTH_THAT_PROXIMITY_SENSOR_TEXT_TAKES * self.workingWidget.funFactText.parent().width()
        self.workingWidget.funFactText.setFixedWidth(half_width) 
        self.main_videos_widget.layout().addWidget(self.workingWidget)

        layout = video_container.layout()
        if layout is None:
            layout = QVBoxLayout(video_container)
        layout.addWidget(self.video_widget)

        self.backgroundImageLabel.hide()
        self.video_widget.show()

        self._initialized = True
        self.current_state = None


    def update_credit(self, credit):
        """Update the credit value. but thread safe."""
        with threading.Lock():
            self.credit += credit  
            self.video_widget.coinLabelText.setText(f"Credit: {round(self.credit/100,2)}")
    
    def get_credit(self):
        """Get the current credit value."""
        return self.credit

    def set_credit(self, credit):
        """Set the credit value. but thread safe."""
        with threading.Lock():
            self.credit = credit
    
    def update_alcohol_level(self, alcohol_level):
        """Update the alcohol level. but thread safe."""
        with threading.Lock():
            self.alcohol_level = alcohol_level
    
    def get_alcohol_level(self):
        """Get the current alcohol level."""
        return self.alcohol_level

    def set_alcohol_level(self, alcohol_level):
        """Set the alcohol level. but thread safe."""
        with threading.Lock():
            self.alcohol_level = alcohol_level

    def read_device_id(self):
        """Read the device ID from the device_id.txt file."""
        try:
            with open(DEVICE_ID_FILE, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"Error: {DEVICE_ID_FILE} not found.")
            return None

    def set_background_image(self, widget, image_path):
        pixmap = QPixmap(image_path)
        widget.setPixmap(pixmap)
        widget.setScaledContents(True)

    def change_state(self, state):
        self.current_state = state

    def handle_successful(self):
        self.change_state(self.current_state.handle_successful())

    def handle_unsuccessful(self):
        self.change_state(self.current_state.handle_unsuccessful())
    
    def handle_error(self):
        self.change_state(self.current_state.handle_error())
        

