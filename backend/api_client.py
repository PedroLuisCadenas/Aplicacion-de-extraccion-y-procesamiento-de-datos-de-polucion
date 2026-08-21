import threading
import time
import requests
from config import KUNAK_BASE_URL, KUNAK_USERNAME, KUNAK_PASSWORD, KUNAK_DEVICE_ID

DEFAULT_HISTORY_HOURS = 24
MAX_READS_PER_REQUEST = 4000

# Ventana de búsqueda para get_device_readings(): debe cubrir el intervalo de
# sondeo del daemon (main.py) con margen, pero mantenerse muy por debajo de
# MAX_READS_PER_REQUEST para el conjunto de todos los sensores combinados, o la
# respuesta se trunca antes de llegar a las lecturas más recientes.
READINGS_SEARCH_WINDOW_MINUTES = 20

# La API de Kunak limita a 10 peticiones/segundo. Se deja margen de seguridad
# y se comparte entre todas las instancias de KunakClient (el daemon y el
# servidor pueden crear varias en el mismo proceso).
KUNAK_MAX_REQUESTS_PER_SECOND = 8
_MIN_REQUEST_INTERVAL = 1.0 / KUNAK_MAX_REQUESTS_PER_SECOND
_RATE_LIMIT_LOCK = threading.Lock()
_last_request_time = 0.0

MAX_RETRIES_ON_429 = 3


def _throttle():
    """Bloquea lo necesario para no superar el límite de peticiones/segundo."""
    global _last_request_time
    with _RATE_LIMIT_LOCK:
        now = time.monotonic()
        wait = _last_request_time + _MIN_REQUEST_INTERVAL - now
        if wait > 0:
            time.sleep(wait)
            now = time.monotonic()
        _last_request_time = now


class KunakClient:
    def __init__(self):
        self.base_url = KUNAK_BASE_URL
        self.session = requests.Session()
        self.session.auth = (KUNAK_USERNAME, KUNAK_PASSWORD)

    def _request(self, method, path, params=None, json=None):
        url = f"{self.base_url}/{path}"

        for attempt in range(MAX_RETRIES_ON_429 + 1):
            _throttle()
            response = self.session.request(method, url, params=params, json=json, timeout=10)

            if response.status_code == 429 and attempt < MAX_RETRIES_ON_429:
                retry_after = response.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else _MIN_REQUEST_INTERVAL * (2 ** (attempt + 1))
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.json()

    def _get(self, path, params=None):
        return self._request("GET", path, params=params)

    def _post(self, path, json=None):
        return self._request("POST", path, json=json)

    def get_user_info(self, user_id):
        return self._get(f"users/{user_id}/info")

    def list_devices(self, user_id):
        return self._get(f"devices/list/{user_id}")

    def get_device_info(self, device_id):
        return self._get(f"devices/{device_id}/info")

    def get_elements_details(self, device_id):
        """Lista los elementos (sensores) de un dispositivo, con su unidad de medida."""
        return self._get(f"devices/{device_id}/elementsDetails")

    def get_element_reads(self, device_id, element_id, ts, number=1000):
        """Lecturas de un elemento posteriores a `ts` (ms desde epoch)."""
        params = {"ts": ts, "number": number}
        return self._get(f"devices/{device_id}/elements/{element_id}/reads/from", params=params)

    def get_elements_reads(self, device_id, sensors, ts, number=1000):
        """Lecturas de varios sensores a la vez, posteriores a `ts` (ms desde epoch)."""
        payload = {"sensors": sensors, "ts": ts, "number": number}
        return self._post(f"devices/{device_id}/reads/from", json=payload)


def _normalize_elements(raw):
    """Normaliza la respuesta de /elementsDetails a una lista de dicts {id, name, unit}.

    La API no da un nombre legible aparte de `tag`, así que `name` es igual a `id`.
    """
    if isinstance(raw, dict):
        raw = raw.get("elements", raw.get("data", raw.get("items", [])))

    elements = []
    if not isinstance(raw, list):
        return elements

    for e in raw:
        if isinstance(e, dict):
            element_id = e.get("tag") or e.get("id") or e.get("element_id")
            if not element_id:
                continue
            name = e.get("name") or e.get("sensor") or e.get("description") or element_id
            unit = e.get("unit") or ""
            elements.append({"id": element_id, "name": name, "unit": unit})
        elif isinstance(e, str):
            elements.append({"id": e, "name": e, "unit": ""})

    return elements


def _normalize_reads(raw):
    """Normaliza la respuesta de reads/from a una lista de dicts {ts, value}."""
    if isinstance(raw, dict):
        raw = raw.get("reads", raw.get("values", raw.get("data", raw.get("items", []))))

    reads = []
    if not isinstance(raw, list):
        return reads

    for r in raw:
        if isinstance(r, dict) and "value" in r:
            ts = r.get("ts") or r.get("timestamp")
            reads.append({"ts": int(ts) if ts is not None else None, "value": r["value"]})

    return reads


def _normalize_multi_reads(raw):
    """Normaliza la respuesta de reads/from (multi-sensor) a {element_id: [{ts, value}, ...]}.

    La API real devuelve una lista plana de lecturas, cada una con su propio
    sensor_tag, p.ej.:
    [{"sensor_tag": "Temp", "value": "27.13", "ts": 1750071417000, "validation": "T", "reason": "0"}, ...]
    """
    if isinstance(raw, dict):
        container = raw.get("reads", raw.get("data", raw.get("items", raw)))
    else:
        container = raw

    result = {}

    if isinstance(container, dict):
        for tag, reads in container.items():
            result[tag] = _normalize_reads(reads)
        return result

    if isinstance(container, list):
        for entry in container:
            if not isinstance(entry, dict):
                continue
            tag = entry.get("sensor_tag") or entry.get("sensor") or entry.get("tag") or entry.get("element_id")
            if tag is None:
                continue
            nested = entry.get("reads", entry.get("values", entry.get("data")))
            if nested is not None:
                result.setdefault(tag, []).extend(_normalize_reads(nested))
            elif "value" in entry:
                ts = entry.get("ts") or entry.get("timestamp")
                result.setdefault(tag, []).append(
                    {"ts": int(ts) if ts is not None else None, "value": entry["value"]}
                )
        return result

    return result


def list_device_elements(device_id=None):
    """Lista los sensores (elementos) disponibles de un dispositivo Kunak."""
    client = KunakClient()
    device_id = device_id or KUNAK_DEVICE_ID
    raw = client.get_elements_details(device_id)
    return _normalize_elements(raw)


def get_element_history(device_id, element_id, hours=DEFAULT_HISTORY_HOURS):
    """Lecturas de un sensor concreto durante las últimas `hours` horas."""
    client = KunakClient()
    now_ms = int(time.time() * 1000)
    ts = now_ms - int(hours * 60 * 60 * 1000)
    raw = client.get_element_reads(device_id, element_id, ts=ts, number=MAX_READS_PER_REQUEST)
    return _normalize_reads(raw)


def get_device_readings(device_id=None, elements=None):
    """Última lectura de cada sensor del dispositivo, para el daemon de recolección.

    Acepta `elements` ya obtenidos (p.ej. por el propio daemon, para escribir
    también el catálogo) y así evita pedirlos dos veces."""
    client = KunakClient()
    device_id = device_id or KUNAK_DEVICE_ID

    elements = elements if elements is not None else list_device_elements(device_id)
    if not elements:
        raise RuntimeError(
            f"No se encontraron sensores para el dispositivo {device_id}."
        )

    now_ms = int(time.time() * 1000)
    ts = now_ms - READINGS_SEARCH_WINDOW_MINUTES * 60 * 1000

    sensors = [element["id"] for element in elements]
    raw = client.get_elements_reads(device_id, sensors, ts=ts, number=MAX_READS_PER_REQUEST)
    reads_by_sensor = _normalize_multi_reads(raw)

    data = {}
    timestamp = None

    for element_id, reads in reads_by_sensor.items():
        if not reads:
            continue

        latest = max(reads, key=lambda r: r["ts"] or 0)
        try:
            data[element_id] = float(latest["value"])
        except (TypeError, ValueError):
            continue

        if latest["ts"] and (timestamp is None or latest["ts"] > timestamp):
            timestamp = latest["ts"]

    if timestamp:
        data["timestamp_ms"] = int(timestamp)

    return data
