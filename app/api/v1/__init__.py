from fastapi import APIRouter
from app.api.v1 import auth, clientes, inventario, ordenes, cotizaciones, citas

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(clientes.router)
api_router.include_router(inventario.router)
api_router.include_router(ordenes.router)
api_router.include_router(cotizaciones.router)
api_router.include_router(citas.router)
