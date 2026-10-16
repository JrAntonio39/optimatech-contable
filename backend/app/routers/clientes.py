from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

@router.get("")
def listar_clientes(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, codigo, nombre, nit, nrc, email, telefono, direccion FROM cliente")).mappings().all()
    return {"total": len(rows), "clientes": [dict(r) for r in rows]}

@router.get("/{cliente_id}")
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    rows = db.execute(text(f"SELECT id, codigo, nombre, nit, nrc, email, telefono, direccion FROM cliente WHERE id={cliente_id}")).mappings().all()
    
    if(len(rows) == 0):
        raise HTTPException(status_code=404, detail="Cliente No Encontrado")
    
    return {"total": len(rows), "clientes": [dict(r) for r in rows]}