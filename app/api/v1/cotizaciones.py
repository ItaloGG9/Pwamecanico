from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.operaciones import Cotizacion, CotizacionItem, OrdenTrabajo, OtItem
from app.schemas.operaciones import CotizacionCreate, CotizacionOut, OTOut

router = APIRouter(prefix="/cotizaciones", tags=["Cotizaciones"])

IVA = Decimal("0.19")


@router.get("", response_model=List[CotizacionOut])
async def listar_cotizaciones(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cotizacion)
        .where(Cotizacion.taller_id == current_user.taller_id)
        .options(selectinload(Cotizacion.items))
        .order_by(Cotizacion.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=CotizacionOut, status_code=201)
async def crear_cotizacion(
    data: CotizacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    neto = sum(Decimal(str(i.cantidad)) * Decimal(str(i.precio_unitario)) for i in data.items)
    iva = neto * IVA
    total = neto + iva

    cotizacion = Cotizacion(
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
    db.add(cotizacion)
    await db.flush()

    for item_data in data.items:
        item = CotizacionItem(cotizacion_id=cotizacion.id, **item_data.model_dump())
        db.add(item)

    await db.commit()
    result = await db.execute(
        select(Cotizacion)
        .where(Cotizacion.id == cotizacion.id)
        .options(selectinload(Cotizacion.items))
    )
    return result.scalar_one()


@router.post("/{cotizacion_id}/aprobar", response_model=OTOut)
async def aprobar_y_convertir_a_ot(
    cotizacion_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Aprueba la cotización y la convierte en Orden de Trabajo."""
    result = await db.execute(
        select(Cotizacion)
        .where(Cotizacion.id == cotizacion_id, Cotizacion.taller_id == current_user.taller_id)
        .options(selectinload(Cotizacion.items))
    )
    cot = result.scalar_one_or_none()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    if cot.estado != "enviada":
        raise HTTPException(status_code=400, detail="Solo se pueden aprobar cotizaciones enviadas")

    # Crear OT desde cotización
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
    return result.scalar_one()


@router.patch("/{cotizacion_id}/estado")
async def cambiar_estado_cotizacion(
    cotizacion_id: str,
    estado: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cotizacion)
        .where(Cotizacion.id == cotizacion_id, Cotizacion.taller_id == current_user.taller_id)
    )
    cot = result.scalar_one_or_none()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    cot.estado = estado
    await db.commit()
    return {"ok": True, "estado": estado}
