from datetime import datetime, timezone

from influxdb_client import InfluxDBClient
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET


def _to_flux_timestamp(value: str) -> str:
    """Valida y normaliza una fecha ISO 8601 (p.ej. de un <input type=datetime-local>)
    a un timestamp RFC3339 en UTC, apto para interpolar en una consulta Flux.
    Lanza ValueError si el formato no es válido."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def query_latest_readings():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "pollution")
          |> last()
    '''

    result = query_api.query(query=query, org=INFLUX_ORG)
    client.close()

    data = {}
    for table in result:
        for record in table.records:
            data[record.get_field()] = record.get_value()

    return data


def query_latest_device_info():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "device_info")
          |> last()
    '''

    result = query_api.query(query=query, org=INFLUX_ORG)
    client.close()

    data = {}
    for table in result:
        for record in table.records:
            data[record.get_field()] = record.get_value()

    return data


def query_latest_user_info():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "user_info")
          |> last()
    '''

    result = query_api.query(query=query, org=INFLUX_ORG)
    client.close()

    data = {}
    for table in result:
        for record in table.records:
            data[record.get_field()] = record.get_value()

    return data


def query_readings_history(hours: int = 24, start: str | None = None, end: str | None = None):
    """Si se pasa `start`, se usa un rango absoluto [start, end] (end por defecto = ahora),
    ignorando `hours`. Si no, se mantiene el comportamiento anterior (últimas `hours` horas)."""
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    if start is not None:
        range_start = _to_flux_timestamp(start)
        range_stop = _to_flux_timestamp(end) if end else "now()"
        range_clause = f"range(start: {range_start}, stop: {range_stop})"
    else:
        range_clause = f"range(start: -{hours}h)"

    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> {range_clause}
          |> filter(fn: (r) => r._measurement == "pollution")
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"])
    '''

    result = query_api.query(query=query, org=INFLUX_ORG)
    client.close()

    records = []
    for table in result:
        for record in table.records:
            row = {"time": record.get_time().isoformat()}
            row.update({k: v for k, v in record.values.items()
                        if not k.startswith("_") and k not in ("result", "table")})
            records.append(row)

    return records
