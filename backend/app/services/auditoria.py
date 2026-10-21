"""
Servicio de auditoría (bitácora).

Registra quién creó, editó, aprobó o anuló cada operación, cuándo y qué cambió.
Se llama desde los routers para que el registro sea automático y no dependa
del frontend.
"""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.models.auth import Usuario


def registrar(
    db: Session,
    usuario: Optional[Usuario],
    modulo: str,
    entidad: str,
    accion: str,
    registro_id: Optional[int] = None,
    registro_codigo: Optional[str] = None,
    descripcion: Optional[str] = None,
    datos_antes: Optional[dict] = None,
    datos_despues: Optional[dict] = None,
    ip: Optional[str] = None,
):
    """Registra una acción en la bitácora. Nunca lanza excepción: si falla el
    registro, la operación principal no debe abortarse."""
    try:
        fila = Auditoria(
            usuario_id=usuario.id if usuario else None,
            usuario_nombre=usuario.nombre_completo if usuario else "Sistema",
            modulo=modulo,
            entidad=entidad,
            accion=accion,
            registro_id=registro_id,
            registro_codigo=registro_codigo,
            descripcion=descripcion,
            datos_antes=json.dumps(datos_antes, default=str) if datos_antes else None,
            datos_despues=json.dumps(datos_despues, default=str) if datos_despues else None,
            ip=ip,
            fecha=datetime.utcnow(),
        )
        db.add(fila)
        db.flush()  # asegura el id sin commitear
    except Exception:
        db.rollback()
    return None
