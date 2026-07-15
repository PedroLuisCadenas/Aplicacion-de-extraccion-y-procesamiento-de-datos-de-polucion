import time
from api_client import KunakClient
from influx_client import write_device_info
from config import KUNAK_DEVICE_ID

# Modo de prueba temporal: solo se llama a get_info para validar
# conectividad antes de construir el pipeline completo de sensores.


def main():
    print("Probando conexión con Kunak (solo get_info)...")
    if not KUNAK_DEVICE_ID:
        print("KUNAK_DEVICE_ID no está configurado en config.py. Ejecuta kunak_discover.py para obtenerlo.")
        return

    client = KunakClient()
    while True:
        try:
            info = client.get_device_info(KUNAK_DEVICE_ID)
            print(f"Info del dispositivo: {info}")
            write_device_info(info, device_id=KUNAK_DEVICE_ID)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)


if __name__ == "__main__":
    main()
