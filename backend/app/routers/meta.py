from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.auth import Usuario
from app.routers.auth import require_permission

router = APIRouter(prefix="/api", tags=["Datos de la empresa"])


@router.get("/empresa", summary="Datos de la OptimaTech")
def datos_empresa(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("sucursales", "ver")),
):
    emp = db.execute(text("SELECT * FROM empresa LIMIT 1")).mappings().first()
    if not emp:
        return {"empresa": None}
    return {"empresa": dict(emp)}


# NOTA: los listados de /api/periodos y /api/sucursales viven en routers/control.py
# porque allí incluyen datos adicionales (nº de asientos, totales) y controles
# de estado (cerrar/reabrir período).
