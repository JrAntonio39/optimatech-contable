from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.factura import FacturaElectronica
from pydantic.json import pydantic_encoder
import json

router = APIRouter(prefix="/api/facturas", tags=["Facturas"])

@router.get("")
def listar_facturas(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM factura ORDER BY creado_en DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay Facturas")
    
    return {"total": len(rows), "facturas": [dict(r) for r in rows]}

@router.get("/{factura_id}")
def get_factura(factura_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text(f"SELECT * FROM factura WHERE id = {factura_id} ORDER BY fecha DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura No Encontrada")
    
    return {"factura":rows} 

@router.get("/{factura_id}/detalles-factura")
def get_detalles_factura(factura_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text(f"SELECT * FROM factura_detalle WHERE factura_id = {factura_id}")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay detalles de factura")
    
    return {"detalles_factura":rows} 

@router.post("", response_model=FacturaElectronica, status_code=status.HTTP_201_CREATED)
def crear_factura(factura: FacturaElectronica, db: Session = Depends(get_db)):
    asiento_id = None 
    sucursal_id = db.execute(text(f"SELECT suc.id FROM sucursal AS suc WHERE suc.nit = '{factura.emisor.nit}'")).scalar_one()
    cliente_id = db.execute(text(f"SELECT cli.id FROM cliente AS cli WHERE cli.nrc = '{factura.receptor.nrc}'")).scalar_one()
    periodo_id = 1
    numero = factura.identificacion.numeroControl
    fecha = factura.identificacion.fechaEmi
    dte_json = json.dumps(factura, default=pydantic_encoder)
    
    match factura.identificacion.tipoDte:
        case "01":
            # Factura Electrónica para Consumidores Finales
            tipo_dte = "FE" 
        case "03":
            # Comprobante de Crédito Fiscal
            tipo_dte = "CCF"

    db.execute(text(
        f"""INSERT INTO factura (numero, tipo_dte, fecha, cliente_id, sucursal_id, periodo_id, asiento_id, dte_json) 
        VALUES ({numero}, {tipo_dte}, {fecha}, {cliente_id}, {sucursal_id}, {periodo_id}, {asiento_id}, {dte_json}) """
    ))        
