# Plantilla de configuración del backend.
# Cópiala como `config.py` y rellena los valores reales de tu entorno.
# `config.py` contiene credenciales, está en .gitignore y NUNCA se sube al repositorio.
# El código siempre importa de `config.py`; este archivo solo documenta qué variables hacen falta.

# --- InfluxDB (base de datos time-series donde se almacenan las lecturas) ---
INFLUX_URL = "http://localhost:8086" # INFLUX_URL:    dirección de la instancia local de InfluxDB.
INFLUX_TOKEN = "<tu-token-influxdb>" # INFLUX_TOKEN:  token de acceso generado en InfluxDB (permisos de lectura/escritura sobre el bucket).
INFLUX_ORG = "mi-org"                # INFLUX_ORG:    organización dentro de InfluxDB.
INFLUX_BUCKET = "pruebas"            # INFLUX_BUCKET: bucket (equivalente a "base de datos") donde se escriben los measurements.

# --- API de Kunak (fuente de datos real de polución) ---

KUNAK_BASE_URL = "https://kunakcloud.com/openAPIv0/v1/rest" # KUNAK_BASE_URL:  URL base de la API REST de Kunak.
KUNAK_USERNAME = "<usuario-web-kunak>"                      # KUNAK_USERNAME:  usuario de la web de Kunak. Se usa también como user_id en las rutas que lo piden.
KUNAK_PASSWORD = "<contraseña-web-kunak>"                   # KUNAK_PASSWORD:  contraseña. La autenticación es Basic Auth en cada petición (sin login por token).
KUNAK_DEVICE_ID = "<id-dispositivo>"                        # KUNAK_DEVICE_ID: identificador del dispositivo/estación cuyos sensores se consultan.

# --- API pública propia (/api/v1) ---

PUBLIC_API_KEY = "<clave-publica-para-API>" # Clave que deben enviar los clientes en la cabecera `X-API-Key` para acceder a /api/v1.
