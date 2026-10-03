from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from app.database import get_db

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


def _periodo_filtro(periodo_id: Optional[int], db: Session):
    """Valida el periodo y devuelve (condición SQL, params)."""
    if periodo_id is None:
        return "", {}
    per = db.execute(
        text("SELECT id, anio FROM periodo_contable WHERE id=:i"),
        {"i": periodo_id},
    ).mappings().first()
    if not per:
        raise HTTPException(400, f"Periodo {periodo_id} no existe")
    return "AND a.periodo_id = :p", {"p": periodo_id}


@router.get("/mayor", summary="Libro Mayor: totales por cuenta hoja con movimiento")
def libro_mayor(
    db: Session = Depends(get_db),
    periodo_id: Optional[int] = Query(None, description="Filtrar por periodo"),
    q: Optional[str] = Query(None, description="Buscar por código o nombre"),
):
    cond_p, par = _periodo_filtro(periodo_id, db)
    cond_q = ""
    if q:
        cond_q = "AND (c.codigo ILIKE :q OR c.nombre ILIKE :q)"
        par["q"] = f"%{q}%"
    rows = db.execute(
        text(f"""
        SELECT c.codigo, c.nombre, c.naturaleza,
               COALESCE(SUM(d.debe),0) AS total_debe,
               COALESCE(SUM(d.haber),0) AS total_haber,
               COALESCE(SUM(d.debe - d.haber),0) AS saldo
          FROM catalogo_cuenta c
          JOIN detalle_asiento d ON d.cuenta_codigo = c.codigo
          JOIN asiento a ON a.id = d.asiento_id AND a.estado = 'VIGENTE'
         WHERE NOT EXISTS (SELECT 1 FROM catalogo_cuenta h WHERE h.codigo_padre = c.codigo)
           {cond_p} {cond_q}
         GROUP BY c.codigo, c.nombre, c.naturaleza
         ORDER BY c.codigo
        """),
        par,
    ).mappings().all()
    out = []
    for r in rows:
        r = dict(r)
        r["total_debe"] = float(r["total_debe"])
        r["total_haber"] = float(r["total_haber"])
        r["saldo"] = float(r["saldo"])
        out.append(r)
    return {"total": len(out), "periodo_id": periodo_id, "cuentas": out}


@router.get("/mayor/{codigo}", summary="Movimientos de una cuenta (mayorización)")
def mayor_cuenta(
    codigo: str,
    db: Session = Depends(get_db),
    periodo_id: Optional[int] = Query(None, description="Filtrar por periodo"),
):
    cta = db.execute(
        text("SELECT codigo, nombre, naturaleza FROM catalogo_cuenta WHERE codigo=:c"),
        {"c": codigo},
    ).mappings().first()
    if not cta:
        raise HTTPException(404, f"Cuenta {codigo} no encontrada")
    cond_p, par = _periodo_filtro(periodo_id, db)
    par["c"] = codigo
    movs = db.execute(
        text(f"""
        SELECT a.fecha, a.codigo AS folio, a.concepto, a.tipo,
               d.debe, d.haber, d.descripcion
          FROM detalle_asiento d
          JOIN asiento a ON a.id = d.asiento_id AND a.estado = 'VIGENTE'
         WHERE d.cuenta_codigo = :c {cond_p}
         ORDER BY a.fecha, a.id, d.id
        """),
        par,
    ).mappings().all()
    lineas, saldo = [], 0.0
    for m in movs:
        m = dict(m)
        m["debe"] = float(m["debe"])
        m["haber"] = float(m["haber"])
        saldo = round(saldo + m["debe"] - m["haber"], 2)
        m["saldo_acumulado"] = saldo
        lineas.append(m)
    debe = round(sum(m["debe"] for m in lineas), 2)
    haber = round(sum(m["haber"] for m in lineas), 2)
    return {
        "cuenta": dict(cta),
        "periodo_id": periodo_id,
        "movimientos": lineas,
        "total_debe": debe,
        "total_haber": haber,
        "saldo_final": round(debe - haber, 2),
    }


@router.get("/balanza", summary="Balanza de Comprobación (sumas y saldos, nivel 3)")
def balanza(
    db: Session = Depends(get_db),
    periodo_id: Optional[int] = Query(None, description="Filtrar por periodo"),
):
    cond_p, par = _periodo_filtro(periodo_id, db)
    rows = db.execute(
        text(f"""
        SELECT c.codigo, c.nombre,
               COALESCE(SUM(d.debe),0) AS sumas_debe,
               COALESCE(SUM(d.haber),0) AS sumas_haber,
               CASE WHEN COALESCE(SUM(d.debe - d.haber),0) > 0
                    THEN COALESCE(SUM(d.debe - d.haber),0) ELSE 0 END AS saldo_deudor,
               CASE WHEN COALESCE(SUM(d.debe - d.haber),0) < 0
                    THEN ABS(COALESCE(SUM(d.debe - d.haber),0)) ELSE 0 END AS saldo_acreedor
          FROM catalogo_cuenta c
          JOIN detalle_asiento d
            ON d.cuenta_codigo = c.codigo OR d.cuenta_codigo LIKE c.codigo || '.%'
          JOIN asiento a ON a.id = d.asiento_id AND a.estado = 'VIGENTE'
         WHERE c.nivel = 3 {cond_p}
         GROUP BY c.codigo, c.nombre
        HAVING COALESCE(SUM(d.debe),0) + COALESCE(SUM(d.haber),0) > 0
         ORDER BY c.codigo
        """),
        par,
    ).mappings().all()
    lineas = []
    for r in rows:
        r = dict(r)
        for k in ("sumas_debe", "sumas_haber", "saldo_deudor", "saldo_acreedor"):
            r[k] = float(r[k])
        lineas.append(r)
    totales = {
        k: round(sum(l[k] for l in lineas), 2)
        for k in ("sumas_debe", "sumas_haber", "saldo_deudor", "saldo_acreedor")
    }
    return {
        "total": len(lineas),
        "periodo_id": periodo_id,
        "lineas": lineas,
        "totales": totales,
        "cuadrada": totales["sumas_debe"] == totales["sumas_haber"]
        and totales["saldo_deudor"] == totales["saldo_acreedor"],
    }
