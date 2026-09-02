"""Escritura en InfluxDB. Cada función abre su propio cliente, escribe de forma
síncrona y lo cierra"""

#Measurements de InfluxDB: pollution, device_info, device_elements ,user_info 

import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

#Escribe los datos de lectura de un dispositivo en InfluxDB (measurement: pollution).
def write_readings(data: dict, device_id: str = "unknown"):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("pollution").tag("device_id", device_id)

    # El timestamp de Kunak viene en milisegundos UTC
    ts_ms = data.get("timestamp_ms")
    if ts_ms:
        point = point.time(
            datetime.datetime.fromtimestamp(ts_ms / 1000, tz=datetime.timezone.utc)
        )

    for field, value in data.items():
        if field == "timestamp_ms":
            continue
        try:
            point = point.field(field, float(value))
        except (TypeError, ValueError):
            pass

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    client.close()
    print("Datos escritos en InfluxDB correctamente")


#Escribe la información del dispositivo en InfluxDB (measurement: device_info)
def write_device_info(info: dict, device_id: str):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    status = info.get("status", {})

    point = (
        Point("device_info")
        .tag("device_id", device_id)
        .field("tag", info.get("tag", ""))
        .field("serial_number", info.get("serial_number", ""))
    )

    for field in ("battery_level", "rx_signal_level"):
        value = status.get(field)
        if value is not None:
            try:
                point = point.field(field, float(value))
            except (TypeError, ValueError):
                pass

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    client.close()
    print("Info del dispositivo escrita en InfluxDB correctamente")


#Escribe el catálogo de sensores del dispositivo en InfluxDB (measurement: device_elements)
def write_elements_catalog(elements: list, device_id: str):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    def _point(element):
        point = (
            Point("device_elements")
            .tag("device_id", device_id)
            .tag("element_id", element["id"])
            .field("name", element.get("name", element["id"]))
        )
        # Cadena vacía y NULL son indistinguibles al releer (el cliente de
        # InfluxDB decodifica "" como None), lo que rompe el pivot() de
        # query_latest_elements. Se omite el campo para sensores sin unidad
        # (p.ej. AQI); query_latest_elements ya trata "sin campo" como "".
        unit = element.get("unit", "")
        if unit:
            point = point.field("unit", unit)
        return point

    points = [_point(element) for element in elements if element.get("id")]

    if points:
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points)
    client.close()
    print("Catálogo de sensores escrito en InfluxDB correctamente")


#Escribe la información del usuario en InfluxDB (measurement: user_info)
def write_user_info(info: dict, user_id: str):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("user_info").tag("user_id", user_id)

    for field, value in info.items():
        if value is None or isinstance(value, (dict, list)):
            continue
        if isinstance(value, bool):
            point = point.field(field, value)
        elif isinstance(value, (int, float)):
            point = point.field(field, float(value))
        else:
            point = point.field(field, str(value))

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    client.close()
    print("Info del usuario escrita en InfluxDB correctamente")
