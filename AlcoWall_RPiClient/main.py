from PySide6.QtWidgets import QApplication
import sys
from Components.AlcoWall import AlcoWall

if __name__ == "__main__":
    app = QApplication(sys.argv)

    alcoWall = AlcoWall()
    alcoWall.showFullScreen()
    #ota testing
    from sensorReadout.SensorVariableUpdates import SensorVariableUpdates
    sensor_variable_updates = SensorVariableUpdates()
    from States.InitialState import InitialState
    alcoWall.current_state = InitialState()

    sys.exit(app.exec())
