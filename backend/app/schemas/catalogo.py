from pydantic import BaseModel
from typing import Optional

class CuentaOut(BaseModel):
    codigo: str
    nombre: str
    naturaleza: str
    nivel: int
    codigo_padre: Optional[str] = None
    class Config:
        from_attributes = True
