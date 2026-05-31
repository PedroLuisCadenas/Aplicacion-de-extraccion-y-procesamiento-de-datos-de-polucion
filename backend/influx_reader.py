from influxdb_client import InfluxDBClient
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET


def query_latest():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "weather")
          |> last()
    '''

    result = query_api.query(query=query, org=INFLUX_ORG)
    client.close()

    data = {}
    for table in result:
        for record in table.records:
            data[record.get_field()] = record.get_value()

    return data


def query_history(hours: int = 24):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -{hours}h)
          |> filter(fn: (r) => r._measurement == "weather")
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"])
    '''

    result = query_api.query(query=query, org=INFLUX_ORG)
    client.close()

    records = []
    for table in result:
        for record in table.records:
            records.append({
                "time": record.get_time().isoformat(),
                "temperature": record.values.get("temperature"),
                "humidity": record.values.get("humidity"),
                "wind_speed": record.values.get("wind_speed"),
                "apparent_temperature": record.values.get("apparent_temperature"),
            })

    return records
