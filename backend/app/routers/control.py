"""
Control del sistema: aprobaciones, anulaciones, administración de períodos y
sucursales, y consulta de la bitácora de auditoría.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.models.auth import Usuario
from app.routers.auth import require_permission
from app.services.auditoria import registrar

router = APIRouter(prefix="/api", tags=["Control del sistema"])

ESTADOS_ASIENTO = ("PENDIENTE", "VIGENTE", "ANULADO")
ESTADOS_PERIODO = ("ABIERTO", "CERRADO")


# ==========================================================================
# 1. ADMINISTRACIÓN DE PERÍODOS CONTABLES
# ==========================================================================

class PeriodoCreate(BaseModel):
    anio: int = Field(..., ge=1900, le=2200)
    fecha_inicio: date
    fecha_fin: date
    estado: str = Field("ABIERTO", pattern="^(ABIERTO|CERRADO)$")


class PeriodoUpdate(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = Field(None, pattern="^(ABIERTO|CERRADO)$")


@router.get("/periodos", summary="Listar períodos contables")
def listar_periodos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("periodos", "ver")),
):
    rows = db.execute(
        text("""
        SELECT p.id, p.anio, p.fecha_inicio, p.fecha_fin, p.estado,
               (SELECT COUNT(*) FROM asiento a WHERE a.periodo_id = p.id) AS num_asientos,
               (SELECT COALESCE(SUM(d.debe),0) FROM detalle_asiento d
                  JOIN asiento a2 ON a2.id = d.asiento_id
                 WHERE a2.periodo_id = p.id AND a2.estado='VIGENTE') AS total_debe
          FROM periodo_contable p ORDER BY p.anio DESC
        """)
    ).mappings().all()
    out = []
    for r in rows:
        r = dict(r)
        r["total_debe"] = float(r["total_debe"])
        out.append(r)
    return {"total": len(out), "periodos": out}


@router.post("/periodos", status_code=201, summary="Abrir un nuevo período contable")
def crear_periodo(
    data: PeriodoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("periodos", "crear")),
):
    if data.fecha_fin <= data.fecha_inicio:
        raise HTTPException(400, "La fecha de fin debe ser posterior a la de inicio")
    if data.fecha_inicio.year != data.anio or data.fecha_fin.year != data.anio:
        raise HTTPException(400, "Las fechas deben pertenecer al año del período")
    existe = db.execute(text("SELECT 1 FROM periodo_contable WHERE anio=:a"), {"a": data.anio}).first()
    if existe:
        raise HTTPException(409, f"Ya existe un período para el año {data.anio}")
    cruce = db.execute(
        text("SELECT anio FROM periodo_contable WHERE NOT (fecha_fin < :inicio OR fecha_inicio > :fin)"),
        {"inicio": data.fecha_inicio, "fin": data.fecha_fin},
    ).mappings().first()
    if cruce:
        raise HTTPException(409, f"El rango se cruza con el período {cruce['anio']}")
    res = db.execute(
        text("INSERT INTO periodo_contable (anio, fecha_inicio, fecha_fin, estado) VALUES (:a,:i,:f,:e) RETURNING id"),
        {"a": data.anio, "i": data.fecha_inicio, "f": data.fecha_fin, "e": data.estado},
    )
    nuevo_id = res.mappings().first()["id"]
    registrar(
        db, user, "periodos", "periodo_contable", "crear",
        registro_id=nuevo_id, registro_codigo=str(data.anio),
        descripcion=f"Abrrió el período contable {data.anio} ({data.fecha_inicio} a {data.fecha_fin})",
        datos_despues={"anio": data.anio, "estado": data.estado},
    )
    db.commit()
    return {"msg": f"Período {data.anio} creado", "id": nuevo_id}


@router.put("/periodos/{periodo_id}", summary="Modificar un período")
def actualizar_periodo(
    periodo_id: int,
    data: PeriodoUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("periodos", "editar")),
):
    cab = db.execute(text("SELECT * FROM periodo_contable WHERE id=:i"), {"i": periodo_id}).mappings().first()
    if not cab:
        raise HTTPException(404, f"Período {periodo_id} no encontrado")
    if cab["estado"] == "CERRADO":
        raise HTTPException(400, f"El período {cab['anio']} está CERRADO y no admite cambios")
    antes = dict(cab)
    campos, params = [], {"i": periodo_id}
    if data.fecha_inicio:
        campos.append("fecha_inicio = :fi")
        params["fi"] = data.fecha_inicio
    if data.fecha_fin:
        campos.append("fecha_fin = :ff")
        params["ff"] = data.fecha_fin
    if data.estado:
        campos.append("estado = :e")
        params["e"] = data.estado
    if campos:
        db.execute(text(f"UPDATE periodo_contable SET {', '.join(campos)} WHERE id = :i"), params)
    registrar(
        db, user, "periodos", "periodo_contable", "editar",
        registro_id=periodo_id, registro_codigo=str(antes["anio"]),
        descripcion=f"Modificó el período contable {antes['anio']}",
        datos_antes={"estado": antes["estado"], "fecha_inicio": str(antes["fecha_inicio"]), "fecha_fin": str(antes["fecha_fin"])},
        datos_despues={"estado": data.estado or antes["estado"]},
    )
    db.commit()
    return {"msg": f"Período {antes['anio']} actualizado"}


@router.post("/periodos/{periodo_id}/cerrar", summary="Cerrar un período contable (bloquea movimientos)")
def cerrar_periodo(
    periodo_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("periodos", "cerrar")),
):
    cab = db.execute(text("SELECT * FROM periodo_contable WHERE id=:i"), {"i": periodo_id}).mappings().first()
    if not cab:
        raise HTTPException(404, f"Período {periodo_id} no encontrado")
    if cab["estado"] == "CERRADO":
        raise HTTPException(400, f"El período {cab['anio']} ya está cerrado")

    pendientes = db.execute(
        text("SELECT COUNT(*) AS n FROM asiento WHERE periodo_id=:p AND estado='PENDIENTE'"),
        {"p": periodo_id},
    ).mappings().first()["n"]
    if pendientes:
        raise HTTPException(400, f"No se puede cerrar: hay {pendientes} asiento(s) PENDIENTE sin aprobar")

    antes = dict(cab)
    db.execute(text("UPDATE periodo_contable SET estado='CERRADO' WHERE id=:i"), {"i": periodo_id})
    registrar(
        db, user, "periodos", "periodo_contable", "cerrar",
        registro_id=periodo_id, registro_codigo=str(cab["anio"]),
        descripcion=f"Cerró el período contable {cab['anio']}",
        datos_antes={"estado": antes["estado"]},
        datos_despues={"estado": "CERRADO"},
    )
    db.commit()
    return {"msg": f"Período {cab['anio']} cerrado", "estado": "CERRADO"}


@router.post("/periodos/{periodo_id}/abrir", summary="Reabrir un período cerrado")
def abrir_periodo(
    periodo_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("periodos", "cerrar")),
):
    cab = db.execute(text("SELECT * FROM periodo_contable WHERE id=:i"), {"i": periodo_id}).mappings().first()
    if not cab:
        raise HTTPException(404, f"Período {periodo_id} no encontrado")
    if cab["estado"] == "ABIERTO":
        raise HTTPException(400, f"El período {cab['anio']} ya está abierto")
    antes = dict(cab)
    db.execute(text("UPDATE periodo_contable SET estado='ABIERTO' WHERE id=:i"), {"i": periodo_id})
    registrar(
        db, user, "periodos", "periodo_contable", "editar",
        registro_id=periodo_id, registro_codigo=str(cab["anio"]),
        descripcion=f"Reabrió el período contable {cab['anio']}",
        datos_antes={"estado": antes["estado"]},
        datos_despues={"estado": "ABIERTO"},
    )
    db.commit()
    return {"msg": f"Período {cab['anio']} reabierto", "estado": "ABIERTO"}


# ==========================================================================
# 2. ADMINISTRACIÓN DE SUCURSALES
# ==========================================================================

class SucursalCreate(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=10)
    nombre: str = Field(..., min_length=2, max_length=100)
    direccion: Optional[str] = None
    es_matriz: bool = False


class SucursalUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    es_matriz: Optional[bool] = None


@router.get("/sucursales", summary="Listar sucursales")
def listar_sucursales(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("sucursales", "ver")),
):
    rows = db.execute(
        text("""
        SELECT s.id, s.codigo, s.nombre, s.direccion, s.es_matriz, s.empresa_id,
               (SELECT COUNT(*) FROM asiento a WHERE a.sucursal_id = s.id) AS num_asientos
          FROM sucursal s ORDER BY s.es_matriz DESC, s.nombre
        """)
    ).mappings().all()
    return {"total": len(rows), "sucursales": [dict(r) for r in rows]}


@router.post("/sucursales", status_code=201, summary="Crear sucursal")
def crear_sucursal(
    data: SucursalCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("sucursales", "crear")),
):
    codigo = data.codigo.strip().upper()
    if db.execute(text("SELECT 1 FROM sucursal WHERE codigo=:c"), {"c": codigo}).first():
        raise HTTPException(409, f"Ya existe una sucursal con el código {codigo}")
    res = db.execute(
        text("INSERT INTO sucursal (codigo, nombre, direccion, es_matriz) VALUES (:c,:n,:d,:m) RETURNING id"),
        {"c": codigo, "n": data.nombre.strip(), "d": data.direccion, "m": data.es_matriz},
    )
    nuevo_id = res.mappings().first()["id"]
    registrar(
        db, user, "sucursales", "sucursal", "crear",
        registro_id=nuevo_id, registro_codigo=codigo,
        descripcion=f"Creó la sucursal {codigo} - {data.nombre}",
        datos_despues={"codigo": codigo, "nombre": data.nombre, "es_matriz": data.es_matriz},
    )
    db.commit()
    return {"msg": f"Sucursal {codigo} creada", "id": nuevo_id}


@router.put("/sucursales/{sucursal_id}", summary="Modificar sucursal")
def actualizar_sucursal(
    sucursal_id: int,
    data: SucursalUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("sucursales", "editar")),
):
    cab = db.execute(text("SELECT * FROM sucursal WHERE id=:i"), {"i": sucursal_id}).mappings().first()
    if not cab:
        raise HTTPException(404, f"Sucursal {sucursal_id} no encontrada")
    antes = dict(cab)
    campos, params = [], {"i": sucursal_id}
    if data.nombre:
        campos.append("nombre = :n")
        params["n"] = data.nombre.strip()
    if data.direccion is not None:
        campos.append("direccion = :d")
        params["d"] = data.direccion
    if data.es_matriz is not None:
        campos.append("es_matriz = :m")
        params["m"] = data.es_matriz
    if campos:
        db.execute(text(f"UPDATE sucursal SET {', '.join(campos)} WHERE id = :i"), params)
    registrar(
        db, user, "sucursales", "sucursal", "editar",
        registro_id=sucursal_id, registro_codigo=antes["codigo"],
        descripcion=f"Modificó la sucursal {antes['codigo']}",
        datos_antes={"nombre": antes["nombre"], "es_matriz": antes["es_matriz"]},
        datos_despues={"nombre": data.nombre or antes["nombre"]},
    )
    db.commit()
    return {"msg": f"Sucursal {antes['codigo']} actualizada"}


# ==========================================================================
# 3. BITÁCORA DE AUDITORÍA
# ==========================================================================

@router.get("/auditoria", summary="Consultar la bitácora de auditoría")
def listar_auditoria(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("auditoria", "ver")),
    modulo: Optional[str] = Query(None, description="Filtrar por módulo"),
    accion: Optional[str] = Query(None, description="Filtrar por acción"),
    usuario_id: Optional[int] = Query(None),
    registro_id: Optional[int] = Query(None),
    desde: Optional[date] = Query(None, description="Desde (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(None, description="Hasta (YYYY-MM-DD)"),
    q: Optional[str] = Query(None, description="Buscar en descripción o código"),
    skip: int = 0,
    limit: int = Query(100, le=500),
    limite: Optional[int] = Query(None, description="Alias de limit"),
):
    conds, params = [], {}
    if modulo:
        conds.append("a.modulo = :m")
        params["m"] = modulo
    if accion:
        conds.append("a.accion = :ac")
        params["ac"] = accion
    if usuario_id:
        conds.append("a.usuario_id = :u")
        params["u"] = usuario_id
    if registro_id:
        conds.append("a.registro_id = :r")
        params["r"] = registro_id
    if desde:
        conds.append("a.fecha >= :d1")
        params["d1"] = f"{desde} 00:00:00"
    if hasta:
        conds.append("a.fecha <= :d2")
        params["d2"] = f"{hasta} 23:59:59"
    if q:
        conds.append("(a.descripcion ILIKE :q OR a.registro_codigo ILIKE :q OR a.usuario_nombre ILIKE :q)")
        params["q"] = f"%{q}%"
    if limite:
        limit = min(limite, 500)
    where = (" WHERE " + " AND ".join(conds)) if conds else ""

    total = db.execute(text(f"SELECT COUNT(*) AS n FROM auditoria a{where}"), params).mappings().first()["n"]
    rows = db.execute(
        text(f"""
        SELECT a.id, a.fecha, a.usuario_id, a.usuario_nombre, a.modulo, a.entidad,
               a.registro_id, a.registro_codigo, a.accion, a.descripcion,
               a.datos_antes, a.datos_despues
          FROM auditoria a{where}
         ORDER BY a.fecha DESC, a.id DESC
         LIMIT :lim OFFSET :sk
        """),
        {**params, "lim": limit, "sk": skip},
    ).mappings().all()
    return {"total": total, "registros": [dict(r) for r in rows]}


@router.get("/auditoria/resumen", summary="Resumen de la auditoría por módulo y acción")
def resumen_auditoria(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("auditoria", "ver")),
):
    modulos = db.execute(
        text("SELECT modulo, accion, COUNT(*) AS n FROM auditoria GROUP BY modulo, accion ORDER BY modulo, accion")
    ).mappings().all()
    return {"total": len(modulos), "conteos": [dict(r) for r in modulos]}
