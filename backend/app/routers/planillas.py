from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/planillas", tags=["Planillas"])

@router.get("")
def listar_planillas(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM planilla ORDER BY creado_en DESC")).mappings().all()

    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay Planillas")
    
    return {"total": len(rows), "planillas": [dict(r) for r in rows]}

@router.get("/{planilla_id}")
def get_planilla(planilla_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text(f"SELECT * FROM planilla WHERE id = {planilla_id} ORDER BY creado_en DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planilla No Encontrada")
    
    return {"planilla":rows} 