# DataManager.py

import os
import json
from datetime import datetime
import requests
from CONSTANTS import BASE_URL, DEVICE_ID

class DataManager:
    def __init__(self, device_id):
        self.device_id = device_id
        self.highscore_file = "jsonFiles/highscores.json"
        self.alcohol_results_file = "jsonFiles/alcohol_results.json"
        self.base_url = BASE_URL

    def get_highscore_from_database(self):
        """
        Fetch the global highscore from the database.
        Returns the highscore if successful, None otherwise.
        """
        url = f"{self.base_url}/measurements/highscore_global"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                highscores = response.json()
                if highscores:
                    return float(highscores[0]["alcohol_percentage"])
                else:
                    print("No highscore data received from server.")
                    return None
            else:
                print(f"Failed to fetch highscore from server. Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Request to fetch highscores failed: {e}")
            return None

    def send_alcohol_level_to_database(self, alcohol_level, measurement_date=None):
        """
        Sends the alcohol level to the database.
        Returns True if successful, False otherwise.
        """
        url = f"{self.base_url}/measurements/add_measurement"
        payload = {
            "device_id": self.device_id,
            "alcohol_percentage": alcohol_level,
            "measurement_date": measurement_date or datetime.now().isoformat()
        }

        try:
            response = requests.post(url, json=payload)
            response_data = response.json()
            if response.status_code == 201 and 'measurement_id' in response_data:
                print(f"Measurement added successfully. Measurement ID: {response_data['measurement_id']}")
                return True
            elif 'error' in response_data:
                print(f"Error in measurement submission: {response_data['error']}")
                return False
            else:
                print(f"Failed to send alcohol level to the database. Status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"Request to send alcohol level failed: {e}")
            return False

    def update_highscores(self, highscore):
        """
        Update highscores in the local file.
        """
        current_week = datetime.now().isocalendar()[1]
        current_month = datetime.now().month
        current_date = str(datetime.today())  # Get today's date as string

        # Initialize highscores dictionary
        highscores = {
            "weekly_highscore": highscore,
            "monthly_highscore": highscore,
            "highscore": highscore,
            "last_updated_week": current_week,
            "last_updated_month": current_month,
            "last_updated_date": current_date  # Add the date to the JSON
        }

        # Write to local JSON file
        highscore_file = self.highscore_file
        try:
            os.makedirs(os.path.dirname(highscore_file), exist_ok=True)
            with open(highscore_file, "w") as file:
                json.dump(highscores, file, indent=4)
            print("Highscores updated and saved to file.")
        except IOError as e:
            print(f"An error occurred while writing the highscore file: {e}")

        return highscores

    def load_highscores_from_file(self):
        """
        Load highscores from the local JSON file.
        Returns the loaded highscore dictionary.
        """
        highscore_file = self.highscore_file

        # Default structure if the file doesn't exist or is missing keys
        highscores = {
            "weekly_highscore": 0.0,
            "monthly_highscore": 0.0,
            "highscore": 0.0,
            "last_updated_week": datetime.now().isocalendar()[1],
            "last_updated_month": datetime.now().month,
            "last_updated_date": str(datetime.today())
        }

        if os.path.exists(highscore_file):
            try:
                with open(highscore_file, "r") as file:
                    file_highscores = json.load(file)
                    highscores.update(file_highscores)
                print("Highscores loaded from local file.")
            except IOError as e:
                print(f"An error occurred while reading the highscore file: {e}")
        else:
            print("Highscore file not found, using default values.")

        return highscores

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
                print(f"Failed to fetch ad URL. Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Request to fetch ad URL failed: {e}")
            return None

    def write_alcohol_results_to_json(self, alcohol_level, measurement_date=None):
        """
        Writes the alcohol measurement results to a JSON file.
        """
        timestamp = measurement_date or datetime.now().isoformat()
        data = {
            "device_id": self.device_id,
            "alcohol_level": alcohol_level,
            "datetime": timestamp
        }

        try:
            os.makedirs(os.path.dirname(self.alcohol_results_file), exist_ok=True)
            with open(self.alcohol_results_file, "a") as json_file:
                json.dump(data, json_file)
                json_file.write("\n")  # Write each entry on a new line
            print("Alcohol results written to JSON file.")
        except IOError as e:
            print(f"An error occurred while writing to the JSON file: {e}")

    def load_alcohol_results(self):
        """
        Loads alcohol results from the JSON file.
        Returns a list of results.
        """
        results = []
        if os.path.exists(self.alcohol_results_file):
            try:
                with open(self.alcohol_results_file, "r") as json_file:
                    for line in json_file:
                        data = json.loads(line)
                        results.append(data)
            except IOError as e:
                print(f"An error occurred while reading the alcohol results file: {e}")
        return results

    def clear_alcohol_results(self):
        """
        Clears the alcohol results JSON file.
        """
        if os.path.exists(self.alcohol_results_file):
            try:
                with open(self.alcohol_results_file, "w") as json_file:
                    pass  # Empty the file
                print("Alcohol results file cleared.")
            except IOError as e:
                print(f"An error occurred while clearing the alcohol results file: {e}")

    def send_stored_alcohol_results(self):
        """
        Sends stored alcohol results to the database.
        Removes successfully sent results from the local storage.
        """
        results = self.load_alcohol_results()
        for result in list(results):  # Use a copy of the list
            success = self.send_alcohol_level_to_database(
                alcohol_level=result["alcohol_level"],
                measurement_date=result["datetime"]
            )
            if success:
                results.remove(result)
            else:
                break  # Stop sending if any send operation fails

        # Write back any remaining results
        if results:
            try:
                with open(self.alcohol_results_file, "w") as json_file:
                    for result in results:
                        json.dump(result, json_file)
                        json_file.write("\n")
                print("Remaining alcohol results saved back to file.")
            except IOError as e:
                print(f"An error occurred while writing to the JSON file: {e}")
        else:
            self.clear_alcohol_results()
