from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from app.database import get_db
from app.models.auth import Usuario
from app.routers.auth import require_permission

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
    user: Usuario = Depends(require_permission("reportes", "ver")),
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
    user: Usuario = Depends(require_permission("reportes", "ver")),
    periodo_id: Optional[int] = Query(None, description="Filtrar por periodo"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    cta = db.execute(
        text("SELECT codigo, nombre, naturaleza FROM catalogo_cuenta WHERE codigo=:c"),
        {"c": codigo},
    ).mappings().first()
    if not cta:
        raise HTTPException(404, f"Cuenta {codigo} no encontrada")
    cond_p, par = _periodo_filtro(periodo_id, db)
    par["c"] = codigo
    base_from = """
          FROM detalle_asiento d
          JOIN asiento a ON a.id = d.asiento_id AND a.estado = 'VIGENTE'
         WHERE d.cuenta_codigo = :c
    """
    params = dict(par)
    params["c"] = codigo
    agregados = db.execute(
        text(f"""
        SELECT COUNT(*) AS total,
               COALESCE(SUM(d.debe),0) AS total_debe,
               COALESCE(SUM(d.haber),0) AS total_haber
        {base_from} {cond_p}
        """),
        params,
    ).mappings().first()
    movs = db.execute(
        text(f"""
        WITH pagina AS (
            SELECT d.id AS movimiento_id, a.id AS asiento_id, a.fecha,
                   a.codigo AS folio, a.concepto, a.tipo,
                   d.debe, d.haber, d.descripcion
            {base_from} {cond_p}
             ORDER BY a.fecha, a.id, d.id
             LIMIT :lim OFFSET :off
        ), saldo_anterior AS (
            SELECT COALESCE(SUM(d.debe - d.haber), 0) AS saldo
            {base_from} {cond_p}
             AND (a.fecha, a.id, d.id) < (
                 SELECT p.fecha, p.asiento_id, p.movimiento_id
                   FROM pagina p
                  ORDER BY p.fecha, p.asiento_id, p.movimiento_id
                  LIMIT 1
             )
        )
        SELECT p.movimiento_id, p.fecha, p.folio, p.concepto, p.tipo,
               p.debe, p.haber, p.descripcion,
               s.saldo + SUM(p.debe - p.haber) OVER (
                   ORDER BY p.fecha, p.asiento_id, p.movimiento_id
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
               ) AS saldo_acumulado
          FROM pagina p
          CROSS JOIN saldo_anterior s
         ORDER BY p.fecha, p.asiento_id, p.movimiento_id
        """),
        {**params, "lim": limit, "off": offset},
    ).mappings().all()
    lineas = []
    for m in movs:
        m = dict(m)
        m["debe"] = float(m["debe"])
        m["haber"] = float(m["haber"])
        m["saldo_acumulado"] = round(float(m["saldo_acumulado"]), 2)
        lineas.append(m)
    debe = round(float(agregados["total_debe"]), 2)
    haber = round(float(agregados["total_haber"]), 2)
    return {
        "cuenta": dict(cta),
        "periodo_id": periodo_id,
        "movimientos": lineas,
        "total_debe": debe,
        "total_haber": haber,
        "saldo_final": round(debe - haber, 2),
        "total_movimientos": int(agregados["total"]),
        "limit": limit,
        "offset": offset,
    }


@router.get("/balanza", summary="Balanza de Comprobación (sumas y saldos, nivel 3)")
def balanza(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("reportes", "ver")),
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


def _saldos_nivel3(clase: str, db: Session, cond_p: str, par: dict):
    """Saldos de cuentas de mayor (nivel 3) de una clase, agregando sus hojas.

    clase: '1'..'7'. Devuelve lista {codigo, nombre, rubro, debe, haber}.
    """
    params = dict(par)
    params["pat"] = f"{clase}.%"
    rows = db.execute(
        text(f"""
        SELECT c.codigo, c.nombre, c.codigo_padre AS rubro,
               COALESCE(SUM(d.debe),0) AS debe,
               COALESCE(SUM(d.haber),0) AS haber
          FROM catalogo_cuenta c
          JOIN detalle_asiento d
            ON d.cuenta_codigo = c.codigo OR d.cuenta_codigo LIKE c.codigo || '.%'
          JOIN asiento a ON a.id = d.asiento_id AND a.estado = 'VIGENTE'
         WHERE c.nivel = 3 AND c.codigo LIKE :pat {cond_p}
         GROUP BY c.codigo, c.nombre, c.codigo_padre
        HAVING COALESCE(SUM(d.debe),0) + COALESCE(SUM(d.haber),0) > 0
         ORDER BY c.codigo
        """),
        params,
    ).mappings().all()
    out = []
    for r in rows:
        r = dict(r)
        r["debe"] = float(r["debe"])
        r["haber"] = float(r["haber"])
        out.append(r)
    return out


@router.get("/resultados", summary="Estado de resultados de varios pasos")
def resultados(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("reportes", "ver")),
    periodo_id: Optional[int] = Query(None, description="Filtrar por periodo"),
):
    cond_p, par = _periodo_filtro(periodo_id, db)

    ing = _saldos_nivel3("5", db, cond_p, par)
    lineas_ing = [
        {"codigo": l["codigo"], "nombre": l["nombre"],
         "total": round(l["haber"] - l["debe"], 2)}
        for l in ing
    ]
    total_ing = round(sum(l["total"] for l in lineas_ing), 2)

    gas = _saldos_nivel3("4", db, cond_p, par)
    lineas_gas = [
        {"codigo": l["codigo"], "nombre": l["nombre"],
         "total": round(l["debe"] - l["haber"], 2)}
        for l in gas
    ]
    total_gas = round(sum(l["total"] for l in lineas_gas), 2)

    # En el catálogo OptimaTech, las cuentas de nivel 3 bajo 4.1.1 y 4.1.2
    # representan costos directos; 4.1.3 y 4.1.4 gastos de operación; 4.1.5
    # y 4.1.6 gastos financieros y otros. La clase 5.1 agrupa ingresos
    # operacionales y 5.2 otros ingresos.
    def seccion(lineas, prefijos):
        incluidas = [l for l in lineas if l["codigo"].startswith(prefijos)]
        return {
            "total": round(sum(l["total"] for l in incluidas), 2),
            "lineas": incluidas,
        }

    ingresos_operacionales = seccion(lineas_ing, ("5.1",))
    otros_ingresos = {
        "total": round(total_ing - ingresos_operacionales["total"], 2),
        "lineas": [l for l in lineas_ing if not l["codigo"].startswith("5.1")],
    }
    costos_ventas = seccion(lineas_gas, ("4.1.1", "4.1.2"))
    gastos_operacionales = seccion(lineas_gas, ("4.1.3", "4.1.4"))
    gastos_financieros = seccion(lineas_gas, ("4.1.5",))
    otros_gastos = {
        "total": round(
            total_gas - costos_ventas["total"] - gastos_operacionales["total"] - gastos_financieros["total"],
            2,
        ),
        "lineas": [
            l for l in lineas_gas
            if not l["codigo"].startswith(("4.1.1", "4.1.2", "4.1.3", "4.1.4", "4.1.5"))
        ],
    }

    utilidad_bruta = round(ingresos_operacionales["total"] - costos_ventas["total"], 2)
    utilidad_operativa = round(utilidad_bruta - gastos_operacionales["total"], 2)
    utilidad = round(
        utilidad_operativa + otros_ingresos["total"] - gastos_financieros["total"] - otros_gastos["total"],
        2,
    )
    resultado = "UTILIDAD" if utilidad > 0 else ("PERDIDA" if utilidad < 0 else "EQUILIBRIO")
    return {
        "periodo_id": periodo_id,
        # Se conservan estos campos para los consumidores existentes del reporte.
        "ingresos": {"total": total_ing, "lineas": lineas_ing},
        "gastos": {"total": total_gas, "lineas": lineas_gas},
        "ingresos_operacionales": ingresos_operacionales,
        "costos_ventas": costos_ventas,
        "utilidad_bruta": utilidad_bruta,
        "gastos_operacionales": gastos_operacionales,
        "utilidad_operativa": utilidad_operativa,
        "otros_ingresos": otros_ingresos,
        "gastos_financieros": gastos_financieros,
        "otros_gastos": otros_gastos,
        "utilidad_neta": utilidad,
        "resultado": resultado,
    }


@router.get("/balance-general", summary="Balance General (1 = 2 + 3 + resultado)")
def balance_general(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("reportes", "ver")),
    periodo_id: Optional[int] = Query(None, description="Filtrar por periodo"),
):
    # El Balance General es una fotografía a la fecha de cierre: debe conservar
    # los saldos anteriores. Si hay una apertura vigente, esta reemplaza los
    # períodos anteriores como saldo inicial; desde ella se suman los demás
    # movimientos hasta el cierre seleccionado. Sin apertura, se acumula el
    # historial completo hasta esa fecha.
    if periodo_id is None:
        periodo = db.execute(
            text("""
                SELECT id, anio, fecha_fin
                  FROM periodo_contable
                 ORDER BY fecha_fin DESC, id DESC
                 LIMIT 1
            """)
        ).mappings().first()
    else:
        periodo = db.execute(
            text("""
                SELECT id, anio, fecha_fin
                  FROM periodo_contable
                 WHERE id = :id
            """),
            {"id": periodo_id},
        ).mappings().first()
        if not periodo:
            raise HTTPException(400, f"Periodo {periodo_id} no existe")

    apertura = None
    if periodo:
        apertura = db.execute(
            text("""
                SELECT a.id, a.fecha
                  FROM asiento a
                 WHERE a.tipo = 'APERTURA'
                   AND a.estado = 'VIGENTE'
                   AND a.fecha <= :fecha_fin
                 ORDER BY a.fecha DESC, a.id DESC
                 LIMIT 1
            """),
            {"fecha_fin": periodo["fecha_fin"]},
        ).mappings().first()

    if periodo and apertura:
        cond_p = """AND a.fecha <= :fecha_fin
                      AND (a.id = :apertura_id OR
                           (a.tipo <> 'APERTURA' AND a.fecha >= :fecha_apertura))"""
        par = {
            "fecha_fin": periodo["fecha_fin"],
            "apertura_id": apertura["id"],
            "fecha_apertura": apertura["fecha"],
        }
    elif periodo:
        cond_p = "AND a.fecha <= :fecha_fin"
        par = {"fecha_fin": periodo["fecha_fin"]}
    else:
        # Instalación sin períodos contables todavía.
        cond_p, par = "AND 1 = 0", {}

    def seccion(clase: str, signo: int):
        """signo +1: saldo = debe-haber (Activo). -1: saldo = haber-debe."""
        saldos = _saldos_nivel3(clase, db, cond_p, par)
        por_rubro: dict = {}
        for l in saldos:
            s = round(signo * (l["debe"] - l["haber"]), 2)
            rub = por_rubro.setdefault(
                l["rubro"],
                {"codigo": l["rubro"], "nombre": "", "saldo": 0.0, "lineas": []},
            )
            rub["lineas"].append({"codigo": l["codigo"], "nombre": l["nombre"], "saldo": s})
            rub["saldo"] = round(rub["saldo"] + s, 2)
        nombres = {
            r["codigo"]: r["nombre"]
            for r in db.execute(
                text("SELECT codigo, nombre FROM catalogo_cuenta WHERE nivel = 2")
            ).mappings().all()
        }
        rubros = []
        for cod in sorted(por_rubro):
            por_rubro[cod]["nombre"] = nombres.get(cod, "")
            rubros.append(por_rubro[cod])
        return rubros, round(sum(r["saldo"] for r in rubros), 2)

    rub_act, tot_act = seccion("1", +1)
    rub_pas, tot_pas = seccion("2", -1)
    rub_pat, tot_pat_rub = seccion("3", -1)

    res = resultados(db=db, periodo_id=periodo["id"]) if periodo else {"utilidad_neta": 0.0}
    utilidad = res["utilidad_neta"]
    tot_pat = round(tot_pat_rub + utilidad, 2)
    tot_pas_pat = round(tot_pas + tot_pat, 2)
    diferencia = round(tot_act - tot_pas_pat, 2)
    return {
        "periodo_id": periodo["id"] if periodo else None,
        "fecha_corte": str(periodo["fecha_fin"]) if periodo else None,
        "fecha_apertura": str(apertura["fecha"]) if apertura else None,
        "activo": {"total": tot_act, "rubros": rub_act},
        "pasivo": {"total": tot_pas, "rubros": rub_pas},
        "patrimonio": {
            "total": tot_pat,
            "rubros": rub_pat,
            "resultado_ejercicio": utilidad,
        },
        "total_pasivo_patrimonio": tot_pas_pat,
        "cuadrado": diferencia == 0,
        "diferencia": diferencia,
    }
