from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.inventario import Producto
from app.schemas.inventario import ProductoCreate, ProductoUpdate, ProductoOut

router = APIRouter(prefix="/productos", tags=["Inventario"])


@router.get("", response_model=List[ProductoOut])
def listar_productos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Producto).filter(Producto.taller_id == current_user.taller_id, Producto.activo == True).order_by(Producto.nombre).all()


@router.post("", response_model=ProductoOut, status_code=201)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    producto = Producto(taller_id=current_user.taller_id, **data.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.get("/bajo-stock", response_model=List[ProductoOut])
def productos_bajo_stock(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    productos = db.query(Producto).filter(Producto.taller_id == current_user.taller_id, Producto.activo == True).all()
    return [p for p in productos if p.bajo_stock]


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = db.query(Producto).filter(Producto.id == producto_id, Producto.taller_id == current_user.taller_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p


@router.patch("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: str, data: ProductoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = db.query(Producto).filter(Producto.id == producto_id, Producto.taller_id == current_user.taller_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = db.query(Producto).filter(Producto.id == producto_id, Producto.taller_id == current_user.taller_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    p.activo = False
    db.commit()
