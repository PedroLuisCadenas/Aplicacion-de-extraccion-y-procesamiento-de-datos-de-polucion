from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api_client import list_device_elements, get_element_history
from config import KUNAK_DEVICE_ID
from influx_reader import (
    query_latest_readings,
    query_readings_history,
    query_latest_device_info,
    query_latest_user_info,
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

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
    """Lista en vivo los sensores (elementos) del dispositivo, consultando la API de Kunak."""
    return list_device_elements(KUNAK_DEVICE_ID)


@app.get("/api/device/elements/{element_id}/readings")
def get_device_element_readings(element_id: str, hours: int = 24):
    """Lecturas en vivo de un sensor concreto, consultando la API de Kunak."""
    return get_element_history(KUNAK_DEVICE_ID, element_id, hours=hours)


app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="ui")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
