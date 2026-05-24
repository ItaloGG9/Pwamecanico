from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.operaciones import OrdenTrabajo, OtItem
from app.schemas.operaciones import OTCreate, OTUpdateEstado, OTOut

router = APIRouter(prefix="/ordenes", tags=["Órdenes de trabajo"])

IVA = Decimal("0.19")


@router.get("", response_model=List[OTOut])
async def listar_ordenes(
    estado: str = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = (
        select(OrdenTrabajo)
        .where(OrdenTrabajo.taller_id == current_user.taller_id)
        .options(selectinload(OrdenTrabajo.items))
        .order_by(OrdenTrabajo.fecha_ingreso.desc())
    )
    if estado:
        q = q.where(OrdenTrabajo.estado == estado)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=OTOut, status_code=201)
async def crear_orden(
    data: OTCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Calcular totales
    neto = sum(Decimal(str(i.cantidad)) * Decimal(str(i.precio_unitario)) for i in data.items)
    iva = neto * IVA
    total = neto + iva

    ot = OrdenTrabajo(
        taller_id=current_user.taller_id,
        numero_ot="",  # el trigger de Supabase lo genera
        cliente_id=data.cliente_id,
        vehiculo_id=data.vehiculo_id,
        mecanico_id=data.mecanico_id,
        cita_id=data.cita_id,
        km_ingreso=data.km_ingreso,
        nivel_combustible=data.nivel_combustible,
        diagnostico=data.diagnostico,
        fecha_entrega_est=data.fecha_entrega_est,
        total_neto=neto,
        total_iva=iva,
        total_final=total,
    )
    db.add(ot)
    await db.flush()

    for item_data in data.items:
        item = OtItem(ot_id=ot.id, **item_data.model_dump())
        db.add(item)

    await db.commit()

    # Recargar con items
    result = await db.execute(
        select(OrdenTrabajo)
        .where(OrdenTrabajo.id == ot.id)
        .options(selectinload(OrdenTrabajo.items))
    )
    return result.scalar_one()


@router.get("/{ot_id}", response_model=OTOut)
async def obtener_orden(
    ot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(OrdenTrabajo)
        .where(OrdenTrabajo.id == ot_id, OrdenTrabajo.taller_id == current_user.taller_id)
        .options(selectinload(OrdenTrabajo.items))
    )
    ot = result.scalar_one_or_none()
    if not ot:
        raise HTTPException(status_code=404, detail="OT no encontrada")
    return ot


@router.patch("/{ot_id}/estado", response_model=OTOut)
async def cambiar_estado(
    ot_id: str,
    data: OTUpdateEstado,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(OrdenTrabajo)
        .where(OrdenTrabajo.id == ot_id, OrdenTrabajo.taller_id == current_user.taller_id)
        .options(selectinload(OrdenTrabajo.items))
    )
    ot = result.scalar_one_or_none()
    if not ot:
        raise HTTPException(status_code=404, detail="OT no encontrada")

    estados_validos = ["recibido", "diagnostico", "en_reparacion", "espera_repuesto", "listo", "entregado"]
    if data.estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {estados_validos}")

    for k, v in data.model_dump(exclude_none=True).items():
        setattr(ot, k, v)

    await db.commit()
    await db.refresh(ot)
    return ot
