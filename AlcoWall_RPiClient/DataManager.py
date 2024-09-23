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

    def ensure_directory_exists(self, directory):
        """
        Ensures that the directory exists, creates it if it doesn't.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def write_alcohol_result_to_json(self, alcohol_level, measurement_date=None):
        """
        Writes the alcohol measurement result to a JSON file.
        """
        timestamp = measurement_date or datetime.now().isoformat()
        data = {
            "device_id": self.device_id,
            "alcohol_level": alcohol_level,
            "datetime": timestamp
        }
        self.ensure_directory_exists(os.path.dirname(self.alcohol_results_file))
        try:
            with open(self.alcohol_results_file, "a") as json_file:
                json.dump(data, json_file)
                json_file.write("\n")  # Write each entry on a new line
            print("Alcohol result written to JSON file.")
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

    def get_highscore_from_database(self):
        """
        Fetches the global highscore from the database.
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

    def load_highscores_from_file(self):
        """
        Loads the existing highscores from the local JSON file, or initializes a new structure if not found.
        Returns the highscores dictionary.
        """
        highscores = {
            "weekly_highscore": 0.0,
            "monthly_highscore": 0.0,
            "highscore": 0.0,
            "last_updated_week": datetime.now().isocalendar()[1],
            "last_updated_month": datetime.now().month
        }

        if os.path.exists(self.highscore_file):
            try:
                with open(self.highscore_file, "r") as file:
                    file_highscores = json.load(file)
                    highscores.update(file_highscores)
                print("Highscores loaded from local file.")
            except IOError as e:
                print(f"An error occurred while reading the highscore file: {e}")
        else:
            print("Highscore file not found, using default values.")

        return highscores

    def update_local_highscores(self, highscores):
        """
        Updates the local JSON file with the provided highscores.
        """
        try:
            with open(self.highscore_file, "w") as file:
                json.dump(highscores, file, indent=4)
            print("Highscores updated and saved to local file.")
        except IOError as e:
            print(f"An error occurred while writing the highscore file: {e}")

    def check_and_update_local_highscore(self, alcohol_level, highscores):
        """
        Updates the highscores if the current alcohol level is higher than the locally stored highscore.
        """
        updated = False
        if alcohol_level > highscores["weekly_highscore"]:
            highscores["weekly_highscore"] = alcohol_level
            updated = True

        if alcohol_level > highscores["monthly_highscore"]:
            highscores["monthly_highscore"] = alcohol_level
            updated = True

        if alcohol_level > highscores["highscore"]:
            highscores["highscore"] = alcohol_level
            updated = True

        return updated  # Returns True if any of the highscores were updated

    def update_highscores(self, highscores, database_highscore):
        """
        Updates the highscores dictionary based on the database highscore.
        """
        current_week = datetime.now().isocalendar()[1]
        current_month = datetime.now().month

        # Reset weekly or monthly highscore if the period has changed
        if highscores["last_updated_week"] != current_week:
            highscores["weekly_highscore"] = 0.0
            highscores["last_updated_week"] = current_week

        if highscores["last_updated_month"] != current_month:
            highscores["monthly_highscore"] = 0.0
            highscores["last_updated_month"] = current_month

        # Update highscores if the database highscore is higher
        if database_highscore > highscores["weekly_highscore"]:
            highscores["weekly_highscore"] = database_highscore

        if database_highscore > highscores["monthly_highscore"]:
            highscores["monthly_highscore"] = database_highscore

        if database_highscore > highscores["highscore"]:
            highscores["highscore"] = database_highscore

    def process_alcohol_measurement(self, alcohol_level):
        """
        Handles the entire process of writing alcohol measurement to JSON,
        sending stored measurements to the database, and updating highscores.
        Returns the updated highscores dictionary.
        """
        # Write the current measurement to JSON file
        self.write_alcohol_result_to_json(alcohol_level)

        # Try sending stored results to the database
        self.send_stored_alcohol_results()

        # Load existing highscores
        highscores = self.load_highscores_from_file()

        # Try to get the highscore from the database
        database_highscore = self.get_highscore_from_database()

        if database_highscore is not None:
            # Update highscores based on the database highscore
            self.update_highscores(highscores, database_highscore)
        else:
            # If unable to get database highscore, update local highscore if current level is higher
            self.check_and_update_local_highscore(alcohol_level, highscores)

        # Update the local highscores file
        self.update_local_highscores(highscores)

        return highscores  # Return the updated highscores
    
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
