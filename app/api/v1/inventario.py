from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import taller_key_builder, invalidate_taller_cache
from app.models.inventario import Producto
from app.schemas.inventario import ProductoCreate, ProductoUpdate, ProductoOut
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/productos", tags=["Inventario"])


@router.get("", response_model=List[ProductoOut])
@cache(expire=300, key_builder=taller_key_builder)
async def listar_productos(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Producto)
        .where(Producto.taller_id == current_user.taller_id, Producto.activo == True)
        .order_by(Producto.nombre)
    )
    return result.scalars().all()


@router.post("", response_model=ProductoOut, status_code=201)
async def crear_producto(
    data: ProductoCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    producto = Producto(taller_id=current_user.taller_id, **data.model_dump())
    db.add(producto)
    await db.commit()
    await db.refresh(producto)
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return producto


@router.get("/bajo-stock", response_model=List[ProductoOut])
@cache(expire=120, key_builder=taller_key_builder)
async def productos_bajo_stock(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Producto).where(
            Producto.taller_id == current_user.taller_id,
            Producto.activo == True,
            Producto.stock_actual <= Producto.stock_minimo,
        )
    )
    return result.scalars().all()


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
    background_tasks: BackgroundTasks,
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
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
    return p


@router.delete("/{producto_id}", status_code=204)
async def eliminar_producto(
    producto_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Producto).where(Producto.id == producto_id, Producto.taller_id == current_user.taller_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    p.activo = False
    await db.commit()
    background_tasks.add_task(invalidate_taller_cache, str(current_user.taller_id))
