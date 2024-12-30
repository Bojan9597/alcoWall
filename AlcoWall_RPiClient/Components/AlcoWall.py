# AlcoWall.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QUrl, Qt, QTimer, Slot
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtGui import QPixmap
from Components.VideoWidget import VideoWidget
from Constants.GENERALCONSTANTS import DEVICE_ID_FILE, PERCENTAGE_OF_SCREEN_WIDTH_THAT_PROXIMITY_SENSOR_TEXT_TAKES
import threading
from DatabaseManagement.DataManager import DataManager  # Import the DataManager
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class AlcoWall(QMainWindow):
    _instance = None
    video_finished = Signal()
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        super().__init__()
        
        # Initialize variables
        self.device_id = self.read_device_id()
        self.next_add_url = None
        self.fun_fact = None

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
        
        # Initialize Video Player Components
        self.initialize_video_player()

        # Initialize Working Widget (Retains VideoWidget)
        self.initialize_working_widget()

        # Initially hide the background image and show the video widget
        self.backgroundImageLabel.hide()
        self.media_player.play()  # Optionally start playing if needed

        self._initialized = True
        self.current_state = None
        self.data_manager = DataManager(self.device_id)

    def initialize_video_player(self):
        """Initialize QMediaPlayer and QVideoWidget to replace self.video_widget."""
        # Find and set backgroundImageLabel as an attribute
        self.backgroundImageLabel = self.ui.findChild(QLabel, "backgroundImageLabel")
        if self.backgroundImageLabel is None:
            print("Error: 'backgroundImageLabel' not found in UI.")
            exit(-1)
        
        # Create a QVideoWidget instance for video playback
        self.video_widget = QVideoWidget(self)

        # Create a QMediaPlayer instance
        self.media_player = QMediaPlayer(self)

        # Set the video output to the QVideoWidget
        self.media_player.setVideoOutput(self.video_widget)

        # Optionally, set media source here or elsewhere as needed
        # Example:
        # self.media_player.setSource(QUrl.fromLocalFile("path/to/your/video.mp4"))

        # Configure the UI elements related to the video player
        video_container = self.ui.findChild(QWidget, "videoContainer")
        if video_container is None:
            print("Error: 'videoContainer' widget not found in UI.")
            exit(-1)

        layout = video_container.layout()
        if layout is None:
            layout = QVBoxLayout(video_container)
            video_container.setLayout(layout)
        
        # Add the QVideoWidget to the layout
        layout.addWidget(self.video_widget)

        # Set the background image
        self.set_background_image(self.backgroundImageLabel, 'Media/images/breathalyzerImage.jpg')
        
        # Show the video widget
        self.video_widget.show()

    def initialize_working_widget(self):
        """Initialize the working widget using the custom VideoWidget."""
        self.workingWidget = VideoWidget(self)
        main_videos_widget = self.ui.findChild(QWidget, "backgroundContainer")
        if main_videos_widget is None:
            print("Error: 'backgroundContainer' widget not found in UI.")
            exit(-1)
        
        # Adjust the width of the fun fact text
        parent_width = self.workingWidget.funFactText.parent().width()
        if parent_width > 0:
            half_width = PERCENTAGE_OF_SCREEN_WIDTH_THAT_PROXIMITY_SENSOR_TEXT_TAKES * parent_width
            self.workingWidget.funFactText.setFixedWidth(half_width)
        else:
            print("Warning: Parent width is not greater than 0. Cannot set funFactText width.")
        
        # Add the working Widget to the main videos widget layout
        main_videos_widget_layout = main_videos_widget.layout()
        if main_videos_widget_layout is None:
            main_videos_widget_layout = QVBoxLayout(main_videos_widget)
            main_videos_widget.setLayout(main_videos_widget_layout)
        main_videos_widget_layout.addWidget(self.workingWidget)

        # Initially hide certain elements of the working widget
        self.workingWidget.alcoholSensorText.hide()
        self.workingWidget.lcdCounter.hide()
        self.workingWidget.lcdNumber.hide()

    @Slot()
    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.video_finished.emit()

    @Slot(str)
    def get_ad_url(self, ad_url):
        if "Error" not in ad_url:
            self.next_add_url = ad_url

    @Slot(str)
    def get_fun_fact(self, fun_fact):
        print(f"Fun fact: {fun_fact}")
        self.fun_fact = fun_fact

    def update_credit(self, credit):
        """Update the credit value in a thread-safe manner."""
        with threading.Lock():
            self.credit += credit
            # Update the credit display labels
            # Ensure that 'creditLabel' exists in your UI and is correctly named
            credit_label = self.ui.findChild(QLabel, "creditLabel")
            if credit_label:
                credit_label.setText(f"Credit: {round(self.credit / 100, 2)}")
            else:
                print("Warning: 'creditLabel' not found in UI.")
            
            # Update the credit label in the working widget
            if hasattr(self.workingWidget, 'coinLabelText'):
                self.workingWidget.coinLabelText.setText(f"Credit: {round(self.credit / 100, 2)}")
            else:
                print("Warning: 'coinLabelText' not found in workingWidget.")

    def get_credit(self):
        """Get the current credit value."""
        return self.credit

    def set_credit(self, credit):
        """Set the credit value in a thread-safe manner."""
        with threading.Lock():
            self.credit = credit
            # Optionally update the UI after setting credit
            self.update_credit(0)  # Pass 0 to refresh the display without changing the value

    def update_alcohol_level(self, alcohol_level):
        """Update the alcohol level in a thread-safe manner."""
        with threading.Lock():
            self.alcohol_level = alcohol_level

    def get_alcohol_level(self):
        """Get the current alcohol level."""
        return self.alcohol_level

    def set_alcohol_level(self, alcohol_level):
        """Set the alcohol level in a thread-safe manner."""
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
        """Set the background image for a QLabel widget."""
        pixmap = QPixmap(image_path)
        widget.setPixmap(pixmap)
        widget.setScaledContents(True)

    def change_state(self, state):
        """Change the current state."""
        self.current_state = state

    def handle_successful(self):
        """Handle a successful state transition."""
        self.change_state(self.current_state.handle_successful())

    def handle_unsuccessful(self):
        """Handle an unsuccessful state transition."""
        self.change_state(self.current_state.handle_unsuccessful())

    def handle_error(self):
        """Handle an error state transition."""
        self.change_state(self.current_state.handle_error())

    # Additional methods related to QMediaPlayer can be added here
    # For example, to play, pause, stop, etc.

    def play_video(self, video_path):
        """Set the media source and play the video."""
        if self.media_player:
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.media_player.play()
        else:
            print("Error: Media player not initialized.")

    def pause_video(self):
        """Pause the video playback."""
        if self.media_player:
            self.media_player.pause()
        else:
            print("Error: Media player not initialized.")

    def stop_video(self):
        """Stop the video playback."""
        if self.media_player:
            self.media_player.stop()
        else:
            print("Error: Media player not initialized.")
