from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(tags=["Catálogos base"])


@router.get("/api/periodos", summary="Periodos contables para los formularios")
def listar_periodos(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, anio, fecha_inicio, fecha_fin, estado FROM periodo_contable ORDER BY anio DESC")).mappings().all()
    return {"total": len(rows), "periodos": [dict(r) for r in rows]}


@router.get("/api/sucursales", summary="Sucursales para los formularios")
def listar_sucursales(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, codigo, nombre, es_matriz FROM sucursal ORDER BY id")).mappings().all()
    return {"total": len(rows), "sucursales": [dict(r) for r in rows]}
