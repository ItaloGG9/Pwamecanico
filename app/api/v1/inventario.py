from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.inventario import Producto
from app.schemas.inventario import ProductoCreate, ProductoUpdate, ProductoOut

router = APIRouter(prefix="/productos", tags=["Inventario"])


@router.get("", response_model=List[ProductoOut])
async def listar_productos(
    solo_bajo_stock: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = select(Producto).where(
        Producto.taller_id == current_user.taller_id,
        Producto.activo == True,
    )
    result = await db.execute(q.order_by(Producto.nombre))
    productos = result.scalars().all()
    if solo_bajo_stock:
        productos = [p for p in productos if p.bajo_stock]
    return productos


@router.post("", response_model=ProductoOut, status_code=201)
async def crear_producto(
    data: ProductoCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    producto = Producto(taller_id=current_user.taller_id, **data.model_dump())
    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    return producto


@router.get("/bajo-stock", response_model=List[ProductoOut])
async def productos_bajo_stock(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Producto).where(
            Producto.taller_id == current_user.taller_id,
            Producto.activo == True,
        )
    )
    return [p for p in result.scalars().all() if p.bajo_stock]


@router.get("/{producto_id}", response_model=ProductoOut)
async def obtener_producto(
    producto_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id == producto_id, Producto.taller_id == current_user.taller_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p


@router.patch("/{producto_id}", response_model=ProductoOut)
async def actualizar_producto(
    producto_id: str,
    data: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id == producto_id, Producto.taller_id == current_user.taller_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return p


@router.delete("/{producto_id}", status_code=204)
async def eliminar_producto(
    producto_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id == producto_id, Producto.taller_id == current_user.taller_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    p.activo = False  # Soft delete
    await db.commit()
