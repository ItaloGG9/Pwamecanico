from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.operaciones import Cotizacion, CotizacionItem, OrdenTrabajo, OtItem
from app.schemas.operaciones import CotizacionCreate, CotizacionOut, OTOut

router = APIRouter(prefix="/cotizaciones", tags=["Cotizaciones"])
IVA = Decimal("0.19")


@router.get("", response_model=List[CotizacionOut])
def listar_cotizaciones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Cotizacion).filter(Cotizacion.taller_id == current_user.taller_id).order_by(Cotizacion.created_at.desc()).all()


@router.post("", response_model=CotizacionOut, status_code=201)
def crear_cotizacion(data: CotizacionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
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
    db.flush()

    for item_data in data.items:
        db.add(CotizacionItem(cotizacion_id=cot.id, **item_data.model_dump()))

    db.commit()
    db.refresh(cot)
    return cot


@router.post("/{cotizacion_id}/aprobar", response_model=OTOut)
def aprobar_cotizacion(cotizacion_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cot = db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id, Cotizacion.taller_id == current_user.taller_id).first()
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
    db.flush()

    for ci in cot.items:
        db.add(OtItem(ot_id=ot.id, tipo=ci.tipo, producto_id=ci.producto_id, descripcion=ci.descripcion, cantidad=ci.cantidad, precio_unitario=ci.precio_unitario))

    cot.estado = "aprobada"
    cot.ot_id = ot.id
    db.commit()
    db.refresh(ot)
    return ot


@router.patch("/{cotizacion_id}/estado")
def cambiar_estado(cotizacion_id: str, estado: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cot = db.query(Cotizacion).filter(Cotizacion.id == cotizacion_id, Cotizacion.taller_id == current_user.taller_id).first()
    if not cot:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    cot.estado = estado
    db.commit()
    return {"ok": True, "estado": estado}
