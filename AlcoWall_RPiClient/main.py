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
    alcoWall.setStyleSheet("QMainWindow { background-color: black; }")
    alcoWall.video_widget.setStyleSheet("QVideoWidget { background-color: black; }")
    alcoWall.showFullScreen()
    #ota testing
    from sensorReadout.SensorVariableUpdates import SensorVariableUpdates
    sensor_variable_updates = SensorVariableUpdates()
    sensor_variable_updates.coinAcceptor.CoinAcceptedSignal.connect(sensor_variable_updates)
    from States.InitialState import InitialState
    alcoWall.current_state = InitialState()


    sys.exit(app.exec())
