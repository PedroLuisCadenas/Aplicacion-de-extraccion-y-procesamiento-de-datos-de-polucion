import time
from api_client import get_weather_data
from influx_client import write_data


def main():
    print("Iniciando recogida de datos...")
    while True:
        try:
            data = get_weather_data()
            print(f"Datos obtenidos: {data}")
            write_data(data)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)


if __name__ == "__main__":
    main()
