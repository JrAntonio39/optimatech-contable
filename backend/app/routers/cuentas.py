from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/cuentas", tags=["Cuentas"])

NATURALEZAS = ("Deudora", "Acreedora", "Deudora o Acreedora")


class CuentaCreate(BaseModel):
    codigo: str = Field(..., max_length=20, description="Ej: 1.1.1.03.04")
    nombre: str = Field(..., max_length=150)
    naturaleza: str = Field(..., description="Deudora | Acreedora | Deudora o Acreedora")
    nivel: int = Field(..., ge=1, le=5)
    codigo_padre: Optional[str] = Field(None, max_length=20)


@router.get("", summary="Lista todas las cuentas del catálogo")
def listar_cuentas(db: Session = Depends(get_db), nivel: int = Query(None, description="Filtrar por nivel 1-5"), q: str = Query(None, description="Buscar por nombre o código")):
    query = "SELECT codigo, nombre, naturaleza, nivel, codigo_padre FROM catalogo_cuenta"
    conds = []
    params = {}
    if nivel is not None:
        conds.append("nivel = :nivel")
        params["nivel"] = nivel
    if q:
        conds.append("(codigo ILIKE :q OR nombre ILIKE :q)")
        params["q"] = f"%{q}%"
    if conds:
        query += " WHERE " + " AND ".join(conds)
    query += " ORDER BY codigo"
    rows = db.execute(text(query), params).mappings().all()
    return {"total": len(rows), "cuentas": list(rows)}

@router.get("/mayor", summary="Solo cuentas de mayor (nivel 3, las del manual)")
def cuentas_mayor(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT codigo, nombre, naturaleza FROM catalogo_cuenta WHERE nivel=3 ORDER BY codigo")).mappings().all()
    return {"total": len(rows), "cuentas": list(rows)}

@router.post("", status_code=201, summary="Agregar una cuenta al catálogo")
def crear_cuenta(data: CuentaCreate, db: Session = Depends(get_db)):
    codigo = data.codigo.strip()
    nombre = data.nombre.strip()
    if not codigo or not nombre:
        raise HTTPException(400, "Código y nombre son obligatorios")
    if data.naturaleza not in NATURALEZAS:
        raise HTTPException(400, f"Naturaleza inválida. Use: {', '.join(NATURALEZAS)}")

    existe = db.execute(text("SELECT 1 FROM catalogo_cuenta WHERE codigo=:c"), {"c": codigo}).first()
    if existe:
        raise HTTPException(409, f"La cuenta {codigo} ya existe")

    if data.codigo_padre:
        padre = db.execute(
            text("SELECT codigo, nivel FROM catalogo_cuenta WHERE codigo=:c"),
            {"c": data.codigo_padre},
        ).mappings().first()
        if not padre:
            raise HTTPException(400, f"La cuenta padre {data.codigo_padre} no existe")
        if data.nivel != padre["nivel"] + 1:
            raise HTTPException(
                400,
                f"Nivel inconsistente: el padre {padre['codigo']} es nivel {padre['nivel']}, la cuenta debe ser nivel {padre['nivel'] + 1}",
            )
    elif data.nivel != 1:
        raise HTTPException(400, "Sin cuenta padre, el nivel debe ser 1 (clase)")

    db.execute(
        text("INSERT INTO catalogo_cuenta (codigo, nombre, naturaleza, nivel, codigo_padre) VALUES (:c, :n, :nat, :niv, :p)"),
        {"c": codigo, "n": nombre, "nat": data.naturaleza, "niv": data.nivel, "p": data.codigo_padre},
    )
    db.commit()
    row = db.execute(
        text("SELECT codigo, nombre, naturaleza, nivel, codigo_padre FROM catalogo_cuenta WHERE codigo=:c"),
        {"c": codigo},
    ).mappings().first()
    return {"msg": "Cuenta creada", "cuenta": dict(row)}

@router.get("/{codigo}", summary="Detalle de una cuenta")
def detalle_cuenta(codigo: str, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT codigo, nombre, naturaleza, nivel, codigo_padre FROM catalogo_cuenta WHERE codigo=:c"), {"c": codigo}).mappings().first()
    if not row:
        raise HTTPException(404, f"Cuenta {codigo} no encontrada")
    hijos = db.execute(text("SELECT codigo, nombre FROM catalogo_cuenta WHERE codigo_padre=:c ORDER BY codigo"), {"c": codigo}).mappings().all()
    return {"cuenta": dict(row), "hijos": list(hijos)}
