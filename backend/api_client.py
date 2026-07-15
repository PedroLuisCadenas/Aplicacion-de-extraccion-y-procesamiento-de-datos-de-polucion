import time
import requests
from config import KUNAK_BASE_URL, KUNAK_USERNAME, KUNAK_PASSWORD, KUNAK_DEVICE_ID


class KunakClient:
    def __init__(self):
        self.base_url = KUNAK_BASE_URL
        self.session = requests.Session()
        self.session.auth = (KUNAK_USERNAME, KUNAK_PASSWORD)

    def _get(self, path, params=None):
        url = f"{self.base_url}/{path}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def _post(self, path, body):
        url = f"{self.base_url}/{path}"
        response = self.session.post(url, json=body, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_user_info(self, user_id):
        return self._get(f"users/{user_id}/info")

    def list_devices(self, user_id):
        return self._get(f"devices/list/{user_id}")

    def get_device_info(self, device_id):
        return self._get(f"devices/{device_id}/info")

    def get_latest_readings(self, device_id, sensors):
        now_ms = int(time.time() * 1000)
        body = {"sensors": sensors, "ts": now_ms, "number": 1}
        return self._post(f"devices/{device_id}/reads/until", body)


def _extract_sensors(device_info):
    """Return sensor name list from device info response."""
    elements = device_info.get("elements", device_info.get("sensors", []))
    if isinstance(elements, list):
        return [e.get("name") or e.get("sensor") or e for e in elements if e]
    return []


def get_device_readings():
    client = KunakClient()
    device_id = KUNAK_DEVICE_ID

    device_info = client.get_device_info(device_id)
    sensors = _extract_sensors(device_info)

    if not sensors:
        raise RuntimeError(
            f"No se encontraron sensores para el dispositivo {device_id}. "
            "Ejecuta kunak_discover.py para inspeccionar la respuesta de la API."
        )

    raw = client.get_latest_readings(device_id, sensors)

    data = {}
    timestamp = None

    for sensor_name, readings in raw.items():
        if isinstance(readings, list) and readings:
            record = readings[0]
            data[sensor_name] = float(record["value"])
            if timestamp is None:
                # ts is milliseconds UTC — convert to seconds for ISO string
                timestamp = record.get("ts")
        elif isinstance(readings, dict):
            data[sensor_name] = float(readings.get("value", 0))
            if timestamp is None:
                timestamp = readings.get("ts")

    if timestamp:
        data["timestamp_ms"] = int(timestamp)

    return data
