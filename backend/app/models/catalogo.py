from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CatalogoCuenta(Base):
    __tablename__ = "catalogo_cuenta"
    codigo = Column(String(20), primary_key=True)
    nombre = Column(String(150), nullable=False)
    naturaleza = Column(String(25), nullable=False)
    nivel = Column(Integer, nullable=False)
    codigo_padre = Column(String(20), ForeignKey("catalogo_cuenta.codigo"), nullable=True)
    # self-referencing
    hijos = relationship("CatalogoCuenta", backref="padre", remote_side=[codigo])
