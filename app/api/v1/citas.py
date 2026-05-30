from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import taller_key_builder, invalidate_taller_cache
from app.models.operaciones import Cita
from app.schemas.operaciones import CitaCreate, CitaUpdate, CitaOut
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/citas", tags=["Agenda"])


@router.get("", response_model=List[CitaOut])
@cache(expire=60, key_builder=taller_key_builder)
async def listar_citas(
    fecha: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    stmt = (
        select(Cita)
        .where(Cita.taller_id == current_user.taller_id)
        .order_by(Cita.fecha_hora)
    )
    if fecha:
        stmt = stmt.where(func.date(Cita.fecha_hora) == fecha)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=CitaOut, status_code=201)
async def crear_cita(
    data: CitaCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cita = Cita(taller_id=current_user.taller_id, **data.model_dump())
    db.add(cita)
    await db.commit()
    await db.refresh(cita)
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return cita


@router.patch("/{cita_id}", response_model=CitaOut)
async def actualizar_cita(
    cita_id: str,
    data: CitaUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cita).where(Cita.id == cita_id, Cita.taller_id == current_user.taller_id)
    )
    cita = result.scalar_one_or_none()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cita, k, v)
    await db.commit()
    await db.refresh(cita)
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return cita


@router.delete("/{cita_id}", status_code=204)
async def cancelar_cita(
    cita_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Cita).where(Cita.id == cita_id, Cita.taller_id == current_user.taller_id)
    )
    cita = result.scalar_one_or_none()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    cita.estado = "cancelada"
    await db.commit()
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
