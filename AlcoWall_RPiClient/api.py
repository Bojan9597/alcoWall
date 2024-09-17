import requests

def send_post_request(endpoint, body=None):
    """
    Sends a POST request to a given endpoint with an optional body.
    Returns the response as JSON.
    """
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(endpoint, json=body, headers=headers)
        # If the response contains JSON, return it, else raise an error
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return response.text  # Return raw text for HTML errors
        else:
            return {"error": f"Request failed with status code {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def api_functionality(functionality, body=None):
    """
    A function that sends POST requests to different endpoints based on the functionality requested.
    """
    base_url = "https://node.alkowall.indigoingenium.ba"
    
    endpoints = {
        "get_highscore": "/measurements/highscore_global",
        "insert_measurement": "/measurements/add_measurement",
        "get_fun_fact": "/facts/general_fact",
        "add_cash": "/cash/add_cash",
        "add_cash_multiple": "/cash/add_cash_multiple",
        "get_ad_url": "/advertisment/get_ad_url",
        "get_device_status": "/status/get_device_status",
        "get_github_branch": "/status/get_github_branch"
    }

    if functionality in endpoints:
        url = base_url + endpoints[functionality]
        return send_post_request(url, body)
    else:
        return {"error": "Invalid functionality specified"}

# Example usage for each functionality

# Get highscore
print(api_functionality("get_highscore"))

# Insert a measurement
body_measurement = {
    "device_id": 1,
    "alcohol_percentage": 0.67,
    "measurement_date": "2024-07-13T12:00:00"
}
print(api_functionality("insert_measurement", body_measurement))

# Get fun fact
print(api_functionality("get_fun_fact"))

# Add cash
body_cash = {
    "device_id": 4,
    "cash_value": 1,
    "date": "2024-07-13T12:00:00"
}
print(api_functionality("add_cash", body_cash))

# Add cash for multiple devices
body_cash_multiple = [
    {
        "device_id": 1,
        "cash_value": 1,
        "date": "2024-07-13T12:00:00"
    },
    {
        "device_id": 1,
        "cash_value": 1,
        "date": "2024-07-13T12:00:00"
    },
    {
        "device_id": 1,
        "cash_value": 1,
        "date": "2024-07-13T12:00:00"
    }
]
print(api_functionality("add_cash_multiple", body_cash_multiple))

# Get ad URL
body_ad_url = {
    "device_id": 1
}
print(api_functionality("get_ad_url", body_ad_url))

# Get device status
body_device_status = {
    "device_id": 1
}
print(api_functionality("get_device_status", body_device_status))

# Get GitHub branch
body_github_branch = {
    "device_id": 1
}
print(api_functionality("get_github_branch", body_github_branch))
