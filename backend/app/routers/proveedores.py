from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/proveedores", tags=["Proveedores"])

@router.get("")
def listar_proveedores(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM proveedor")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay Proveedores")
    
    return {"total": len(rows), "proveedores": [dict(r) for r in rows]}

@router.get("/{proveedor_id}")
def get_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text(f"SELECT * FROM proveedor WHERE id = {proveedor_id}")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor No Encontrado")
    
    return {"proveedor":rows}