import time
from api_client import get_pollution_data
from influx_client import write_data
from config import KUNAK_DEVICE_ID


def main():
    print("Iniciando recogida de datos de polución (Kunak)...")
    while True:
        try:
            data = get_pollution_data()
            print(f"Datos obtenidos: {data}")
            write_data(data, device_id=KUNAK_DEVICE_ID)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)


if __name__ == "__main__":
    main()
