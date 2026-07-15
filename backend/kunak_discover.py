"""
Script de ayuda para la API Kunak.
Usa Basic Auth (usuario/contraseña) para listar los dispositivos
disponibles, para poder rellenar KUNAK_USER_ID y KUNAK_DEVICE_ID en config.py.

Uso:
    python kunak_discover.py
"""
import json
from api_client import KunakClient
from config import KUNAK_USERNAME, KUNAK_USER_ID


def main():
    print(f"Consultando como: {KUNAK_USERNAME}")
    client = KunakClient()

    user_id = KUNAK_USER_ID or KUNAK_USERNAME
    print(f"Buscando dispositivos para user_id='{user_id}'...")
    try:
        devices = client.list_devices(user_id)
        print(json.dumps(devices, indent=2, ensure_ascii=False))
        print("\nCopia el user_id/device_id que necesites en config.py.")
    except Exception as e:
        print(f"Error al listar dispositivos: {e}")
        print("Si KUNAK_USER_ID está vacío en config.py, prueba a rellenarlo con el user_id real.")


if __name__ == "__main__":
    main()
