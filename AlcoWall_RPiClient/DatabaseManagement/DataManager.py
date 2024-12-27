# DataManager.py

import os
import json
from datetime import datetime
import requests
from Constants.GENERALCONSTANTS import BASE_URL, DEVICE_ID

class DataManager:
    def __init__(self, device_id):
        self.device_id = device_id
        # self.highscore_file = "DatabaseManagement/jsonFiles/highscores.json"
        # self.alcohol_results_file = "DatabaseManagement/jsonFiles/alcohol_results.json"
        self.base_url = BASE_URL

    def ensure_directory_exists(self, directory):
        """
        Ensures that the directory exists, creates it if it doesn't.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def get_ad_url(self):
        """
        Fetch the ad URL from the server.
        Returns the ad URL if successful, None otherwise.
        """
        url = f"{self.base_url}/advertisment/get_ad_url"
        payload = {"device_id": self.device_id}
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                ad_url = response.json().get("ad_url")
                if ad_url:
                    return ad_url
                else:
                    print("No ad URL found in the response.")
                    return None
            else:
                print(f"Failed to fetch ad URL. Status code: {e}")
                return None
        except requests.RequestException as e:
            print(f"Request to fetch ad URL failed: {e}")
            return None
    
    def get_fun_fact(self):
        """
        Fetches a fun fact from the API.
        Returns the fun fact string if successful, or a default fun fact on failure.
        """
        fallback_fact = ("Tokom prohibicije u Sjedinjenim Državama, ljudi su pili \"lekovitu\" viskiju "
                         "koju su im lekari prepisivali kao način da legalno dođu do alkohola.")
        try:
            response = requests.post("https://node.alkowall.indigoingenium.ba/facts/general_fact")
            if response.status_code == 200:
                fact_data = response.json()

                # Check if fact_data is a list or dict
                if isinstance(fact_data, list) and len(fact_data) > 0:
                    fact_sentence = fact_data[0].get("sentence", fallback_fact)
                elif isinstance(fact_data, dict):
                    fact_sentence = fact_data.get("sentence", fallback_fact)
                else:
                    fact_sentence = fallback_fact

                return fact_sentence
            else:
                print(f"Failed to fetch fun fact. Status code: {response.status_code}")
                return fallback_fact
        except requests.RequestException as e:
            print(f"Error fetching fun fact: {e}")
            return fallback_fact
