"""Escritura en InfluxDB 1.x (InfluxQL). Cada función abre su propio cliente,
escribe de forma síncrona y lo cierra"""

# Measurements de InfluxDB: pollution, device_info, device_elements, user_info

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


# Escribe una lectura de un dispositivo en InfluxDB (measurement: pollution).
def write_readings(data: dict, device_id: str = "unknown"):
    fields = {}
    for field, value in data.items():
        if field == "timestamp_ms":
            continue
        try:
            fields[field] = float(value)
        except (TypeError, ValueError):
            pass

    if not fields:
        print("Sin lecturas numéricas que escribir")
        return

    point = {
        "measurement": "pollution",
        "tags": {"device_id": device_id},
        "fields": fields,
    }
    # El timestamp de Kunak viene en milisegundos; con time_precision="ms" el
    # cliente lo interpreta bien (por defecto asumiría nanosegundos).
    ts_ms = data.get("timestamp_ms")
    if ts_ms:
        point["time"] = int(ts_ms)

    client = _client()
    client.write_points([point], time_precision="ms")
    client.close()
    print("Datos escritos en InfluxDB correctamente")


# Escribe la información del dispositivo en InfluxDB (measurement: device_info).
def write_device_info(info: dict, device_id: str):
    status = info.get("status", {})

    fields = {
        "tag": info.get("tag", ""),
        "serial_number": info.get("serial_number", ""),
    }
    for field in ("battery_level", "rx_signal_level"):
        value = status.get(field)
        if value is not None:
            try:
                fields[field] = float(value)
            except (TypeError, ValueError):
                pass

    point = {
        "measurement": "device_info",
        "tags": {"device_id": device_id},
        "fields": fields,
    }
    client = _client()
    client.write_points([point])
    client.close()
    print("Info del dispositivo escrita en InfluxDB correctamente")


# Escribe el catálogo de sensores del dispositivo (measurement: device_elements).
def write_elements_catalog(elements: list, device_id: str):
    points = []
    for element in elements:
        if not element.get("id"):
            continue
        fields = {"name": element.get("name", element["id"])}
        # Los sensores adimensionales (p.ej. AQI) no llevan unidad: se omite el
        # field en vez de escribir "".
        unit = element.get("unit", "")
        if unit:
            fields["unit"] = unit
        points.append({
            "measurement": "device_elements",
            "tags": {"device_id": device_id, "element_id": element["id"]},
            "fields": fields,
        })

    if not points:
        return

    client = _client()
    client.write_points(points)
    client.close()
    print("Catálogo de sensores escrito en InfluxDB correctamente")


# Escribe la información del usuario en InfluxDB (measurement: user_info).
def write_user_info(info: dict, user_id: str):
    fields = {}
    for field, value in info.items():
        if value is None or isinstance(value, (dict, list)):
            continue
        if isinstance(value, bool):
            fields[field] = value
        elif isinstance(value, (int, float)):
            fields[field] = float(value)
        else:
            fields[field] = str(value)

    if not fields:
        return

    point = {
        "measurement": "user_info",
        "tags": {"user_id": user_id},
        "fields": fields,
    }
    client = _client()
    client.write_points([point])
    client.close()
    print("Info del usuario escrita en InfluxDB correctamente")
