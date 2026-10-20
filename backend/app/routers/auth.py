import os
from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.models.auth import Usuario, Rol, Permiso
from app.schemas.auth import (
    UsuarioCreate, UsuarioUpdate, UsuarioOut,
    LoginRequest, TokenResponse,
    RolCreate, RolUpdate, RolOut,
    PermisoCreate, PermisoOut,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET", "cambia-esto-en-produccion-usando-una-clave-larga-y-aleatoria")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MIN", "480"))  # 8 horas

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Utilidades de contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


# Dependencia: usuario actual
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.activo:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return user


def require_permission(modulo: str, accion: str):
    """Dependencia que verifica si el usuario tiene el permiso modulo:accion."""
    def checker(user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
        # Admin (rol "admin") pasa todo
        for r in user.roles:
            if r.codigo == "admin":
                return user
        # Buscar permiso
        permiso = db.query(Permiso).filter(
            Permiso.modulo == modulo, Permiso.accion == accion
        ).first()
        if not permiso:
            raise HTTPException(403, f"Permiso no configurado: {modulo}:{accion}")
        # Verificar si algún rol del usuario tiene ese permiso
        for r in user.roles:
            if permiso in r.permisos:
                return user
        raise HTTPException(403, f"Sin permiso: {modulo}:{accion}")
    return checker


# ===================== LOGIN / REGISTRO =====================

@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    user.ultimo_acceso = datetime.utcnow()
    db.commit()
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        usuario=UsuarioOut.model_validate(user, from_attributes=True)
    )


@router.post("/register", response_model=UsuarioOut, status_code=201, summary="Registrar usuario (solo admin)")
def register(data: UsuarioCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "crear"))):
    if db.query(Usuario).filter(Usuario.username == data.username).first():
        raise HTTPException(400, "El usuario ya existe")
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(400, "El email ya está registrado")
    new_user = Usuario(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        nombre_completo=data.nombre_completo,
        sucursal_id=data.sucursal_id,
    )
    if data.rol_codigos:
        roles = db.query(Rol).filter(Rol.codigo.in_(data.rol_codigos)).all()
        new_user.roles = roles
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UsuarioOut.model_validate(new_user, from_attributes=True)


@router.get("/me", response_model=UsuarioOut, summary="Usuario autenticado")
def me(user: Usuario = Depends(get_current_user)):
    return UsuarioOut.model_validate(user, from_attributes=True)


@router.get("/debug-permisos", summary="Debug: ver permisos del usuario")
def debug_permisos(user: Usuario = Depends(get_current_user)):
    return {
        "usuario": user.username,
        "roles": [r.codigo for r in user.roles],
        "permisos": [p.codigo for r in user.roles for p in r.permisos],
    }


@router.get("/debug-token", summary="Debug: decodificar token sin validar")
def debug_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"payload": payload}
    except Exception as e:
        return {"error": str(e), "token_recibido": token[:20] if token else "None"}


from fastapi import Header

@router.get("/debug-header", summary="Debug: ver header Authorization")
def debug_header(authorization: str = Header(None, alias="Authorization")):
    return {"authorization_header": authorization[:50] if authorization else "None"}


# ===================== USUARIOS (admin) =====================

@router.get("/usuarios", response_model=List[UsuarioOut], summary="Listar usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("admin", "leer")),
    skip: int = 0, limit: int = 50,
):
    return db.query(Usuario).offset(skip).limit(limit).all()


@router.get("/usuarios/{user_id}", response_model=UsuarioOut)
def obtener_usuario(user_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "leer"))):
    u = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    return UsuarioOut.model_validate(u, from_attributes=True)


@router.put("/usuarios/{user_id}", response_model=UsuarioOut)
def actualizar_usuario(user_id: int, data: UsuarioUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "editar"))):
    u = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    if data.email and data.email != u.email:
        if db.query(Usuario).filter(Usuario.email == data.email).first():
            raise HTTPException(400, "Email ya en uso")
        u.email = data.email
    if data.nombre_completo:
        u.nombre_completo = data.nombre_completo
    if data.activo is not None:
        u.activo = data.activo
    if data.sucursal_id is not None:
        u.sucursal_id = data.sucursal_id
    if data.rol_codigos is not None:
        u.roles = db.query(Rol).filter(Rol.codigo.in_(data.rol_codigos)).all()
    db.commit()
    db.refresh(u)
    return UsuarioOut.model_validate(u, from_attributes=True)


@router.delete("/usuarios/{user_id}", status_code=204)
def desactivar_usuario(user_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "eliminar"))):
    u = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    u.activo = False
    db.commit()


# ===================== ROLES =====================

@router.post("/roles", response_model=RolOut, status_code=201)
def crear_rol(data: RolCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "crear"))):
    if db.query(Rol).filter(Rol.codigo == data.codigo).first():
        raise HTTPException(400, "El código de rol ya existe")
    r = Rol(codigo=data.codigo, nombre=data.nombre, descripcion=data.descripcion)
    if data.permiso_codigos:
        r.permisos = db.query(Permiso).filter(Permiso.codigo.in_(data.permiso_codigos)).all()
    db.add(r)
    db.commit()
    db.refresh(r)
    return RolOut.model_validate(r, from_attributes=True)


@router.get("/roles", response_model=List[RolOut])
def listar_roles(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return db.query(Rol).filter(Rol.activo == True).all()


@router.get("/roles/{rol_id}", response_model=RolOut)
def obtener_rol(rol_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    r = db.query(Rol).filter(Rol.id == rol_id).first()
    if not r:
        raise HTTPException(404, "Rol no encontrado")
    return RolOut.model_validate(r, from_attributes=True)


@router.put("/roles/{rol_id}", response_model=RolOut)
def actualizar_rol(rol_id: int, data: RolUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "editar"))):
    r = db.query(Rol).filter(Rol.id == rol_id).first()
    if not r:
        raise HTTPException(404, "Rol no encontrado")
    if data.nombre:
        r.nombre = data.nombre
    if data.descripcion is not None:
        r.descripcion = data.descripcion
    if data.activo is not None:
        r.activo = data.activo
    if data.permiso_codigos is not None:
        r.permisos = db.query(Permiso).filter(Permiso.codigo.in_(data.permiso_codigos)).all()
    db.commit()
    db.refresh(r)
    return RolOut.model_validate(r, from_attributes=True)


@router.delete("/roles/{rol_id}", status_code=204)
def desactivar_rol(rol_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "eliminar"))):
    r = db.query(Rol).filter(Rol.id == rol_id).first()
    if not r:
        raise HTTPException(404, "Rol no encontrado")
    r.activo = False
    db.commit()


# ===================== PERMISOS =====================

@router.post("/permisos", response_model=PermisoOut, status_code=201)
def crear_permiso(data: PermisoCreate, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("admin", "crear"))):
    if db.query(Permiso).filter(Permiso.codigo == data.codigo).first():
        raise HTTPException(400, "El código de permiso ya existe")
    p = Permiso(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return PermisoOut.model_validate(p, from_attributes=True)


@router.get("/permisos", response_model=List[PermisoOut])
def listar_permisos(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return db.query(Permiso).order_by(Permiso.modulo, Permiso.accion).all()


@router.get("/permisos/modulos", response_model=List[str])
def listar_modulos(db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    return [r[0] for r in db.query(Permiso.modulo).distinct().all()]