import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET


def write_data(data: dict, device_id: str = "unknown"):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("pollution").tag("device_id", device_id)

    # Timestamp from Kunak comes in milliseconds UTC
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
