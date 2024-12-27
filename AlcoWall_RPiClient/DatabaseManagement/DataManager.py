import os
import json
from datetime import datetime
import requests
from threading import Thread
from PySide6.QtCore import QObject, Signal
from Constants.GENERALCONSTANTS import BASE_URL, DEVICE_ID

class DataManager(QObject):
    # Define PySide6 Signals
    ad_url_signal = Signal(str)
    fun_fact_signal = Signal(str)

    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.base_url = BASE_URL

    def ensure_directory_exists(self, directory):
        """
        Ensures that the directory exists, creates it if it doesn't.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get_ad_url(self):
        """
        Fetch the ad URL from the server in a separate thread.
        Emits the URL through the ad_url_signal or an error message.
        """
        def fetch_ad_url():
            url = f"{self.base_url}/advertisment/get_ad_url"
            payload = {"device_id": self.device_id}
            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    ad_url = response.json().get("ad_url")
                    if ad_url:
                        self.ad_url_signal.emit(ad_url)
                    else:
                        self.ad_url_signal.emit("No ad URL found. failed to fetch. Error.")
                else:
                    self.ad_url_signal.emit(f"Failed to fetch ad URL. Status code: {response.status_code}. Error.")
            except requests.RequestException as e:
                self.ad_url_signal.emit(f"Request to fetch ad URL failed: {e} Error.")
        
        # Run in a separate daemon thread
        thread = Thread(target=fetch_ad_url)
        thread.daemon = True
        thread.start()

    def get_fun_fact(self):
        """
        Fetches a fun fact from the API in a separate thread.
        Emits the fun fact through the fun_fact_signal or a default fun fact on failure.
        """
        def fetch_fun_fact():
            fallback_fact = ("Tokom prohibicije u Sjedinjenim Državama, ljudi su pili \"lekovitu\" viskiju "
                             "koju su im lekari prepisivali kao način da legalno dođu do alkohola.")
            try:
                response = requests.post("https://node.alkowall.indigoingenium.ba/facts/general_fact")
                if response.status_code == 200:
                    print(response.json())
                    fact_data = response.json()
                    fact_sentence = ""
                    if isinstance(fact_data, list) and len(fact_data) > 0:
                        fact_sentence = fact_data[0].get("sentence", fallback_fact)
                    elif isinstance(fact_data, dict):
                        fact_sentence = fact_data.get("sentence", fallback_fact)
                    else:
                        fact_sentence = fallback_fact

                    self.fun_fact_signal.emit(fact_sentence)
                else:
                    self.fun_fact_signal.emit(fallback_fact)
            except requests.RequestException as e:
                self.fun_fact_signal.emit(fallback_fact)
        
        # Run in a separate daemon thread
        thread = Thread(target=fetch_fun_fact)
        thread.daemon = True
        thread.start()
