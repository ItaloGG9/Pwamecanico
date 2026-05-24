import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class Cita(Base):
    __tablename__ = "citas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    cliente_id: Mapped[str] = mapped_column(String, ForeignKey("clientes.id", ondelete="CASCADE"))
    vehiculo_id: Mapped[str | None] = mapped_column(String, ForeignKey("vehiculos.id", ondelete="SET NULL"))
    mecanico_id: Mapped[str | None] = mapped_column(String, ForeignKey("usuarios.id", ondelete="SET NULL"))
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duracion_min: Mapped[int] = mapped_column(Integer, default=60)
    descripcion: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    gcal_event_id: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    cliente: Mapped["Cliente"] = relationship(back_populates="citas")  # type: ignore
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="citas")  # type: ignore


class OrdenTrabajo(Base):
    __tablename__ = "ordenes_trabajo"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    numero_ot: Mapped[str] = mapped_column(String(20), default="")
    cita_id: Mapped[str | None] = mapped_column(String, ForeignKey("citas.id", ondelete="SET NULL"))
    cliente_id: Mapped[str] = mapped_column(String, ForeignKey("clientes.id"))
    vehiculo_id: Mapped[str] = mapped_column(String, ForeignKey("vehiculos.id"))
    mecanico_id: Mapped[str | None] = mapped_column(String, ForeignKey("usuarios.id", ondelete="SET NULL"))
    estado: Mapped[str] = mapped_column(String(30), default="recibido")
    km_ingreso: Mapped[int | None] = mapped_column(Integer)
    nivel_combustible: Mapped[int | None] = mapped_column(SmallInteger)
    diagnostico: Mapped[str | None] = mapped_column(Text)
    trabajo_realizado: Mapped[str | None] = mapped_column(Text)
    fecha_ingreso: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    fecha_entrega_est: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_entrega_real: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_neto: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_iva: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_final: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    notas_internas: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    cliente: Mapped["Cliente"] = relationship(back_populates="ordenes")  # type: ignore
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="ordenes")  # type: ignore
    items: Mapped[list["OtItem"]] = relationship(back_populates="orden", cascade="all, delete")


class OtItem(Base):
    __tablename__ = "ot_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ot_id: Mapped[str] = mapped_column(String, ForeignKey("ordenes_trabajo.id", ondelete="CASCADE"))
    tipo: Mapped[str] = mapped_column(String(15))
    producto_id: Mapped[str | None] = mapped_column(String, ForeignKey("productos.id", ondelete="SET NULL"))
    descripcion: Mapped[str] = mapped_column(Text)
    cantidad: Mapped[float] = mapped_column(Numeric(10, 2), default=1)
    precio_unitario: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    orden: Mapped["OrdenTrabajo"] = relationship(back_populates="items")

    @property
    def subtotal(self) -> float:
        return float(self.cantidad) * float(self.precio_unitario)


class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    numero: Mapped[str] = mapped_column(String(20), default="")
    cliente_id: Mapped[str] = mapped_column(String, ForeignKey("clientes.id"))
    vehiculo_id: Mapped[str | None] = mapped_column(String, ForeignKey("vehiculos.id", ondelete="SET NULL"))
    estado: Mapped[str] = mapped_column(String(20), default="borrador")
    validez_dias: Mapped[int] = mapped_column(Integer, default=7)
    notas: Mapped[str | None] = mapped_column(Text)
    total_neto: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_iva: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_final: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    ot_id: Mapped[str | None] = mapped_column(String, ForeignKey("ordenes_trabajo.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    cliente: Mapped["Cliente"] = relationship(back_populates="cotizaciones")  # type: ignore
    items: Mapped[list["CotizacionItem"]] = relationship(back_populates="cotizacion", cascade="all, delete")


class CotizacionItem(Base):
    __tablename__ = "cotizacion_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cotizacion_id: Mapped[str] = mapped_column(String, ForeignKey("cotizaciones.id", ondelete="CASCADE"))
    tipo: Mapped[str] = mapped_column(String(15))
    producto_id: Mapped[str | None] = mapped_column(String, ForeignKey("productos.id", ondelete="SET NULL"))
    descripcion: Mapped[str] = mapped_column(Text)
    cantidad: Mapped[float] = mapped_column(Numeric(10, 2), default=1)
    precio_unitario: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    cotizacion: Mapped["Cotizacion"] = relationship(back_populates="items")

    @property
    def subtotal(self) -> float:
        return float(self.cantidad) * float(self.precio_unitario)
