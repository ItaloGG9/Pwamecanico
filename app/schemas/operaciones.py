from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── ITEMS ─────────────────────────────────────────────
class ItemCreate(BaseModel):
    tipo: str  # producto | servicio
    producto_id: Optional[str] = None
    descripcion: str
    cantidad: float = 1
    precio_unitario: float = 0


class ItemOut(BaseModel):
    id: str
    tipo: str
    producto_id: Optional[str]
    descripcion: str
    cantidad: float
    precio_unitario: float
    subtotal: float

    model_config = {"from_attributes": True}


# ── CITAS ─────────────────────────────────────────────
class CitaCreate(BaseModel):
    cliente_id: str
    vehiculo_id: Optional[str] = None
    mecanico_id: Optional[str] = None
    fecha_hora: datetime
    duracion_min: int = 60
    descripcion: Optional[str] = None


class CitaUpdate(BaseModel):
    mecanico_id: Optional[str] = None
    fecha_hora: Optional[datetime] = None
    duracion_min: Optional[int] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None


class CitaOut(BaseModel):
    id: str
    taller_id: str
    cliente_id: str
    vehiculo_id: Optional[str]
    mecanico_id: Optional[str]
    fecha_hora: datetime
    duracion_min: int
    descripcion: Optional[str]
    estado: str
    gcal_event_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── ÓRDENES DE TRABAJO ────────────────────────────────
class OTCreate(BaseModel):
    cliente_id: str
    vehiculo_id: str
    mecanico_id: Optional[str] = None
    cita_id: Optional[str] = None
    km_ingreso: Optional[int] = None
    nivel_combustible: Optional[int] = None
    diagnostico: Optional[str] = None
    fecha_entrega_est: Optional[datetime] = None
    items: List[ItemCreate] = []


class OTUpdateEstado(BaseModel):
    estado: str
    trabajo_realizado: Optional[str] = None
    notas_internas: Optional[str] = None
    fecha_entrega_est: Optional[datetime] = None


class OTOut(BaseModel):
    id: str
    taller_id: str
    numero_ot: str
    cliente_id: str
    vehiculo_id: str
    mecanico_id: Optional[str]
    estado: str
    km_ingreso: Optional[int]
    diagnostico: Optional[str]
    trabajo_realizado: Optional[str]
    fecha_ingreso: datetime
    fecha_entrega_est: Optional[datetime]
    total_neto: float
    total_iva: float
    total_final: float
    items: List[ItemOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ── COTIZACIONES ──────────────────────────────────────
class CotizacionCreate(BaseModel):
    cliente_id: str
    vehiculo_id: Optional[str] = None
    validez_dias: int = 7
    notas: Optional[str] = None
    items: List[ItemCreate] = []


class CotizacionOut(BaseModel):
    id: str
    taller_id: str
    numero: str
    cliente_id: str
    vehiculo_id: Optional[str]
    estado: str
    validez_dias: int
    total_neto: float
    total_iva: float
    total_final: float
    ot_id: Optional[str]
    items: List[ItemOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}
