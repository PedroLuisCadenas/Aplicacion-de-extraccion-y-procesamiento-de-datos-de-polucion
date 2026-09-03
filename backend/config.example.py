# Plantilla de configuración del backend.
# Cópiala como `config.py` y rellena los valores reales de tu entorno.
# `config.py` contiene credenciales, está en .gitignore y NUNCA se sube al repositorio.
# El código siempre importa de `config.py`; este archivo solo documenta qué variables hacen falta.

# --- InfluxDB 1.x (base de datos de series temporales) --- 
INFLUX_HOST = "127.0.0.1"   # INFLUX_HOST:     host o IP del servidor, (usa IP, no "localhost").
INFLUX_PORT = 8086          # INFLUX_PORT:     puerto HTTP de InfluxDB.
INFLUX_SSL = False          # INFLUX_SSL:      True si el servidor usa https.
INFLUX_DATABASE = "pruebas" # INFLUX_DATABASE: base de datos.
INFLUX_USERNAME = ""        # INFLUX_USERNAME: usuario; vacío si el servidor no tiene autenticación activada.
INFLUX_PASSWORD = ""        # INFLUX_PASSWORD: contraseña.

# --- API de Kunak (fuente de datos real de polución) ---

KUNAK_BASE_URL = "https://kunakcloud.com/openAPIv0/v1/rest" # KUNAK_BASE_URL:  URL base de la API REST de Kunak.
KUNAK_USERNAME = "<usuario-web-kunak>"                      # KUNAK_USERNAME:  usuario de la web de Kunak. Se usa también como user_id en las rutas que lo piden.
KUNAK_PASSWORD = "<contraseña-web-kunak>"                   # KUNAK_PASSWORD:  contraseña. La autenticación es Basic Auth en cada petición (sin login por token).
KUNAK_DEVICE_ID = "<id-dispositivo>"                        # KUNAK_DEVICE_ID: identificador del dispositivo/estación cuyos sensores se consultan.

# --- API pública propia (/api/v1) ---

PUBLIC_API_KEY = "<clave-publica-para-API>" # Clave que deben enviar los clientes en la cabecera `X-API-Key` para acceder a /api/v1.
