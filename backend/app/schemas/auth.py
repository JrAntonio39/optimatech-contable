from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nombre_completo: str = Field(..., min_length=2, max_length=150)
    sucursal_id: Optional[int] = None

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=100)
    rol_codigos: List[str] = []  # lista de códigos de rol a asignar

class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    activo: Optional[bool] = None
    sucursal_id: Optional[int] = None
    rol_codigos: Optional[List[str]] = None

class UsuarioOut(UsuarioBase):
    id: int
    activo: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime]
    rol_codigos: List[str] = []  # códigos de rol

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


class RolBase(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=30)
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None

class RolCreate(RolBase):
    permiso_codigos: List[str] = []

class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    permiso_codigos: Optional[List[str]] = None

class RolOut(RolBase):
    id: int
    activo: bool
    permiso_codigos: List[str] = []  # códigos de permiso

    class Config:
        from_attributes = True


class PermisoBase(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=50)
    nombre: str = Field(..., min_length=2, max_length=100)
    modulo: str = Field(..., min_length=2, max_length=30)
    accion: str = Field(..., min_length=2, max_length=20)
    descripcion: Optional[str] = None

class PermisoCreate(PermisoBase):
    pass

class PermisoOut(PermisoBase):
    id: int

    class Config:
        from_attributes = True