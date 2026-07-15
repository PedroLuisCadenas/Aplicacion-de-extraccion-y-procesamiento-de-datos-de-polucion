from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from influx_reader import query_latest_readings, query_readings_history, query_latest_device_info

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="TFG Pollution API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/device/info/latest")
def get_latest_device_info():
    return query_latest_device_info()


@app.get("/api/device/readings/latest")
def get_latest_readings():
    return query_latest_readings()


@app.get("/api/device/readings")
def get_readings_history(hours: int = 24):
    return query_readings_history(hours=hours)


app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
