from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, Index, text
)
from sqlalchemy.orm import relationship
from app.database import Base


class Auditoria(Base):
    """Bitácora de auditoría: quién hizo qué, cuándo y qué cambió."""

    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, nullable=False, server_default=text("now()"))
    usuario_id = Column(
        Integer, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True
    )
    usuario_nombre = Column(String(150), nullable=False)
    modulo = Column(String(30), nullable=False)   # asientos, periodos, sucursales, cuentas, usuarios
    entidad = Column(String(30), nullable=False)   # tabla afectada
    registro_id = Column(Integer, nullable=True)   # id del registro
    registro_codigo = Column(String(40), nullable=True)  # código legible (AST-2026-0001, MATRIZ, 2026)
    accion = Column(String(20), nullable=False)    # crear, editar, aprobar, anular, cerrar, eliminar
    descripcion = Column(Text, nullable=True)      # qué se hizo, en palabras
    datos_antes = Column(Text, nullable=True)      # JSON del estado previo
    datos_despues = Column(Text, nullable=True)    # JSON del estado nuevo
    ip = Column(String(45), nullable=True)

    usuario = relationship("Usuario", lazy="joined")

    __table_args__ = (
        Index("idx_auditoria_fecha", "fecha"),
        Index("idx_auditoria_modulo_accion", "modulo", "accion"),
        Index("idx_auditoria_usuario", "usuario_id"),
        Index("idx_auditoria_registro", "entidad", "registro_id"),
    )
