from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.operaciones import OrdenTrabajo, OtItem
from app.schemas.operaciones import OTCreate, OTUpdateEstado, OTOut

router = APIRouter(prefix="/ordenes", tags=["Órdenes de trabajo"])
IVA = Decimal("0.19")


@router.get("", response_model=List[OTOut])
def listar_ordenes(estado: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(OrdenTrabajo).filter(OrdenTrabajo.taller_id == current_user.taller_id)
    if estado:
        q = q.filter(OrdenTrabajo.estado == estado)
    return q.order_by(OrdenTrabajo.fecha_ingreso.desc()).all()


@router.post("", response_model=OTOut, status_code=201)
def crear_orden(data: OTCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
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
    db.flush()

    for item_data in data.items:
        db.add(OtItem(ot_id=ot.id, **item_data.model_dump()))

    db.commit()
    db.refresh(ot)
    return ot


@router.get("/{ot_id}", response_model=OTOut)
def obtener_orden(ot_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    ot = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == ot_id, OrdenTrabajo.taller_id == current_user.taller_id).first()
    if not ot:
        raise HTTPException(status_code=404, detail="OT no encontrada")
    return ot


@router.patch("/{ot_id}/estado", response_model=OTOut)
def cambiar_estado(ot_id: str, data: OTUpdateEstado, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    ot = db.query(OrdenTrabajo).filter(OrdenTrabajo.id == ot_id, OrdenTrabajo.taller_id == current_user.taller_id).first()
    if not ot:
        raise HTTPException(status_code=404, detail="OT no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(ot, k, v)
    db.commit()
    db.refresh(ot)
    return ot
