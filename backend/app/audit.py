import json
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def registrar_evento(
    db: Session,
    *,
    actor_id: Optional[int],
    accion: str,
    entidad: str,
    entidad_id: Optional[str] = None,
    motivo: Optional[str] = None,
    antes: Optional[dict[str, Any]] = None,
    despues: Optional[dict[str, Any]] = None,
) -> None:
    """Registra un cambio relevante dentro de la misma transacción SQL.

    Escribe en la tabla `auditoria`, que es la bitácora única del sistema
    (misma que usa app/services/auditoria.py). Así todo el historial queda
    en un solo lugar, sin importar desde dónde se llame.
    """
    db.execute(
        text("""
            INSERT INTO auditoria
                (usuario_id, usuario_nombre, modulo, entidad, registro_id,
                 registro_codigo, accion, descripcion, datos_antes, datos_despues)
            VALUES
                (:actor,
                 (SELECT nombre_completo FROM usuario WHERE id = :actor),
                 :modulo, :entidad, :registro_id, :registro_codigo,
                 :accion, :descripcion, :antes, :despues)
        """),
        {
            "actor": actor_id,
            "accion": accion.lower(),
            "modulo": entidad,
            "entidad": entidad,
            "registro_id": int(entidad_id) if str(entidad_id or "").isdigit() else None,
            "registro_codigo": (despues or {}).get("codigo") if isinstance(despues, dict) else None,
            "descripcion": motivo or f"{accion} en {entidad}",
            "antes": json.dumps(antes, default=str) if antes is not None else None,
            "despues": json.dumps(despues, default=str) if despues is not None else None,
        },
    )
