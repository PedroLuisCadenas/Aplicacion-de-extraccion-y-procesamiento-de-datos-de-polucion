# Aplicación de extracción y procesamiento de datos de polución

Aplicación de **extracción, almacenamiento y visualización de datos de polución ambiental**, desarrollada como Trabajo de Fin de Grado (TFG).

Un daemon recolecta periódicamente las lecturas de una estación de calidad del aire a través de la **API REST de Kunak**, las almacena en una base de datos de series temporales (**InfluxDB**) y las expone mediante una **API REST propia** (FastAPI) que consume una **aplicación web en Angular**.

---

## Contenido

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos previos](#requisitos-previos)
- [Instalación y configuración](#instalación-y-configuración)
- [Puesta en marcha](#puesta-en-marcha)
- [API REST pública (`/api/v1`)](#api-rest-pública-apiv1)
- [Relleno de histórico (backfill)](#relleno-de-histórico-backfill)
- [Notas sobre la fuente de datos (Kunak)](#notas-sobre-la-fuente-de-datos-kunak)
- [Trabajo futuro](#trabajo-futuro)
- [Autor](#autor)

---

## Características

- **Recolección automática** de datos cada 30 minutos mediante un daemon (`main.py`), guardando **todas** las lecturas de la ventana, no solo la última de cada sensor.
- **Almacenamiento en InfluxDB 1.12** (InfluxQL) en cuatro *measurements*: `pollution` (lecturas), `device_info`, `device_elements` (catálogo de sensores) y `user_info`.
- **API REST** con FastAPI:
  - Namespace público `/api/v1/...` de solo lectura, autenticado con cabecera `X-API-Key`.
  - Namespace interno para la aplicación web (info de usuario, lanzamiento de *backfill*).
  - Documentación automática (Swagger) en `/docs`.
- **Aplicación web Angular 20** con:
  - **Inicio**: tarjetas con el último valor de las 12 variables principales, cada una con su mini-gráfica de los últimos 7 días.
  - **Datos**: consulta del histórico por sensor, con presets de intervalo o rango de fechas personalizado, y exportación a CSV.
  - **Gráficas**: comparador multi-sensor con selección por buscador, estadísticas del intervalo (media / mín / máx), tabla paginada y exportación a CSV.
  - **Dispositivo / Usuario / Ayuda**: información de la estación y de la cuenta, y catálogo de sensores con descripción.
- **Script de *backfill*** (`backfill.py`) para poblar la base de datos con histórico de golpe, sin esperar al daemon.
- Diseñado teniendo en cuenta los **límites de la API de Kunak** (10 peticiones/segundo y 10.000 peticiones/mes): el histórico siempre se sirve desde InfluxDB, nunca repitiendo consultas amplias contra Kunak.

---

## Arquitectura

```
                 ┌─────────────┐
                 │  Kunak API  │  (fuente de datos real, Basic Auth)
                 └──────┬──────┘
                        │  cada 30 min
                        ▼
                 ┌─────────────┐        ┌──────────────────┐
                 │   main.py   │        │   backfill.py    │  (relleno puntual)
                 │  (daemon)   │        └────────┬─────────┘
                 └──────┬──────┘                 │
                        ▼                        ▼
                 ┌────────────────────────────────────┐
                 │  influx_client.py  (escritura)     │
                 └──────────────────┬─────────────────┘
                                    ▼
                          ┌──────────────────┐
                          │   InfluxDB 1.12  │  (series temporales)
                          └────────┬─────────┘
                                   ▼
                 ┌────────────────────────────────────┐
                 │  influx_reader.py  (consulta)      │
                 └──────────────────┬─────────────────┘
                                    ▼
                          ┌──────────────────┐
                          │ server.py (API)  │  FastAPI · puerto 8200
                          │  /api/v1 + interno│
                          └────────┬─────────┘
                                   ▼
                          ┌──────────────────┐
                          │  Frontend Angular │  puerto 4200
                          └──────────────────┘
```

---

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| Backend / API | Python 3 · FastAPI · Uvicorn |
| Base de datos | InfluxDB 1.12 (InfluxQL) · cliente Python `influxdb` |
| Frontend | Angular 20 (standalone components) · Chart.js + ng2-charts |
| Fuente de datos | API REST de Kunak (Basic Auth) |

---

## Estructura del repositorio

```
backend/
├── main.py            # Daemon de recolección (bucle cada 30 min)
├── server.py          # Servidor FastAPI: monta /api/v1 + endpoints internos
├── public_api.py      # Router público /api/v1 (solo lectura, X-API-Key)
├── api_client.py      # Cliente HTTP de la API de Kunak
├── influx_client.py   # Escritura en InfluxDB
├── influx_reader.py   # Lectura / consulta de InfluxDB (InfluxQL)
├── backfill.py        # Script de relleno de histórico
├── config.example.py  # Plantilla de configuración (cópiala como config.py)
└── requirements.txt

frontend/
└── pollution-app/     # Aplicación Angular (ng serve en :4200)
    └── src/app/
        ├── core/                 # Servicio Api, interceptor de X-API-Key, catálogo de sensores
        └── features/
            ├── dashboard/        # "Inicio"
            ├── sensors-readings/ # "Datos"
            ├── charts/           # "Gráficas"
            ├── dispositivo/      # "Dispositivo"
            ├── usuario/          # "Usuario"
            └── ayuda/            # "Ayuda"
```

Los archivos con credenciales (`backend/config.py`, `frontend/pollution-app/src/environments/environment*.ts`) están en `.gitignore` y **no se incluyen en el repositorio**. Usa las plantillas `*.example.*` como punto de partida.

---

## Requisitos previos

- **Python 3.10+**
- **Node.js 20 o 22** y **Angular CLI 20** (`npm install -g @angular/cli@20`)
- **InfluxDB 1.12** (InfluxQL). Descarga: <https://portal.influxdata.com/downloads/> (rama 1.x)
- Credenciales de la **API de Kunak** y el identificador del dispositivo/estación a consultar

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/PedroLuisCadenas/Aplicacion-de-extraccion-y-procesamiento-de-datos-de-polucion.git
cd Aplicacion-de-extraccion-y-procesamiento-de-datos-de-polucion
```

### 2. Base de datos InfluxDB

Arranca el servidor (`influxd`) y crea la base de datos la primera vez:

```bash
influx            # abre la CLI
> CREATE DATABASE pruebas
```

> En Windows, usa `127.0.0.1` en lugar de `localhost` para conectar (`influx -host 127.0.0.1`).

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt

cp config.example.py config.py     # y rellena los valores reales
```

`config.py` (no versionado) debe contener:

| Variable | Descripción |
|----------|-------------|
| `INFLUX_HOST` / `INFLUX_PORT` / `INFLUX_SSL` | Conexión a InfluxDB (por defecto `127.0.0.1:8086`, sin SSL) |
| `INFLUX_DATABASE` | Nombre de la base de datos (p. ej. `pruebas`) |
| `INFLUX_USERNAME` / `INFLUX_PASSWORD` | Vacíos si InfluxDB no tiene autenticación |
| `KUNAK_BASE_URL` | URL base de la API REST de Kunak |
| `KUNAK_USERNAME` / `KUNAK_PASSWORD` | Credenciales de Kunak (Basic Auth) |
| `KUNAK_DEVICE_ID` | Identificador de la estación cuyos sensores se consultan |
| `PUBLIC_API_KEY` | Clave que los clientes deben enviar en la cabecera `X-API-Key` para acceder a `/api/v1` |

### 4. Frontend

```bash
cd frontend/pollution-app
npm install

cp src/environments/environment.example.ts src/environments/environment.ts
cp src/environments/environment.example.ts src/environments/environment.development.ts
```

Edita ambos archivos:

```ts
export const environment = {
  production: true,                       // false en environment.development.ts
  apiUrl: 'http://localhost:8200',        // URL del backend
  apiKey: '<misma clave que PUBLIC_API_KEY>',
};
```

> Si vas a acceder desde otro dispositivo de la red, pon en `apiUrl` la IP de la máquina que sirve el backend y añade ese origen a `allow_origins` en `backend/server.py`.

---

## Puesta en marcha

Necesitas **tres procesos** en marcha (InfluxDB aparte):

```bash
# 1. Daemon de recolección (backend/)
python main.py

# 2. API REST (backend/)
python server.py          # http://localhost:8200  ·  Swagger en /docs

# 3. Aplicación web (frontend/pollution-app/)
npm start                 # http://localhost:4200
```

El daemon y la API pueden ejecutarse de forma independiente: la API solo lee de InfluxDB, así que funciona aunque el daemon no esté corriendo (mostrará los datos ya almacenados).

---

## API REST pública (`/api/v1`)

Todas las rutas requieren la cabecera `X-API-Key` con el valor de `PUBLIC_API_KEY`. Sin ella (o con una clave incorrecta) se devuelve `401`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/device/info/latest` | Última información del dispositivo |
| GET | `/api/v1/device/readings/latest` | Última lectura de cada sensor |
| GET | `/api/v1/device/readings` | Histórico de lecturas |
| GET | `/api/v1/device/elements` | Catálogo de sensores (nombre + unidad) |

Parámetros de `/api/v1/device/readings`:

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `hours` | int | Últimas N horas (por defecto 24). Se ignora si se indica `start` |
| `start` / `end` | ISO 8601 | Rango concreto (`end` por defecto: ahora) |
| `element_id` | string | Filtra por un único sensor |

Ejemplo:

```bash
curl -H "X-API-Key: TU_CLAVE" \
  "http://localhost:8200/api/v1/device/readings?hours=48&element_id=Temp%20ext"
```

---

## Relleno de histórico (backfill)

`backfill.py` descarga de golpe los últimos *N* días de todas las lecturas de todos los sensores y las escribe en InfluxDB. Es **idempotente** (relanzarlo no duplica datos) y puede ejecutarse mientras el daemon está en marcha.

```bash
cd backend
python backfill.py            # 14 días (por defecto)
python backfill.py 30         # 30 días
python backfill.py 3650       # todo el histórico disponible (se detiene solo al agotarlo)
```

También se puede lanzar desde la aplicación web (**Dispositivo → Rellenar histórico**), con un límite de 60 días por seguridad.

---

## Notas sobre la fuente de datos (Kunak)

- **Autenticación**: Basic Auth (usuario/contraseña) en cada petición.
- **Límite de tasa**: 10 peticiones/segundo. El cliente aplica un *throttle* a 8 req/s y reintenta ante un `429`.
- **Cuota mensual**: 10.000 peticiones/mes. Es la restricción de diseño dominante: el daemon hace 4 peticiones por ciclo cada 30 minutos (~5.760/mes) y las consultas de histórico se sirven **siempre desde InfluxDB**, nunca repitiendo consultas amplias contra Kunak.

---

## Trabajo futuro

- Información ampliada de la estación en la sección **Dispositivo**: mapa con la ubicación y foto de la estación.
- Categorización de sensores por familias (calidad del aire, partículas, climáticos, viento…) en el selector del comparador.
- Pantallas de **Reportes** y **Configuración**.
- Gestión de cuentas de usuario.

---

## Autor

Trabajo de Fin de Grado · [@PedroLuisCadenas](https://github.com/PedroLuisCadenas)
