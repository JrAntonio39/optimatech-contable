from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Sucursal(Base):
    __tablename__ = "sucursal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=True)
    es_matriz = Column(Boolean, default=False)
    empresa_id = Column(Integer, ForeignKey("empresa.id"), nullable=True)

    usuarios = relationship("Usuario", back_populates="sucursal")
    empresa = relationship("Empresa", back_populates="sucursales")


class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(Integer, primary_key=True, autoincrement=True)
    razon_social = Column(String(150), nullable=False)
    nombre_comercial = Column(String(100), nullable=False)
    nit = Column(String(20), nullable=True)
    nrc = Column(String(20), nullable=True)
    giro = Column(Text, nullable=True)

    sucursales = relationship("Sucursal", back_populates="empresa")