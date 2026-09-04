"""Servidor FastAPI para expone la API pública 
y proporciona la información a la aplicación

Se arranca ejecutando el comando 'python server.py'
En la dirección http://localhost:8200/docs se puede ver la documentación
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from config import KUNAK_DEVICE_ID
from public_api import router as public_api_router
from influx_reader import (
    query_latest_user_info,
)
from backfill import backfill


app = FastAPI(title="TFG Pollution API")

# CORS: solo se permite el origen del frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://192.168.1.143:4200"], # Cambia a la IP de tu máquina si quieres permitir el acceso desde otros dispositivos
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Monta /api/v1 como subruta de la API pública
app.include_router(public_api_router)

# Endpoint interno para mostrar la info de usuario en la aplicación web
@app.get("/api/user/info", include_in_schema=False)
def get_latest_user_info():
    return query_latest_user_info()


MAX_BACKFILL_DIAS = 60  # 2 meses

# Endpoint interno: lanza backfill.py en segundo plano para rellenar `days` días
# de histórico de Kunak en InfluxDB. Máximo 60 días (2 meses).
@app.post("/api/backfill", include_in_schema=False)
def run_backfill(days: int, background_tasks: BackgroundTasks):
    if not 1 <= days <= MAX_BACKFILL_DIAS:
        raise HTTPException(
            status_code=400,
            detail=f"El número de días debe estar entre 1 y {MAX_BACKFILL_DIAS} (2 meses).",
        )
    background_tasks.add_task(backfill, days)
    return {"status": "iniciado", "days": days}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
