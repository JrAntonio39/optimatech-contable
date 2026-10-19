from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.factura import FacturaElectronica, ItemFactura
from pydantic.json import pydantic_encoder
import json
from app.routers.asientos import AsientoCreate, crear_asiento

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

@router.post("/{factura_id}/detalles-factura")
def crear_detalles_factura(factura_id: int, items_factura: list[ItemFactura], db: Session = Depends(get_db)):
    detalles_creados = []

    codigos_cuenta = db.execute(text(f"SELECT dasi.cuenta_codigo FROM factura AS fac INNER JOIN asiento AS asi ON fac.asiento_id = asi.id INNER JOIN detalle_asiento AS dasi ON dasi.asiento_id = asi.id WHERE fac.id = '{factura_id}'")).mappings().all()
    
    for index, item in enumerate(items_factura):
        codigo_cuenta = codigos_cuenta[index]

        detalle_agregado = db.execute(text(
            f"""INSERT INTO factura_detalle (factura_id, descripcion, cantidad, precio_unitario, cuenta_ingreso_codigo) 
            VALUES ({factura_id}, {item.descripcion}, {item.cantidad}, {item.precioUni}, {codigo_cuenta})
            RETURNING * """
        )).mappings().one()

        detalles_creados.append(detalle_agregado)

    return {"detalles_creados": detalles_creados}   


@router.post("", response_model=FacturaElectronica, status_code=status.HTTP_201_CREATED)
def crear_factura(factura: FacturaElectronica, db: Session = Depends(get_db)):
    asiento_id = None 
    sucursal_id = db.execute(text(f"SELECT suc.id FROM sucursal AS suc WHERE suc.nit = '{factura.emisor.nit}'")).scalar()
    cliente_id = db.execute(text(f"SELECT cli.id FROM cliente AS cli WHERE cli.nrc = '{factura.receptor.nrc}'")).scalar()
    periodo_id = db.execute(text("SELECT periodo_c.id FROM periodo_contable AS periodo_c ORDER BY periodo_c.id DESC")).scalar()
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

    factura_creada = db.execute(text(
        f"""INSERT INTO factura (numero, tipo_dte, fecha, cliente_id, sucursal_id, periodo_id, asiento_id, dte_json) 
        VALUES ({numero}, {tipo_dte}, {fecha}, {cliente_id}, {sucursal_id}, {periodo_id}, {asiento_id}, {dte_json})
        RETURNING * """
    )).mappings().one()

    return {"factura_creada": factura_creada}

@router.post("/{factura_id}/contabilizar", response_model=AsientoCreate, status_code=status.HTTP_201_CREATED)
def contabilizar_factura(factura_id: int, data: AsientoCreate, db: Session = Depends(get_db)):
    asiento_creado = crear_asiento(data, db)

    if not asiento_creado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo crear el asiento contable")

    asiento_id = asiento_creado["asiento"]["id"]    
    factura_modificada = db.execute(text(f"UPDATE factura AS fac SET asiento_id = '{asiento_id}' WHERE fac.id = '{factura_id}' RETURNING *")).mappings().one()       

    respuestaGetFactura = get_factura(factura_id)
    dte_json_factura =  FacturaElectronica(respuestaGetFactura["factura"][0]["dte_json"])
    cuerpoDocumentoFactura = dte_json_factura.cuerpoDocumento

    detalles_creados_factura = crear_detalles_factura(factura_id, cuerpoDocumentoFactura)

    return {"factura": factura_modificada, "detalles_factura": detalles_creados_factura, "asiento": asiento_creado}       
