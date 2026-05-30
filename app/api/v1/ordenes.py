from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import taller_key_builder, invalidate_taller_cache
from app.models.operaciones import OrdenTrabajo, OtItem
from app.schemas.operaciones import OTCreate, OTUpdateEstado, OTOut
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/ordenes", tags=["Órdenes de trabajo"])
IVA = Decimal("0.19")


def _ot_options():
    return selectinload(OrdenTrabajo.items)


@router.get("", response_model=List[OTOut])
@cache(expire=30, key_builder=taller_key_builder)
async def listar_ordenes(
    estado: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    stmt = (
        select(OrdenTrabajo)
        .where(OrdenTrabajo.taller_id == current_user.taller_id)
        .options(_ot_options())
        .order_by(OrdenTrabajo.fecha_ingreso.desc())
    )
    if estado:
        stmt = stmt.where(OrdenTrabajo.estado == estado)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=OTOut, status_code=201)
async def crear_orden(
    data: OTCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    neto = sum(Decimal(str(i.cantidad)) * Decimal(str(i.precio_unitario)) for i in data.items)
    iva = neto * IVA
    total = neto + iva

    ot = OrdenTrabajo(
        taller_id=current_user.taller_id,
        numero_ot="",
        cliente_id=data.cliente_id,
        vehiculo_id=data.vehiculo_id,
        mecanico_id=data.mecanico_id,
        cita_id=data.cita_id,
        km_ingreso=data.km_ingreso,
        diagnostico=data.diagnostico,
        fecha_entrega_est=data.fecha_entrega_est,
        total_neto=neto,
        total_iva=iva,
        total_final=total,
    )
    db.add(ot)
    await db.flush()

    for item_data in data.items:
        db.add(OtItem(ot_id=ot.id, **item_data.model_dump()))

    await db.commit()

    result = await db.execute(
        select(OrdenTrabajo).where(OrdenTrabajo.id == ot.id).options(_ot_options())
    )
    ot = result.scalar_one()
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return ot


@router.get("/{ot_id}", response_model=OTOut)
async def obtener_orden(
    ot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(OrdenTrabajo)
        .where(OrdenTrabajo.id == ot_id, OrdenTrabajo.taller_id == current_user.taller_id)
        .options(_ot_options())
    )
    ot = result.scalar_one_or_none()
    if not ot:
        raise HTTPException(status_code=404, detail="OT no encontrada")
    return ot


@router.patch("/{ot_id}/estado", response_model=OTOut)
async def cambiar_estado(
    ot_id: str,
    data: OTUpdateEstado,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(OrdenTrabajo)
        .where(OrdenTrabajo.id == ot_id, OrdenTrabajo.taller_id == current_user.taller_id)
        .options(_ot_options())
    )
    ot = result.scalar_one_or_none()
    if not ot:
        raise HTTPException(status_code=404, detail="OT no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(ot, k, v)
    await db.commit()
    await db.refresh(ot)
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return ot
