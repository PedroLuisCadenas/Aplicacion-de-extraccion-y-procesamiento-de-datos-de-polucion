"""
Script de discovery para la API Kunak.
Prueba distintas URLs base y métodos de autenticación.

Uso:
    python kunak_discover.py
"""
import base64
import requests
from config import KUNAK_USERNAME, KUNAK_TOKEN

_PWD = "sm6U*AI2"  # contraseña original de la cuenta (prueba temporal)

BASE_URLS = [
    "https://kunakcloud.com/openAPIv0/v1/rest",
    "https://kunakcloud.com/api/v1",
    "https://kunakcloud.com/v1",
    "https://api.kunakcloud.com/v1",
    "https://api.kunakcloud.com/openAPIv0/v1/rest",
]

AUTH_VARIANTS = [
    ("Basic user+pwd",     lambda: {"Authorization": "Basic " + base64.b64encode(f"{KUNAK_USERNAME}:{_PWD}".encode()).decode()}),
    ("Basic user+token",   lambda: {"Authorization": "Basic " + base64.b64encode(f"{KUNAK_USERNAME}:{KUNAK_TOKEN}".encode()).decode()}),
    ("Bearer token",       lambda: {"Authorization": f"Bearer {KUNAK_TOKEN}"}),
    ("Bearer pwd",         lambda: {"Authorization": f"Bearer {_PWD}"}),
    ("Token header",       lambda: {"Authorization": f"Token {KUNAK_TOKEN}"}),
    ("X-API-Key token",    lambda: {"X-API-Key": KUNAK_TOKEN}),
    ("X-API-Key pwd",      lambda: {"X-API-Key": _PWD}),
    ("Basic token:empty",  lambda: {"Authorization": "Basic " + base64.b64encode(f"{KUNAK_TOKEN}:".encode()).decode()}),
]

TEST_PATHS = [
    f"devices/list/{KUNAK_USERNAME}",
    "devices",
    "users/me/info",
    f"users/{KUNAK_USERNAME}/info",
]


def probe(base_url, path, headers):
    url = f"{base_url}/{path}"
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        return resp.status_code, resp.text[:300]
    except Exception as e:
        return None, str(e)


def main():
    print(f"Username: {KUNAK_USERNAME}")
    print(f"Token:    {KUNAK_TOKEN[:6]}...{KUNAK_TOKEN[-4:]}\n")

    found = []

    for base_url in BASE_URLS:
        for path in TEST_PATHS:
            for auth_label, auth_fn in AUTH_VARIANTS:
                status, body = probe(base_url, path, auth_fn())
                if status == 200:
                    print(f"EXITO [{status}] {auth_label} -> {base_url}/{path}")
                    print(f"  {body[:200]}\n")
                    found.append((auth_label, base_url, path))
                elif status and status != 401:
                    # Cualquier respuesta que no sea 401 es interesante
                    print(f"  [{status}] {auth_label} -> {base_url}/{path}")
                    print(f"    {body[:150]}")

    print("\n========== RESUMEN ==========")
    if found:
        for auth_label, base_url, path in found:
            print(f"FUNCIONA: {auth_label}  URL: {base_url}/{path}")
    else:
        print("Ninguna combinación funcionó (todos 401 o error de red).")
        print("\nAcciones necesarias — consulta al tutor:")
        print("  1. Email exacto usado en la cuenta Kunak Cloud")
        print("  2. Cómo usar el token: ¿Bearer? ¿Basic Auth? ¿Otro método?")
        print("  3. Confirmar que el token sigue vigente (no caducado)")


if __name__ == "__main__":
    main()
