"""
Backfill: vuelca en InfluxDB el histórico reciente (14 días por defecto) de todos
los sensores del dispositivo Kunak, de una sola vez.

Uso:
    python backfill.py        # 14 días
    python backfill.py 7      # 7 días

Cada petición a Kunak trae 4000 lecturas (~medio día de histórico), así que un
backfill de 14 días son unas 25-30 peticiones. Muy por debajo del límite mensual
de la API (10.000), pero no es algo para lanzar de forma rutinaria.
"""

import sys
import time

from api_client import (
    KunakClient,
    list_device_elements,
    _normalize_multi_reads,   # parsea la respuesta multi-sensor de Kunak
    MAX_READS_PER_REQUEST,
)
from influx_client import write_readings_bulk
from config import KUNAK_DEVICE_ID

DIAS_POR_DEFECTO = 14


def backfill(dias):
    sensores = [e["id"] for e in list_device_elements(KUNAK_DEVICE_ID)]
    if not sensores:
        print(f"No hay sensores para el dispositivo {KUNAK_DEVICE_ID}.")
        return 0

    ahora_ms = int(time.time() * 1000)
    cursor = ahora_ms - dias * 24 * 60 * 60 * 1000
    print(f"Backfill de {dias} días ({len(sensores)} sensores)...")

    kunak = KunakClient()
    total = 0
    while cursor < ahora_ms:
        raw = kunak.get_elements_reads(
            KUNAK_DEVICE_ID, sensores, ts=cursor, number=MAX_READS_PER_REQUEST
        )
        lecturas = _normalize_multi_reads(raw)
        marcas = [r["ts"] for lista in lecturas.values() for r in lista if r.get("ts")]
        if not marcas:
            break

        total += write_readings_bulk(lecturas, KUNAK_DEVICE_ID)
        print(f"  ...{time.strftime('%d/%m %H:%M', time.localtime(max(marcas) / 1000))}  ({total} puntos)")

        # Menos de un lote completo => se ha llegado al final del histórico.
        if sum(len(lista) for lista in lecturas.values()) < MAX_READS_PER_REQUEST:
            break
        cursor = max(marcas) + 1

    print(f"Hecho: {total} puntos escritos en InfluxDB.")
    return total


if __name__ == "__main__":
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else DIAS_POR_DEFECTO
    backfill(dias)
