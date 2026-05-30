from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import taller_key_builder, invalidate_taller_cache
from app.models.operaciones import Cotizacion, CotizacionItem, OrdenTrabajo, OtItem
from app.schemas.operaciones import CotizacionCreate, CotizacionOut, OTOut
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/cotizaciones", tags=["Cotizaciones"])
IVA = Decimal("0.19")


def _cot_options():
    return selectinload(Cotizacion.items)


@router.get("", response_model=List[CotizacionOut])
@cache(expire=60, key_builder=taller_key_builder)
async def listar_cotizaciones(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cotizacion)
        .where(Cotizacion.taller_id == current_user.taller_id)
        .options(_cot_options())
        .order_by(Cotizacion.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=CotizacionOut, status_code=201)
async def crear_cotizacion(
    data: CotizacionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    neto = sum(Decimal(str(i.cantidad)) * Decimal(str(i.precio_unitario)) for i in data.items)
    iva = neto * IVA
    total = neto + iva

    cot = Cotizacion(
        taller_id=current_user.taller_id,
        numero="",
        cliente_id=data.cliente_id,
        vehiculo_id=data.vehiculo_id,
        validez_dias=data.validez_dias,
        notas=data.notas,
        total_neto=neto,
        total_iva=iva,
        total_final=total,
    )
    db.add(cot)
    await db.flush()

    for item_data in data.items:
        db.add(CotizacionItem(cotizacion_id=cot.id, **item_data.model_dump()))

    await db.commit()

    result = await db.execute(
        select(Cotizacion).where(Cotizacion.id == cot.id).options(_cot_options())
    )
    cot = result.scalar_one()
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return cot


@router.post("/{cotizacion_id}/aprobar", response_model=OTOut)
async def aprobar_cotizacion(
    cotizacion_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cotizacion)
        .where(Cotizacion.id == cotizacion_id, Cotizacion.taller_id == current_user.taller_id)
        .options(_cot_options())
    )
    cot = result.scalar_one_or_none()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    if cot.estado != "enviada":
        raise HTTPException(status_code=400, detail="Solo se pueden aprobar cotizaciones enviadas")

    ot = OrdenTrabajo(
        taller_id=current_user.taller_id,
        numero_ot="",
        cliente_id=cot.cliente_id,
        vehiculo_id=cot.vehiculo_id,
        total_neto=cot.total_neto,
        total_iva=cot.total_iva,
        total_final=cot.total_final,
    )
    db.add(ot)
    await db.flush()

    for ci in cot.items:
        db.add(OtItem(
            ot_id=ot.id,
            tipo=ci.tipo,
            producto_id=ci.producto_id,
            descripcion=ci.descripcion,
            cantidad=ci.cantidad,
            precio_unitario=ci.precio_unitario,
        ))

    cot.estado = "aprobada"
    cot.ot_id = ot.id
    await db.commit()

    result = await db.execute(
        select(OrdenTrabajo)
        .where(OrdenTrabajo.id == ot.id)
        .options(selectinload(OrdenTrabajo.items))
    )
    ot = result.scalar_one()
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return ot


@router.patch("/{cotizacion_id}/estado")
async def cambiar_estado(
    cotizacion_id: str,
    estado: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cotizacion).where(
            Cotizacion.id == cotizacion_id,
            Cotizacion.taller_id == current_user.taller_id,
        )
    )
    cot = result.scalar_one_or_none()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    cot.estado = estado
    await db.commit()
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return {"ok": True, "estado": estado}
