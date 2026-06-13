from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from influx_reader import query_latest, query_history

app = FastAPI(title="TFG Pollution API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/pollution/latest")
def get_latest():
    return query_latest()


@app.get("/api/pollution")
def get_history(hours: int = 24):
    return query_history(hours=hours)
