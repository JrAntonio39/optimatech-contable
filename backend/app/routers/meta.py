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


@router.get("/api/clientes", summary="Lista de clientes")
def listar_clientes(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, codigo, nombre, nit, nrc, email, telefono, direccion FROM cliente")).mappings().all()
    return {"total": len(rows), "clientes": [dict(r) for r in rows]}


@router.get("/api/facturas", summary="Lista de facturas")
def listar_facturas(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT fac.id, fac.numero as numero_cliente, clie.nit as nit_cliente, clie.nrc as nrc_cliente, clie.nombre as nombre_cliente, suc.codigo as codigo_sucursal, suc.nombre as nombre_sucursal, suc.nit as nit_sucursal, suc.nrc as nrc_sucursal, fac.tipo_dte, fac.fecha, fac.estado, fac.dte_json, fac.creado_en FROM factura AS fac INNER JOIN sucursal AS suc ON suc.id = fac.sucursal_id INNER JOIN cliente AS clie ON clie.id = fac.cliente_id ORDER BY fecha DESC")).mappings().all()
    return {"total": len(rows), "facturas": [dict(r) for r in rows]}