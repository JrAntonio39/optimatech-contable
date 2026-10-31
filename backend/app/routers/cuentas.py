from fastapi import APIRouter, Depends, Query, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.auth import Usuario
from app.routers.auth import require_permission
from app.services.auditoria import registrar

router = APIRouter(prefix="/api/cuentas", tags=["Cuentas"])

NATURALEZAS = ("Deudora", "Acreedora", "Deudora o Acreedora")


class CuentaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(..., max_length=150)
    naturaleza: str = Field(..., description="Deudora | Acreedora | Deudora o Acreedora")
    codigo_padre: str = Field(..., min_length=3, max_length=20)


@router.get("", summary="Lista todas las cuentas del catálogo")
def listar_cuentas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("cuentas", "ver")),
    nivel: int = Query(None, description="Filtrar por nivel 1-5"),
    q: str = Query(None, description="Buscar por nombre o código"),
):
    query = "SELECT codigo, nombre, naturaleza, nivel, codigo_padre FROM catalogo_cuenta"
    conds = []
    params = {}
    if nivel is not None:
        conds.append("nivel = :nivel")
        params["nivel"] = nivel
    if q:
        conds.append("(codigo ILIKE :q OR nombre ILIKE :q)")
        params["q"] = f"%{q}%"
    if conds:
        query += " WHERE " + " AND ".join(conds)
    query += " ORDER BY codigo"
    rows = db.execute(text(query), params).mappings().all()
    return {"total": len(rows), "cuentas": list(rows)}

@router.get("/mayor", summary="Solo cuentas de mayor (nivel 3, las del manual)")
def cuentas_mayor(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("cuentas", "ver"))):
    rows = db.execute(text("SELECT codigo, nombre, naturaleza FROM catalogo_cuenta WHERE nivel=3 ORDER BY codigo")).mappings().all()
    return {"total": len(rows), "cuentas": list(rows)}

@router.post("", status_code=201, summary="Agregar una cuenta al catálogo")
def crear_cuenta(
    data: CuentaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("cuentas", "crear")),
):
    nombre = data.nombre.strip()
    if not nombre:
        raise HTTPException(400, "El nombre de la cuenta es obligatorio")
    if data.naturaleza not in NATURALEZAS:
        raise HTTPException(400, f"Naturaleza inválida. Use: {', '.join(NATURALEZAS)}")

    # Bloquea la cuenta padre mientras asignamos el siguiente código de su nivel.
    # Así una cuenta nueva no puede saltarse la jerarquía ni colisionar con otra alta concurrente.
    padre = db.execute(
        text("SELECT codigo, nivel FROM catalogo_cuenta WHERE codigo=:c FOR UPDATE"),
        {"c": data.codigo_padre.strip()},
    ).mappings().first()
    if not padre:
        raise HTTPException(400, f"La cuenta padre {data.codigo_padre} no existe")
    if padre["nivel"] >= 5:
        raise HTTPException(400, "Una cuenta de nivel 5 no puede tener subcuentas")
    segmentos = padre["codigo"].split(".")
    formato_raiz = padre["nivel"] == 1 and len(segmentos) == 2 and segmentos[1] == "0"
    formato_subcuenta = padre["nivel"] > 1 and len(segmentos) == padre["nivel"]
    if not (formato_raiz or formato_subcuenta) or not all(x.isdigit() for x in segmentos):
        raise HTTPException(400, "La cuenta padre no tiene un código jerárquico válido")

    nuevo_nivel = padre["nivel"] + 1
    ancho_segmento = 1 if nuevo_nivel <= 3 else 2
    hermanos = db.execute(
        text("SELECT codigo FROM catalogo_cuenta WHERE codigo_padre=:p"),
        {"p": padre["codigo"]},
    ).mappings().all()
    numeros = []
    for hermano in hermanos:
        sufijo = hermano["codigo"].rsplit(".", 1)[-1]
        if sufijo.isdigit():
            numeros.append(int(sufijo))
    siguiente = max(numeros, default=0) + 1
    maximo = 9 if ancho_segmento == 1 else 99
    if siguiente > maximo:
        raise HTTPException(409, "La cuenta padre ya alcanzó el máximo de subcuentas permitido")
    if formato_raiz:
        codigo = f"{segmentos[0]}.{siguiente:0{ancho_segmento}d}"
    else:
        codigo = f"{padre['codigo']}.{siguiente:0{ancho_segmento}d}"
    if db.execute(text("SELECT 1 FROM catalogo_cuenta WHERE codigo=:c"), {"c": codigo}).first():
        raise HTTPException(409, f"El código automático {codigo} ya existe; revise el catálogo")

    try:
        db.execute(
            text("INSERT INTO catalogo_cuenta (codigo, nombre, naturaleza, nivel, codigo_padre) VALUES (:c, :n, :nat, :niv, :p)"),
            {"c": codigo, "n": nombre, "nat": data.naturaleza, "niv": nuevo_nivel, "p": padre["codigo"]},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    row = db.execute(
        text("SELECT codigo, nombre, naturaleza, nivel, codigo_padre FROM catalogo_cuenta WHERE codigo=:c"),
        {"c": codigo},
    ).mappings().first()
    return {"msg": "Cuenta creada con código automático", "cuenta": dict(row)}

@router.get("/{codigo}", summary="Detalle de una cuenta")
def detalle_cuenta(
    codigo: str,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("cuentas", "ver")),
):
    row = db.execute(text("SELECT codigo, nombre, naturaleza, nivel, codigo_padre FROM catalogo_cuenta WHERE codigo=:c"), {"c": codigo}).mappings().first()
    if not row:
        raise HTTPException(404, f"Cuenta {codigo} no encontrada")
    hijos = db.execute(text("SELECT codigo, nombre FROM catalogo_cuenta WHERE codigo_padre=:c ORDER BY codigo"), {"c": codigo}).mappings().all()
    return {"cuenta": dict(row), "hijos": list(hijos)}


@router.delete("/{codigo}", status_code=204, summary="Eliminar una cuenta sin movimientos ni dependencias")
def eliminar_cuenta(
    codigo: str,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("cuentas", "eliminar")),
):
    cuenta = db.execute(
        text("SELECT codigo, nombre, naturaleza, nivel, codigo_padre FROM catalogo_cuenta WHERE codigo=:c FOR UPDATE"),
        {"c": codigo},
    ).mappings().first()
    if not cuenta:
        raise HTTPException(404, f"Cuenta {codigo} no encontrada")

    dependencias = []
    if db.execute(text("SELECT 1 FROM catalogo_cuenta WHERE codigo_padre=:c LIMIT 1"), {"c": codigo}).first():
        dependencias.append("subcuentas")

    # Estas relaciones tienen claves foráneas a catalogo_cuenta en el esquema base.
    referencias = (
        ("detalle_asiento", "cuenta_codigo", "asientos contables"),
        ("cliente", "cuenta_codigo", "clientes"),
        ("proveedor", "cuenta_codigo", "proveedores"),
        ("empleado", "cuenta_anticipo_codigo", "empleados"),
        ("compra_detalle", "cuenta_activo_codigo", "compras"),
        ("factura_detalle", "cuenta_ingreso_codigo", "facturas"),
    )
    for tabla, columna, etiqueta in referencias:
        existe = db.execute(
            text(f"SELECT 1 FROM {tabla} WHERE {columna}=:c LIMIT 1"), {"c": codigo}
        ).first()
        if existe:
            dependencias.append(etiqueta)

    # planilla_pago se instala mediante una migración opcional.
    tiene_pagos_planilla = db.execute(text("SELECT to_regclass('public.planilla_pago')")).scalar()
    if tiene_pagos_planilla and db.execute(
        text("SELECT 1 FROM planilla_pago WHERE cuenta_pago_codigo=:c LIMIT 1"), {"c": codigo}
    ).first():
        dependencias.append("pagos de planilla")

    if dependencias:
        db.rollback()
        detalle = ", ".join(dependencias)
        raise HTTPException(409, f"No se puede eliminar la cuenta: tiene referencias en {detalle}.")

    try:
        registrar(
            db, user, "cuentas", "catalogo_cuenta", "eliminar",
            registro_codigo=codigo, datos_antes=dict(cuenta),
        )
        db.execute(text("DELETE FROM catalogo_cuenta WHERE codigo=:c"), {"c": codigo})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "No se puede eliminar la cuenta porque otra operación la está utilizando.")
    except Exception:
        db.rollback()
        raise
    return Response(status_code=204)
