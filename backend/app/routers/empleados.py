from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/empleados", tags=["Empleados"])

@router.get("")
def listar_emplados(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM empleado ORDER BY fecha_ingreso DESC")).mappings().all()

    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay Empleados")
    
    return {"total": len(rows), "empleados": [dict(r) for r in rows]}

@router.get("/{empleado_id}")
def get_empleado(empleado_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text(f"SELECT * FROM empleado WHERE id = {empleado_id} ORDER BY fecha_ingreso DESC")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado No Encontrado")
    
    return {"empleado":rows} 