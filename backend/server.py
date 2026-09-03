"""Servidor FastAPI para expone la API pública 
y proporciona la información a la aplicación

Se arranca ejecutando el comando 'python server.py'
En la dirección http://localhost:8200/docs se puede ver la documentación
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import KUNAK_DEVICE_ID
from public_api import router as public_api_router
from influx_reader import (
    query_latest_user_info,
)


app = FastAPI(title="TFG Pollution API")

# CORS: solo se permite el origen del frontend Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Monta /api/v1 como subruta de la API pública
app.include_router(public_api_router)

# Endpoint interno para mostrar la info de usuario en la aplicación web
@app.get("/api/user/info", include_in_schema=False)
def get_latest_user_info():
    return query_latest_user_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
