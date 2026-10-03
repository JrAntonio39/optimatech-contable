from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

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


def _totales(detalles):
    debe = round(sum(float(d.debe or 0) for d in detalles), 2)
    haber = round(sum(float(d.haber or 0) for d in detalles), 2)
    return debe, haber


@router.get("", summary="Lista asientos con sus totales")
def listar_asientos(
    db: Session = Depends(get_db),
    tipo: str = Query(None, description="APERTURA | DIARIO | AJUSTE | CIERRE"),
    periodo_id: int = Query(None),
    sucursal_id: int = Query(None),
):
    query = """
        SELECT a.id, a.codigo, a.fecha, a.concepto, a.tipo, a.periodo_id, a.sucursal_id, a.estado,
               COALESCE(SUM(d.debe),0) AS total_debe, COALESCE(SUM(d.haber),0) AS total_haber
        FROM asiento a LEFT JOIN detalle_asiento d ON d.asiento_id = a.id
    """
    conds, params = [], {}
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
def totales_asientos(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM v_asiento_totales ORDER BY codigo")).mappings().all()
    return {"total": len(rows), "totales": [dict(r) for r in rows]}


@router.get("/{asiento_id}", summary="Detalle de un asiento con sus líneas")
def detalle_asiento(asiento_id: int, db: Session = Depends(get_db)):
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
def crear_asiento(data: AsientoCreate, db: Session = Depends(get_db)):
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
        ya = db.execute(text("SELECT 1 FROM asiento WHERE tipo='APERTURA' AND periodo_id=:p AND estado='VIGENTE'"), {"p": data.periodo_id}).first()
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
            text("INSERT INTO asiento (codigo, fecha, concepto, tipo, periodo_id, sucursal_id) VALUES (:c,:f,:co,:t,:p,:s) RETURNING id"),
            {"c": codigo, "f": data.fecha, "co": data.concepto.strip(), "t": data.tipo, "p": data.periodo_id, "s": data.sucursal_id},
        )
        nuevo_id = res.mappings().first()["id"]
        for lin in data.detalles:
            db.execute(
                text("INSERT INTO detalle_asiento (asiento_id, cuenta_codigo, debe, haber, descripcion) VALUES (:a,:c,:d,:h,:desc)"),
                {"a": nuevo_id, "c": lin.cuenta_codigo, "d": float(lin.debe or 0), "h": float(lin.haber or 0), "desc": lin.descripcion},
            )
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"No se pudo guardar el asiento: {e}")

    return detalle_asiento(nuevo_id, db)
