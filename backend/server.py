from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from influx_reader import query_latest, query_history

app = FastAPI(title="TFG Weather API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/weather/latest")
def get_latest():
    return query_latest()


@app.get("/api/weather")
def get_history(hours: int = 24):
    return query_history(hours=hours)
