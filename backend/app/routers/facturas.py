from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/facturas", tags=["Facturas"])

@router.get("")
def listar_facturas(db: Session = Depends(get_db)):
    #rows = db.execute(text("SELECT fac.id, fac.numero as numero_cliente, clie.nit as nit_cliente, clie.nrc as nrc_cliente, clie.nombre as nombre_cliente, suc.codigo as codigo_sucursal, suc.nombre as nombre_sucursal, suc.nit as nit_sucursal, suc.nrc as nrc_sucursal, fac.tipo_dte, fac.fecha, fac.estado, fac.dte_json, fac.creado_en FROM factura AS fac INNER JOIN sucursal AS suc ON suc.id = fac.sucursal_id INNER JOIN cliente AS clie ON clie.id = fac.cliente_id ORDER BY fecha DESC")).mappings().all()
    rows = db.execute(text("SELECT * FROM factura ORDER BY creado_en DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay Facturas")
    
    return {"total": len(rows), "facturas": [dict(r) for r in rows]}

@router.get("/{factura_id}")
def get_factura(factura_id: int, db: Session = Depends(get_db)):
    #rows = db.execute(text(f"SELECT fac.id, fac.numero as numero_cliente, clie.nit as nit_cliente, clie.nrc as nrc_cliente, clie.nombre as nombre_cliente, suc.codigo as codigo_sucursal, suc.nombre as nombre_sucursal, suc.nit as nit_sucursal, suc.nrc as nrc_sucursal, fac.tipo_dte, fac.fecha, fac.estado, fac.dte_json, fac.creado_en FROM factura AS fac INNER JOIN sucursal AS suc ON suc.id = fac.sucursal_id INNER JOIN cliente AS clie ON clie.id = fac.cliente_id WHERE fac.id = {factura_id} ORDER BY fecha DESC")).mappings().all()
    rows = db.execute(text(f"SELECT * FROM factura WHERE id = {factura_id} ORDER BY fecha DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura No Encontrada")
    
    return {"factura":rows} 