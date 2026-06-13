# Copia este fichero como config.py y rellena los valores reales.
# config.py está en .gitignore y NO debe subirse al repositorio.

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "<tu-token-influxdb>"
INFLUX_ORG = "mi-org"
INFLUX_BUCKET = "pruebas"

KUNAK_BASE_URL = "https://kunakcloud.com/openAPIv0/v1/rest"
KUNAK_USERNAME = "<email-o-usuario-kunak>"
KUNAK_PASSWORD = "<contraseña-kunak>"
KUNAK_TOKEN = "<token-api-kunak>"        # alternativa a contraseña si el tutor la confirma
KUNAK_USER_ID = ""                       # obtener ejecutando: python kunak_discover.py
KUNAK_DEVICE_ID = ""                     # obtener ejecutando: python kunak_discover.py
