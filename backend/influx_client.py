from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET


def write_data(data):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = (
        Point("weather")
        .tag("location", "Madrid")
        .field("temperature", data["temperature"])
        .field("humidity", float(data["humidity"]))
        .field("wind_speed", data["wind_speed"])
        .field("apparent_temperature", data["apparent_temperature"])
    )

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    client.close()
    print("Datos escritos en InfluxDB correctamente")
