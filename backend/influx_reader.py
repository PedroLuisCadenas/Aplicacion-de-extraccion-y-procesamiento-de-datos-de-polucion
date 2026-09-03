"""Lectura/consulta de InfluxDB 1.x (InfluxQL)"""

from datetime import datetime, timezone
from influxdb import InfluxDBClient
from config import (
    INFLUX_HOST,
    INFLUX_PORT,
    INFLUX_SSL,
    INFLUX_DATABASE,
    INFLUX_USERNAME,
    INFLUX_PASSWORD,
)


# Cliente InfluxDB 1.x. Cada función abre el suyo y lo cierra al terminar.
def _client():
    return InfluxDBClient(
        host=INFLUX_HOST,
        port=INFLUX_PORT,
        username=INFLUX_USERNAME,
        password=INFLUX_PASSWORD,
        database=INFLUX_DATABASE,
        ssl=INFLUX_SSL,
        verify_ssl=INFLUX_SSL,
    )


def _iso_to_rfc3339(value: str) -> str:
    """Valida una fecha ISO 8601 y la normaliza a RFC3339 UTC ('...Z'), apta para
    interpolar como literal de tiempo en una consulta InfluxQL.
    Lanza ValueError si el formato no es válido."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# Última fila escrita en un measurement, como {campo: valor} (sin tags ni time).
# *::field selecciona solo fields, no tags. Vale para device_info y user_info,
# que el daemon escribe como un único punto completo por ciclo.
def _latest_point(measurement: str) -> dict:
    client = _client()
    result = client.query(
        f'SELECT *::field FROM "{measurement}" ORDER BY time DESC LIMIT 1'
    )
    client.close()

    for point in result.get_points():
        return {k: v for k, v in point.items() if k != "time" and v is not None}
    return {}


# Última lectura conocida de cada sensor (measurement: pollution).
def query_latest_readings():
    # LAST(*) = último valor no nulo de cada field por separado. InfluxQL nombra
    # esas columnas "last_<sensor>": se les quita el prefijo. Ventana de 1h.
    client = _client()
    result = client.query('SELECT LAST(*) FROM "pollution" WHERE time > now() - 1h')
    client.close()

    data = {}
    for point in result.get_points():
        for key, value in point.items():
            if key == "time" or value is None:
                continue
            data[key[5:] if key.startswith("last_") else key] = value
    return data


# Última información conocida del dispositivo (measurement: device_info).
def query_latest_device_info():
    return _latest_point("device_info")


# Última información conocida del usuario (measurement: user_info).
def query_latest_user_info():
    return _latest_point("user_info")


# Último catálogo de sensores conocido (measurement: device_elements).
def query_latest_elements(device_id: str):
    """Leído de Influx en vez de en vivo de Kunak. -7d de margen por si el daemon
    lleva un tiempo parado. """
    client = _client()
    result = client.query(
        'SELECT LAST(*) FROM "device_elements" '
        f"WHERE \"device_id\" = '{device_id}' AND time > now() - 7d "
        'GROUP BY "element_id"'
    )
    client.close()

    elements = []
    for (_measurement, tags), series in result.items():
        rows = list(series)
        point = rows[0] if rows else {}
        values = {
            (k[5:] if k.startswith("last_") else k): v
            for k, v in point.items()
            if k != "time" and v is not None
        }
        element_id = (tags or {}).get("element_id")
        elements.append({
            "id": element_id,
            "name": values.get("name") or element_id,
            "unit": values.get("unit") or "",
        })
    return elements


# Histórico de lecturas (measurement: pollution).
def query_readings_history(hours: int = 24, start: str | None = None, end: str | None = None, field: str | None = None):
    """Si se pasa `start`, se usa un rango absoluto [start, end] (end por defecto = ahora),
    ignorando `hours`. Si no, últimas `hours` horas. `field` (opcional) trae un solo sensor."""
    if field is not None and '"' in field:
        raise ValueError("Nombre de sensor inválido")

    if start is not None:
        where = f"time >= '{_iso_to_rfc3339(start)}'"
        if end:
            where += f" AND time <= '{_iso_to_rfc3339(end)}'"
    else:
        where = f"time > now() - {int(hours)}h"

    select = f'"{field}"' if field else "*::field"
    query = f'SELECT {select} FROM "pollution" WHERE {where} ORDER BY time ASC'

    client = _client()
    result = client.query(query)
    client.close()

    records = []
    for point in result.get_points():
        row = {"time": point["time"]}
        for key, value in point.items():
            if key != "time" and value is not None:
                row[key] = value
        records.append(row)
    return records
