import threading
import time
import requests
from config import KUNAK_BASE_URL, KUNAK_USERNAME, KUNAK_PASSWORD, KUNAK_DEVICE_ID

DEFAULT_HISTORY_HOURS = 24
MAX_READS_PER_REQUEST = 4000

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

    def _get(self, path, params=None):
        url = f"{self.base_url}/{path}"

        for attempt in range(MAX_RETRIES_ON_429 + 1):
            _throttle()
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 429 and attempt < MAX_RETRIES_ON_429:
                retry_after = response.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else _MIN_REQUEST_INTERVAL * (2 ** (attempt + 1))
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.json()

    def get_user_info(self, user_id):
        return self._get(f"users/{user_id}/info")

    def list_devices(self, user_id):
        return self._get(f"devices/list/{user_id}")

    def get_device_info(self, device_id):
        return self._get(f"devices/{device_id}/info")

    def get_elements(self, device_id):
        """Lista los elementos (sensores) de un dispositivo."""
        return self._get(f"devices/{device_id}/elements")

    def get_element_reads(self, device_id, element_id, ts, number=1000):
        """Lecturas de un elemento posteriores a `ts` (ms desde epoch)."""
        params = {"ts": ts, "number": number}
        return self._get(f"devices/{device_id}/elements/{element_id}/reads/from", params=params)


def _normalize_elements(raw):
    """Normaliza la respuesta de /elements a una lista de dicts {id, name}."""
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
            elements.append({"id": element_id, "name": name})
        elif isinstance(e, str):
            elements.append({"id": e, "name": e})

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


def list_device_elements(device_id=None):
    """Lista los sensores (elementos) disponibles de un dispositivo Kunak."""
    client = KunakClient()
    device_id = device_id or KUNAK_DEVICE_ID
    raw = client.get_elements(device_id)
    return _normalize_elements(raw)


def get_element_history(device_id, element_id, hours=DEFAULT_HISTORY_HOURS):
    """Lecturas de un sensor concreto durante las últimas `hours` horas."""
    client = KunakClient()
    now_ms = int(time.time() * 1000)
    ts = now_ms - int(hours * 60 * 60 * 1000)
    raw = client.get_element_reads(device_id, element_id, ts=ts, number=MAX_READS_PER_REQUEST)
    return _normalize_reads(raw)


def get_device_readings(device_id=None):
    """Última lectura de cada sensor del dispositivo, para el daemon de recolección."""
    client = KunakClient()
    device_id = device_id or KUNAK_DEVICE_ID

    elements = list_device_elements(device_id)
    if not elements:
        raise RuntimeError(
            f"No se encontraron sensores para el dispositivo {device_id}."
        )

    now_ms = int(time.time() * 1000)
    ts = now_ms - 24 * 60 * 60 * 1000  # ventana de búsqueda de la última lectura

    data = {}
    timestamp = None

    for element in elements:
        element_id = element["id"]
        raw = client.get_element_reads(device_id, element_id, ts=ts, number=MAX_READS_PER_REQUEST)
        reads = _normalize_reads(raw)
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
