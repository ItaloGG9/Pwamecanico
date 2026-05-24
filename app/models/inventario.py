import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric, SmallInteger, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(150))
    rut: Mapped[str | None] = mapped_column(String(12))
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    direccion: Mapped[str | None] = mapped_column(Text)
    notas: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    taller: Mapped["Taller"] = relationship(back_populates="clientes")  # type: ignore
    vehiculos: Mapped[list["Vehiculo"]] = relationship(back_populates="cliente", cascade="all, delete")
    cotizaciones: Mapped[list["Cotizacion"]] = relationship(back_populates="cliente")
    ordenes: Mapped[list["OrdenTrabajo"]] = relationship(back_populates="cliente")


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    cliente_id: Mapped[str] = mapped_column(String, ForeignKey("clientes.id", ondelete="CASCADE"))
    patente: Mapped[str] = mapped_column(String(10))
    marca: Mapped[str | None] = mapped_column(String(60))
    modelo: Mapped[str | None] = mapped_column(String(60))
    anio: Mapped[int | None] = mapped_column(SmallInteger)
    color: Mapped[str | None] = mapped_column(String(40))
    vin: Mapped[str | None] = mapped_column(String(17))
    km_actual: Mapped[int] = mapped_column(Integer, default=0)
    notas: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    cliente: Mapped["Cliente"] = relationship(back_populates="vehiculos")
    ordenes: Mapped[list["OrdenTrabajo"]] = relationship(back_populates="vehiculo")
    citas: Mapped[list["Cita"]] = relationship(back_populates="vehiculo")


class Proveedor(Base):
    __tablename__ = "proveedores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(150))
    rut: Mapped[str | None] = mapped_column(String(12))
    contacto: Mapped[str | None] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    condiciones: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    productos: Mapped[list["Producto"]] = relationship(back_populates="proveedor")


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    proveedor_id: Mapped[str | None] = mapped_column(String, ForeignKey("proveedores.id", ondelete="SET NULL"))
    nombre: Mapped[str] = mapped_column(String(150))
    sku: Mapped[str | None] = mapped_column(String(60))
    descripcion: Mapped[str | None] = mapped_column(Text)
    imagen_url: Mapped[str | None] = mapped_column(Text)
    compatibilidad: Mapped[str | None] = mapped_column(Text)
    stock_actual: Mapped[int] = mapped_column(Integer, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=1)
    precio_costo: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    precio_venta: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    unidad: Mapped[str] = mapped_column(String(20), default="unidad")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    taller: Mapped["Taller"] = relationship(back_populates="productos")  # type: ignore
    proveedor: Mapped["Proveedor"] = relationship(back_populates="productos")

    @property
    def bajo_stock(self) -> bool:
        return self.stock_actual <= self.stock_minimo
