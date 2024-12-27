from PySide6.QtWidgets import QApplication
import sys
from Components.AlcoWall import AlcoWall

if __name__ == "__main__":
    app = QApplication(sys.argv)

    alcoWall = AlcoWall()
    alcoWall.data_manager.ad_url_signal.connect(alcoWall.get_ad_url)
    alcoWall.data_manager.fun_fact_signal.connect(alcoWall.get_fun_fact)
    alcoWall.data_manager.get_ad_url()
    alcoWall.data_manager.get_fun_fact()
    alcoWall.show()
    #ota testing
    from sensorReadout.SensorVariableUpdates import SensorVariableUpdates
    sensor_variable_updates = SensorVariableUpdates()
    from States.InitialState import InitialState
    alcoWall.current_state = InitialState()

    sys.exit(app.exec())
