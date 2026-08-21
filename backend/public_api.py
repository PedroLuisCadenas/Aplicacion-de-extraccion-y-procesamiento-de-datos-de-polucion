from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from config import KUNAK_DEVICE_ID, PUBLIC_API_KEY
from influx_reader import (
    query_latest_readings,
    query_readings_history,
    query_latest_device_info,
    query_latest_elements,
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(key: str = Depends(api_key_header)):
    if key != PUBLIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o ausente",
        )

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])

@router.get("/device/info/latest")
def get_latest_device_info():
    return query_latest_device_info()


@router.get("/device/readings/latest")
def get_latest_readings():
    return query_latest_readings()


@router.get("/device/readings")
def get_readings_history(hours: int = 24, start: str | None = None, end: str | None = None, element_id: str | None = None):
    try:
        return query_readings_history(hours=hours, start=start, end=end, field=element_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (se espera ISO 8601)")


@router.get("/device/elements")
def get_device_elements():
    """Catálogo de sensores del dispositivo, leído de InfluxDB (lo escribe el daemon)."""
    return query_latest_elements(KUNAK_DEVICE_ID)