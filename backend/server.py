from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import KUNAK_DEVICE_ID
from influx_reader import (
    query_latest_readings,
    query_readings_history,
    query_latest_device_info,
    query_latest_user_info,
    query_latest_elements,
)


app = FastAPI(title="TFG Pollution API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/user/info")
def get_latest_user_info():
    return query_latest_user_info()


@app.get("/api/device/info/latest")
def get_latest_device_info():
    return query_latest_device_info()


@app.get("/api/device/readings/latest")
def get_latest_readings():
    return query_latest_readings()


@app.get("/api/device/readings")
def get_readings_history(hours: int = 24, start: str | None = None, end: str | None = None, element_id: str | None = None):
    try:
        return query_readings_history(hours=hours, start=start, end=end, field=element_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (se espera ISO 8601)")


@app.get("/api/device/elements")
def get_device_elements():
    """Catálogo de sensores del dispositivo, leído de InfluxDB (lo escribe el daemon)."""
    return query_latest_elements(KUNAK_DEVICE_ID)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
