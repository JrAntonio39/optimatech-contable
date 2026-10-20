from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Tablas de asociación
usuario_rol = Table(
    "usuario_rol",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuario.id"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("rol.id"), primary_key=True),
)

rol_permiso = Table(
    "rol_permiso",
    Base.metadata,
    Column("rol_id", Integer, ForeignKey("rol.id"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permiso.id"), primary_key=True),
)


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)
    sucursal_id = Column(Integer, ForeignKey("sucursal.id"), nullable=True)

    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")
    sucursal = relationship("Sucursal", back_populates="usuarios")

    @property
    def rol_codigos(self) -> list[str]:
        return [r.codigo for r in self.roles]


class Rol(Base):
    __tablename__ = "rol"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(30), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    activo = Column(Boolean, default=True)

    usuarios = relationship("Usuario", secondary=usuario_rol, back_populates="roles")
    permisos = relationship("Permiso", secondary=rol_permiso, back_populates="roles")

    @property
    def permiso_codigos(self) -> list[str]:
        return [p.codigo for p in self.permisos]


class Permiso(Base):
    __tablename__ = "permiso"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    modulo = Column(String(30), nullable=False, index=True)  # catálogo, asientos, reportes, facturación, compras, planilla, admin
    accion = Column(String(20), nullable=False)  # crear, leer, editar, eliminar, aprobar, anular, cerrar
    descripcion = Column(String(255))

    roles = relationship("Rol", secondary=rol_permiso, back_populates="permisos")


# Actualizar modelo Sucursal para la relación inversa
# (se hace en catalogo.py o se crea archivo aparte; aquí solo referencia)