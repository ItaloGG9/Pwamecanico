from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TallerCreate(BaseModel):
    nombre: str
    rut: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None


class TallerOut(BaseModel):
    id: str
    nombre: str
    rut: Optional[str]
    email: Optional[str]
    plan: str
    logo_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: str = "mecanico"


class UsuarioOut(BaseModel):
    id: str
    taller_id: str
    nombre: str
    email: str
    rol: str
    activo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


class RegisterRequest(BaseModel):
    taller: TallerCreate
    usuario: UsuarioCreate
