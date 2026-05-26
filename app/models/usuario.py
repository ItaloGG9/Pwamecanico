import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class Taller(Base):
    __tablename__ = "talleres"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre: Mapped[str] = mapped_column(String(100))
    rut: Mapped[str | None] = mapped_column(String(12))
    direccion: Mapped[str | None] = mapped_column(Text)
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(150))
    logo_url: Mapped[str | None] = mapped_column(Text)
    plan: Mapped[str] = mapped_column(String(20), default="starter")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="taller", cascade="all, delete")
    clientes: Mapped[list["Cliente"]] = relationship(back_populates="taller", cascade="all, delete")  # type: ignore
    productos: Mapped[list["Producto"]] = relationship(back_populates="taller", cascade="all, delete")  # type: ignore


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    taller_id: Mapped[str] = mapped_column(String, ForeignKey("talleres.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    rol: Mapped[str] = mapped_column(String(30), default="mecanico")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    taller: Mapped["Taller"] = relationship(back_populates="usuarios")
