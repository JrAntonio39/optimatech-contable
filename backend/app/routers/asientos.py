from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.auth import Usuario
from app.routers.auth import require_permission
from app.services.auditoria import registrar
from app.audit import registrar_evento

router = APIRouter(prefix="/api/asientos", tags=["Asientos"])

TIPOS = ("APERTURA", "DIARIO", "AJUSTE", "CIERRE")


class LineaIn(BaseModel):
    cuenta_codigo: str = Field(..., max_length=20)
    debe: float = Field(0, ge=0)
    haber: float = Field(0, ge=0)
    descripcion: Optional[str] = None


class AsientoCreate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20, description="Si se omite se genera AST-ANIO-0001")
    fecha: date
    concepto: str = Field(..., min_length=3)
    tipo: str = Field("DIARIO")
    periodo_id: int
    sucursal_id: Optional[int] = None
    detalles: list[LineaIn]


class AnulacionIn(BaseModel):
    motivo: str = Field(..., min_length=5, max_length=500)
    fecha_reversion: date
    periodo_id: int


def _totales(detalles):
    debe = round(sum(float(d.debe or 0) for d in detalles), 2)
    haber = round(sum(float(d.haber or 0) for d in detalles), 2)
    return debe, haber


@router.get("", summary="Lista asientos con sus totales")
def listar_asientos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("asientos", "ver")),
    tipo: str = Query(None, description="APERTURA | DIARIO | AJUSTE | CIERRE"),
    periodo_id: int = Query(None),
    sucursal_id: int = Query(None),
    estado: str = Query(None, description="PENDIENTE | VIGENTE | ANULADO"),
    desde: date = Query(None),
    hasta: date = Query(None),
):
    query = """
        SELECT a.id, a.codigo, a.fecha, a.concepto, a.tipo, a.periodo_id, a.sucursal_id, a.estado,
               COALESCE(SUM(d.debe),0) AS total_debe, COALESCE(SUM(d.haber),0) AS total_haber
        FROM asiento a LEFT JOIN detalle_asiento d ON d.asiento_id = a.id
    """
    conds, params = [], {}
    if estado:
        if estado not in ("PENDIENTE", "VIGENTE", "ANULADO"):
            raise HTTPException(400, "Estado inválido")
        conds.append("a.estado = :estado")
        params["estado"] = estado
    if tipo:
        if tipo not in TIPOS:
            raise HTTPException(400, f"Tipo inválido. Use: {', '.join(TIPOS)}")
        conds.append("a.tipo = :tipo")
        params["tipo"] = tipo
    if periodo_id:
        conds.append("a.periodo_id = :p")
        params["p"] = periodo_id
    if sucursal_id:
        conds.append("a.sucursal_id = :s")
        params["s"] = sucursal_id
    if desde and hasta and desde > hasta:
        raise HTTPException(400, "La fecha inicial no puede ser posterior a la fecha final")
    if desde:
        conds.append("a.fecha >= :desde")
        params["desde"] = desde
    if hasta:
        conds.append("a.fecha <= :hasta")
        params["hasta"] = hasta
    if conds:
        query += " WHERE " + " AND ".join(conds)
    query += " GROUP BY a.id ORDER BY a.fecha, a.id"
    rows = db.execute(text(query), params).mappings().all()
    out = []
    for r in rows:
        r = dict(r)
        r["total_debe"] = float(r["total_debe"])
        r["total_haber"] = float(r["total_haber"])
        r["estado_partida"] = "CUADRADO" if r["total_debe"] == r["total_haber"] else "DESCUADRADO"
        out.append(r)
    return {"total": len(out), "asientos": out}


@router.get("/totales", summary="Totales calculados (vista v_asiento_totales)")
def totales_asientos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("asientos", "ver")),
):
    rows = db.execute(text("SELECT * FROM v_asiento_totales ORDER BY codigo")).mappings().all()
    return {"total": len(rows), "totales": [dict(r) for r in rows]}


@router.get("/pendientes", summary="Asientos en estado PENDIENTE (por aprobar)")
def listar_pendientes(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("asientos", "ver")),
    periodo_id: Optional[int] = Query(None),
):
    cond = ""
    params = {}
    if periodo_id:
        cond = "AND a.periodo_id = :p"
        params["p"] = periodo_id
    rows = db.execute(
        text(f"""
        SELECT a.id, a.codigo, a.fecha, a.concepto, a.tipo, a.estado,
               a.periodo_id, a.sucursal_id, a.creado_en,
               COALESCE(SUM(d.debe),0) AS total_debe,
               COALESCE(SUM(d.haber),0) AS total_haber
          FROM asiento a
          LEFT JOIN detalle_asiento d ON d.asiento_id = a.id
         WHERE a.estado = 'PENDIENTE' {cond}
         GROUP BY a.id
         ORDER BY a.fecha, a.id
        """),
        params,
    ).mappings().all()
    out = []
    for r in rows:
        r = dict(r)
        r["total_debe"] = float(r["total_debe"])
        r["total_haber"] = float(r["total_haber"])
        r["estado_partida"] = "CUADRADO" if r["total_debe"] == r["total_haber"] else "DESCUADRADO"
        out.append(r)
    return {"total": len(out), "asientos": out}


@router.get("/{asiento_id}", summary="Detalle de un asiento con sus líneas")
def detalle_asiento(
    asiento_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("asientos", "ver")),
):
    cab = db.execute(text("SELECT * FROM asiento WHERE id=:i"), {"i": asiento_id}).mappings().first()
    if not cab:
        raise HTTPException(404, f"Asiento {asiento_id} no encontrado")
    lineas = db.execute(
        text("SELECT d.id, d.cuenta_codigo, c.nombre AS cuenta_nombre, d.debe, d.haber, d.descripcion FROM detalle_asiento d JOIN catalogo_cuenta c ON c.codigo=d.cuenta_codigo WHERE d.asiento_id=:i ORDER BY d.id"),
        {"i": asiento_id},
    ).mappings().all()
    debe = round(sum(float(l["debe"]) for l in lineas), 2)
    haber = round(sum(float(l["haber"]) for l in lineas), 2)
    return {"asiento": dict(cab), "detalles": [dict(l) for l in lineas], "total_debe": debe, "total_haber": haber,
            "estado_partida": "CUADRADO" if debe == haber else "DESCUADRADO"}


@router.post("", status_code=201, summary="Registrar un asiento (valida partida doble)")
def crear_asiento(
    data: AsientoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("asientos", "crear")),
):
    if data.tipo not in TIPOS:
        raise HTTPException(400, f"Tipo inválido. Use: {', '.join(TIPOS)}")
    if len(data.detalles) < 2:
        raise HTTPException(400, "El asiento necesita al menos 2 líneas")

    per = db.execute(text("SELECT * FROM periodo_contable WHERE id=:i"), {"i": data.periodo_id}).mappings().first()
    if not per:
        raise HTTPException(400, f"Periodo {data.periodo_id} no existe")
    if per["estado"] == "CERRADO":
        raise HTTPException(400, f"El periodo {per['anio']} está CERRADO, no admite asientos")
    if not (per["fecha_inicio"] <= data.fecha <= per["fecha_fin"]):
        raise HTTPException(400, f"La fecha {data.fecha} está fuera del periodo {per['anio']} ({per['fecha_inicio']} a {per['fecha_fin']})")

    if data.sucursal_id:
        suc = db.execute(text("SELECT id FROM sucursal WHERE id=:i"), {"i": data.sucursal_id}).first()
        if not suc:
            raise HTTPException(400, f"Sucursal {data.sucursal_id} no existe")

    if data.tipo == "APERTURA":
        ya = db.execute(text("SELECT 1 FROM asiento WHERE tipo='APERTURA' AND periodo_id=:p AND estado IN ('PENDIENTE','VIGENTE')"), {"p": data.periodo_id}).first()
        if ya:
            raise HTTPException(409, "Ya existe un asiento de APERTURA vigente en este periodo")

    for idx, lin in enumerate(data.detalles, start=1):
        debe, haber = float(lin.debe or 0), float(lin.haber or 0)
        if debe < 0 or haber < 0:
            raise HTTPException(400, f"Línea {idx}: debe y haber no pueden ser negativos")
        if not ((debe > 0 and haber == 0) or (haber > 0 and debe == 0)):
            raise HTTPException(400, f"Línea {idx} ({lin.cuenta_codigo}): cargue solo debe o solo haber, no ambos ni cero")
        cta = db.execute(text("SELECT codigo FROM catalogo_cuenta WHERE codigo=:c"), {"c": lin.cuenta_codigo}).first()
        if not cta:
            raise HTTPException(400, f"Línea {idx}: la cuenta {lin.cuenta_codigo} no existe en el catálogo")
        hijo = db.execute(text("SELECT 1 FROM catalogo_cuenta WHERE codigo_padre=:c LIMIT 1"), {"c": lin.cuenta_codigo}).first()
        if hijo:
            raise HTTPException(400, f"Línea {idx}: la cuenta {lin.cuenta_codigo} es de agrupación, use una subcuenta hoja")

    debe, haber = _totales(data.detalles)
    if debe != haber:
        raise HTTPException(400, f"Partida descuadrada: debe {debe} != haber {haber}")
    if debe == 0:
        raise HTTPException(400, "El asiento no puede ser de valor cero")

    codigo = (data.codigo or "").strip()
    if codigo:
        dup = db.execute(text("SELECT 1 FROM asiento WHERE codigo=:c"), {"c": codigo}).first()
        if dup:
            raise HTTPException(409, f"El código {codigo} ya existe")
    else:
        nxt = db.execute(text("SELECT COALESCE(MAX(id),0)+1 AS n FROM asiento")).mappings().first()["n"]
        codigo = f"AST-{per['anio']}-{int(nxt):04d}"

    try:
        res = db.execute(
            text("INSERT INTO asiento (codigo, fecha, concepto, tipo, periodo_id, sucursal_id, estado, creado_por) VALUES (:c,:f,:co,:t,:p,:s,'PENDIENTE',:u) RETURNING id"),
            {"c": codigo, "f": data.fecha, "co": data.concepto.strip(), "t": data.tipo, "p": data.periodo_id, "s": data.sucursal_id, "u": user.id},
        )
        nuevo_id = res.mappings().first()["id"]
        for lin in data.detalles:
            db.execute(
                text("INSERT INTO detalle_asiento (asiento_id, cuenta_codigo, debe, haber, descripcion) VALUES (:a,:c,:d,:h,:desc)"),
                {"a": nuevo_id, "c": lin.cuenta_codigo, "d": float(lin.debe or 0), "h": float(lin.haber or 0), "desc": lin.descripcion},
            )
        registrar_evento(
            db,
            actor_id=user.id,
            accion="CREAR",
            entidad="asiento",
            entidad_id=nuevo_id,
            despues={"codigo": codigo, "estado": "PENDIENTE", "debe": debe, "haber": haber},
        )
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"No se pudo guardar el asiento: {e}")

    respuesta = detalle_asiento(nuevo_id, db)
    respuesta["estado"] = "PENDIENTE"
    respuesta["msg"] = (
        f"Asiento {codigo} registrado como PENDIENTE. "
        "Requiere aprobación de un contador para contabilizarse."
    )
    return respuesta


@router.post("/{asiento_id}/aprobar", summary="Aprobar un asiento pendiente")
def aprobar_asiento(
    asiento_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("asientos", "aprobar")),
):
    row = db.execute(text("SELECT id, codigo, estado FROM asiento WHERE id=:id FOR UPDATE"), {"id": asiento_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Asiento no encontrado")
    if row["estado"] != "PENDIENTE":
        raise HTTPException(409, "Solo se pueden aprobar asientos pendientes")
    tot = db.execute(
        text("SELECT COALESCE(SUM(debe),0) debe, COALESCE(SUM(haber),0) haber FROM detalle_asiento WHERE asiento_id=:id"),
        {"id": asiento_id},
    ).mappings().first()
    if round(float(tot["debe"]), 2) != round(float(tot["haber"]), 2) or float(tot["debe"]) <= 0:
        raise HTTPException(409, "El asiento no cuadra y no se puede aprobar")
    db.execute(
        text("UPDATE asiento SET estado='VIGENTE', aprobado_por=:u, aprobado_en=:now WHERE id=:id"),
        {"u": user.id, "now": datetime.utcnow(), "id": asiento_id},
    )
    registrar_evento(db, actor_id=user.id, accion="APROBAR", entidad="asiento", entidad_id=asiento_id, antes={"estado": "PENDIENTE"}, despues={"estado": "VIGENTE", "codigo": row["codigo"]})
    db.commit()
    return detalle_asiento(asiento_id, db)


@router.post("/{asiento_id}/anular", summary="Anular asiento con contrapartida y motivo")
def anular_asiento(
    asiento_id: int,
    data: AnulacionIn,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("asientos", "anular")),
):
    original = db.execute(
        text("SELECT * FROM asiento WHERE id=:id FOR UPDATE"), {"id": asiento_id}
    ).mappings().first()
    if not original:
        raise HTTPException(404, "Asiento no encontrado")
    if original["estado"] != "VIGENTE":
        raise HTTPException(409, "Solo se pueden anular asientos vigentes")
    periodo = db.execute(
        text("SELECT id, anio, fecha_inicio, fecha_fin FROM periodo_contable WHERE id=:id AND estado='ABIERTO'"),
        {"id": data.periodo_id},
    ).mappings().first()
    if not periodo or not (periodo["fecha_inicio"] <= data.fecha_reversion <= periodo["fecha_fin"]):
        raise HTTPException(400, "La fecha de reversión debe estar dentro de un período abierto")

    lineas = db.execute(
        text("SELECT cuenta_codigo, debe, haber, descripcion FROM detalle_asiento WHERE asiento_id=:id ORDER BY id"),
        {"id": asiento_id},
    ).mappings().all()
    next_id = db.execute(text("SELECT nextval(pg_get_serial_sequence('asiento','id')) AS id")).mappings().first()["id"]
    codigo = f"REV-{periodo['anio']}-{int(next_id):04d}"
    try:
        nuevo = db.execute(
            text("""
                INSERT INTO asiento
                    (codigo, fecha, concepto, tipo, periodo_id, sucursal_id, estado,
                     creado_por, aprobado_por, aprobado_en, reverso_de_id)
                VALUES (:codigo, :fecha, :concepto, 'AJUSTE', :periodo, :sucursal, 'VIGENTE',
                        :usuario, :usuario, :ahora, :original)
                RETURNING id
            """),
            {"codigo": codigo, "fecha": data.fecha_reversion,
             "concepto": f"Reversión de {original['codigo']}: {data.motivo.strip()}",
             "periodo": data.periodo_id, "sucursal": original["sucursal_id"],
             "usuario": user.id, "ahora": datetime.utcnow(), "original": asiento_id},
        ).mappings().first()
        reversal_id = nuevo["id"]
        for lin in lineas:
            db.execute(
                text("INSERT INTO detalle_asiento (asiento_id, cuenta_codigo, debe, haber, descripcion) VALUES (:a,:c,:d,:h,:desc)"),
                {"a": reversal_id, "c": lin["cuenta_codigo"], "d": lin["haber"], "h": lin["debe"], "desc": f"Reversión: {lin['descripcion'] or original['concepto']}"},
            )
        db.execute(
            text("UPDATE asiento SET estado='ANULADO', anulado_por=:u, anulado_en=:now, motivo_anulacion=:motivo WHERE id=:id"),
            {"u": user.id, "now": datetime.utcnow(), "motivo": data.motivo.strip(), "id": asiento_id},
        )
        registrar_evento(db, actor_id=user.id, accion="ANULAR", entidad="asiento", entidad_id=asiento_id,
                         motivo=data.motivo.strip(), antes={"estado": "VIGENTE", "codigo": original["codigo"]},
                         despues={"estado": "ANULADO", "reverso_id": reversal_id, "reverso_codigo": codigo})
        registrar_evento(db, actor_id=user.id, accion="REVERSAR", entidad="asiento", entidad_id=reversal_id,
                         motivo=data.motivo.strip(), despues={"estado": "VIGENTE", "reverso_de_id": asiento_id, "codigo": codigo})
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(500, f"No se pudo anular el asiento: {exc}")
    return {"anulado": detalle_asiento(asiento_id, db), "reversion": detalle_asiento(reversal_id, db)}
