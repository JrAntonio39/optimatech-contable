from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/compras", tags=["Compras"])

@router.get("")
def listar_compras(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM compra ORDER BY creado_en DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay Compras")
    
    return {"total": len(rows), "compras": [dict(r) for r in rows]}

@router.get("/{compra_id}")
def get_compra(compra_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text(f"SELECT * FROM compra WHERE id = {compra_id} ORDER BY fecha DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra No Encontrada")
    
    return {"compra":rows} 