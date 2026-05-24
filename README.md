# PWAmecanico — Backend API

Backend REST para el sistema de gestión de talleres automotrices.
Construido con **FastAPI + SQLAlchemy 2 + PostgreSQL (Supabase)**.

## Stack

- Python 3.12
- FastAPI 0.111
- SQLAlchemy 2 (async)
- PostgreSQL via Supabase
- Deploy en Railway

## Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/pwamecanico-backend.git
cd pwamecanico-backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase

# 5. Levantar el servidor
uvicorn app.main:app --reload --port 8000
```

## Variables de entorno requeridas

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | URL de conexión a Supabase PostgreSQL |
| `SECRET_KEY` | Clave secreta para JWT (mín. 32 caracteres) |
| `ALLOWED_ORIGINS` | URLs del frontend separadas por coma |

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/auth/register` | Registrar taller + admin |
| POST | `/api/v1/auth/login` | Iniciar sesión |
| GET | `/api/v1/auth/me` | Usuario actual |
| GET | `/api/v1/clientes` | Listar clientes |
| POST | `/api/v1/clientes` | Crear cliente |
| GET | `/api/v1/productos` | Inventario |
| GET | `/api/v1/productos/bajo-stock` | Alertas de stock |
| GET | `/api/v1/ordenes` | Órdenes de trabajo |
| POST | `/api/v1/ordenes` | Crear OT |
| PATCH | `/api/v1/ordenes/{id}/estado` | Cambiar estado OT |
| GET | `/api/v1/cotizaciones` | Cotizaciones |
| POST | `/api/v1/cotizaciones/{id}/aprobar` | Convertir a OT |
| GET | `/api/v1/citas` | Agenda |
| GET | `/health` | Health check |

## Deploy en Railway

1. Subir código a GitHub
2. Crear nuevo proyecto en Railway → "Deploy from GitHub"
3. Agregar las variables de entorno en Railway → Variables
4. Railway detecta el `Dockerfile` automáticamente
5. El `railway.toml` configura el health check en `/health`

## Documentación interactiva

Disponible en modo DEBUG en:
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
