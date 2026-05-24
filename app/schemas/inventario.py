from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── CLIENTES ──────────────────────────────────────────
class ClienteCreate(BaseModel):
    nombre: str
    rut: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    notas: Optional[str] = None


class ClienteUpdate(ClienteCreate):
    nombre: Optional[str] = None


class ClienteOut(BaseModel):
    id: str
    taller_id: str
    nombre: str
    rut: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── VEHÍCULOS ─────────────────────────────────────────
class VehiculoCreate(BaseModel):
    cliente_id: str
    patente: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    km_actual: int = 0
    notas: Optional[str] = None


class VehiculoUpdate(VehiculoCreate):
    cliente_id: Optional[str] = None
    patente: Optional[str] = None


class VehiculoOut(BaseModel):
    id: str
    taller_id: str
    cliente_id: str
    patente: str
    marca: Optional[str]
    modelo: Optional[str]
    anio: Optional[int]
    color: Optional[str]
    km_actual: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── PRODUCTOS ─────────────────────────────────────────
class ProductoCreate(BaseModel):
    nombre: str
    sku: Optional[str] = None
    descripcion: Optional[str] = None
    compatibilidad: Optional[str] = None
    stock_actual: int = 0
    stock_minimo: int = 1
    precio_costo: float = 0
    precio_venta: float = 0
    unidad: str = "unidad"
    proveedor_id: Optional[str] = None


class ProductoUpdate(ProductoCreate):
    nombre: Optional[str] = None


class ProductoOut(BaseModel):
    id: str
    taller_id: str
    nombre: str
    sku: Optional[str]
    stock_actual: int
    stock_minimo: int
    precio_venta: float
    imagen_url: Optional[str]
    bajo_stock: bool
    activo: bool

    model_config = {"from_attributes": True}
