from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.inventario import Cliente, Vehiculo
from app.schemas.inventario import (
    ClienteCreate, ClienteUpdate, ClienteOut,
    VehiculoCreate, VehiculoUpdate, VehiculoOut,
)

router = APIRouter(tags=["Clientes y Vehículos"])


# ── CLIENTES ──────────────────────────────────────────
@router.get("/clientes", response_model=List[ClienteOut])
async def listar_clientes(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cliente)
        .where(Cliente.taller_id == current_user.taller_id)
        .order_by(Cliente.nombre)
    )
    return result.scalars().all()


@router.post("/clientes", response_model=ClienteOut, status_code=201)
async def crear_cliente(
    data: ClienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cliente = Cliente(taller_id=current_user.taller_id, **data.model_dump())
    db.add(cliente)
    await db.commit()
    await db.refresh(cliente)
    return cliente


@router.get("/clientes/{cliente_id}", response_model=ClienteOut)
async def obtener_cliente(
    cliente_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cliente).where(Cliente.id == cliente_id, Cliente.taller_id == current_user.taller_id)
    )
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.patch("/clientes/{cliente_id}", response_model=ClienteOut)
async def actualizar_cliente(
    cliente_id: str,
    data: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cliente).where(Cliente.id == cliente_id, Cliente.taller_id == current_user.taller_id)
    )
    cliente = result.scalar_one_or_none()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cliente, k, v)
    await db.commit()
    await db.refresh(cliente)
    return cliente


# ── VEHÍCULOS ─────────────────────────────────────────
@router.get("/clientes/{cliente_id}/vehiculos", response_model=List[VehiculoOut])
async def vehiculos_de_cliente(
    cliente_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Vehiculo).where(
            Vehiculo.cliente_id == cliente_id,
            Vehiculo.taller_id == current_user.taller_id,
        )
    )
    return result.scalars().all()


@router.post("/vehiculos", response_model=VehiculoOut, status_code=201)
async def crear_vehiculo(
    data: VehiculoCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vehiculo = Vehiculo(taller_id=current_user.taller_id, **data.model_dump())
    db.add(vehiculo)
    await db.commit()
    await db.refresh(vehiculo)
    return vehiculo


@router.get("/vehiculos/{vehiculo_id}", response_model=VehiculoOut)
async def obtener_vehiculo(
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Vehiculo).where(Vehiculo.id == vehiculo_id, Vehiculo.taller_id == current_user.taller_id)
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return v
