from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.inventario import Cliente, Vehiculo
from app.schemas.inventario import (
    ClienteCreate, ClienteUpdate, ClienteOut,
    VehiculoCreate, VehiculoUpdate, VehiculoOut,
)

router = APIRouter(tags=["Clientes y Vehículos"])


@router.get("/clientes", response_model=List[ClienteOut])
def listar_clientes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Cliente).filter(Cliente.taller_id == current_user.taller_id).order_by(Cliente.nombre).all()


@router.post("/clientes", response_model=ClienteOut, status_code=201)
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cliente = Cliente(taller_id=current_user.taller_id, **data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.get("/clientes/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(cliente_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.taller_id == current_user.taller_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.patch("/clientes/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(cliente_id: str, data: ClienteUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id, Cliente.taller_id == current_user.taller_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cliente, k, v)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.get("/clientes/{cliente_id}/vehiculos", response_model=List[VehiculoOut])
def vehiculos_de_cliente(cliente_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Vehiculo).filter(Vehiculo.cliente_id == cliente_id, Vehiculo.taller_id == current_user.taller_id).all()


@router.post("/vehiculos", response_model=VehiculoOut, status_code=201)
def crear_vehiculo(data: VehiculoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    vehiculo = Vehiculo(taller_id=current_user.taller_id, **data.model_dump())
    db.add(vehiculo)
    db.commit()
    db.refresh(vehiculo)
    return vehiculo


@router.get("/vehiculos/{vehiculo_id}", response_model=VehiculoOut)
def obtener_vehiculo(vehiculo_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    v = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id, Vehiculo.taller_id == current_user.taller_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return v
