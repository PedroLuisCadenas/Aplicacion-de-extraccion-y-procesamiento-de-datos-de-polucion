import time
from api_client import KunakClient, get_device_readings
from influx_client import write_device_info, write_user_info, write_readings
from config import KUNAK_DEVICE_ID, KUNAK_USERNAME

# Modo de prueba temporal, recopila información del dispositivo y del usuario cada minuto 
# y la escribe en InfluxDB.


def main():
    print("Probando conexión con Kunak...")
    if not KUNAK_DEVICE_ID:
        print("KUNAK_DEVICE_ID no está configurado en config.py. Ejecuta kunak_discover.py para obtenerlo.")
        return

    client = KunakClient()
    while True:
        try:
            # info = client.get_device_info(KUNAK_DEVICE_ID)
            # write_device_info(info, device_id=KUNAK_DEVICE_ID)
            # info = client.get_user_info(KUNAK_USERNAME)
            # write_user_info(info, user_id=KUNAK_USERNAME)
            info = get_device_readings()
            write_readings(info, device_id=KUNAK_DEVICE_ID)            
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)


if __name__ == "__main__":
    main()
