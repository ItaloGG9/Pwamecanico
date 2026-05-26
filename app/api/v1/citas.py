from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.operaciones import Cita
from app.schemas.operaciones import CitaCreate, CitaUpdate, CitaOut

router = APIRouter(prefix="/citas", tags=["Agenda"])


@router.get("", response_model=List[CitaOut])
def listar_citas(fecha: Optional[date] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from sqlalchemy import func
    q = db.query(Cita).filter(Cita.taller_id == current_user.taller_id)
    if fecha:
        q = q.filter(func.date(Cita.fecha_hora) == fecha)
    return q.order_by(Cita.fecha_hora).all()


@router.post("", response_model=CitaOut, status_code=201)
def crear_cita(data: CitaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cita = Cita(taller_id=current_user.taller_id, **data.model_dump())
    db.add(cita)
    db.commit()
    db.refresh(cita)
    return cita


@router.patch("/{cita_id}", response_model=CitaOut)
def actualizar_cita(cita_id: str, data: CitaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id, Cita.taller_id == current_user.taller_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cita, k, v)
    db.commit()
    db.refresh(cita)
    return cita


@router.delete("/{cita_id}", status_code=204)
def cancelar_cita(cita_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cita = db.query(Cita).filter(Cita.id == cita_id, Cita.taller_id == current_user.taller_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    cita.estado = "cancelada"
    db.commit()
