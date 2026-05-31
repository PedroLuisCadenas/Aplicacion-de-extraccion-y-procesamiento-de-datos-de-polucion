import requests
from config import API_URL, API_PARAMS


def get_weather_data():
    response = requests.get(API_URL, params=API_PARAMS)
    response.raise_for_status()
    data = response.json()
    current = data["current"]
    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "apparent_temperature": current["apparent_temperature"],
        "timestamp": current["time"]
    }
