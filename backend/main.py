"""Daemon de recolección de datos de Kunak y escritura en InfluxDB

Se arranca ejecutando el comando 'python main.py'
"""

import time
from api_client import KunakClient, get_device_readings_window, list_device_elements
from influx_client import write_device_info, write_user_info, write_readings_bulk, write_elements_catalog
from config import KUNAK_DEVICE_ID, KUNAK_USERNAME

# La API de Kunak tiene un límite de 10.000 peticiones/mes. Con 4 peticiones por
# ciclo, sondear cada 30 min son ~5.760/mes, dejando margen para el resto
# (backfill puntual, alguna consulta manual). La ventana de lecturas
# (READINGS_SEARCH_WINDOW_MINUTES en api_client.py) va ligada a este intervalo.
POLL_INTERVAL_SECONDS = 30 * 60


# Comprueba la configuración y lanza el bucle de recolección de Kunak.
def main():
    print("Probando conexión con Kunak...")
    if not KUNAK_DEVICE_ID:
        print("KUNAK_DEVICE_ID no está configurado en config.py.")
        return

    client = KunakClient()
    while True:
        try:
            # Información del dispositivo.
            info = client.get_device_info(KUNAK_DEVICE_ID)
            write_device_info(info, device_id=KUNAK_DEVICE_ID)

            # Información del usuario.
            info = client.get_user_info(KUNAK_USERNAME)
            write_user_info(info, user_id=KUNAK_USERNAME)

            # Información de los sensores.
            elements = list_device_elements(KUNAK_DEVICE_ID)
            write_elements_catalog(elements, device_id=KUNAK_DEVICE_ID)

            # Lecturas de los sensores.
            readings = get_device_readings_window(device_id=KUNAK_DEVICE_ID, elements=elements)
            n = write_readings_bulk(readings, device_id=KUNAK_DEVICE_ID)
            print(f"{n} puntos de lecturas escritos en InfluxDB")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
