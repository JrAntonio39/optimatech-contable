"""Proyectos y análisis de rentabilidad a partir de operaciones contabilizadas."""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import Usuario
from app.routers.auth import require_permission
from app.services.auditoria import registrar

router = APIRouter(prefix="/api/proyectos", tags=["Proyectos y rentabilidad"])

# Las asignaciones se conservan como historial si se anula su documento fuente,
# pero dejan de consumir saldo y de afectar la rentabilidad.
ASIGNACION_FUENTE_VIGENTE_SQL = """(
    (pa.fuente_tipo='FACTURA' AND EXISTS (
        SELECT 1 FROM factura_detalle fd JOIN factura f ON f.id=fd.factura_id
        JOIN asiento a ON a.id=f.asiento_id
        WHERE fd.id=pa.fuente_detalle_id AND a.estado='VIGENTE'
          AND f.tipo_dte IN ('CCF','FCON')
    )) OR
    (pa.fuente_tipo='COMPRA' AND EXISTS (
        SELECT 1 FROM compra_detalle cd JOIN compra c ON c.id=cd.compra_id
        JOIN asiento a ON a.id=c.asiento_id
        WHERE cd.id=pa.fuente_detalle_id AND a.estado='VIGENTE'
          AND c.tipo_doc <> 'NCR'
    )) OR
    (pa.fuente_tipo='PLANILLA' AND EXISTS (
        SELECT 1 FROM planilla_detalle pd JOIN planilla p ON p.id=pd.planilla_id
        JOIN asiento a ON a.id=p.asiento_id
        WHERE pd.id=pa.fuente_detalle_id AND a.estado='VIGENTE'
    ))
)"""


class ProyectoIn(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: str = Field(..., min_length=3, max_length=160)
    descripcion: Optional[str] = Field(None, max_length=2000)
    tipo: Literal["CCTV", "DESARROLLO", "HOSTING", "SOPORTE", "LICENCIAS", "EQUIPO", "OTRO"] = "OTRO"
    cliente_id: Optional[int] = Field(None, gt=0)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None

    @field_validator("codigo", mode="before")
    @classmethod
    def limpiar_codigo(cls, value):
        if value is None or not str(value).strip():
            return None
        return str(value).strip().upper()

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, value):
        return " ".join(str(value or "").split())

    @field_validator("descripcion", mode="before")
    @classmethod
    def limpiar_descripcion(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        return value or None


class ProyectoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: str = Field(..., min_length=3, max_length=160)
    descripcion: Optional[str] = Field(None, max_length=2000)
    tipo: Literal["CCTV", "DESARROLLO", "HOSTING", "SOPORTE", "LICENCIAS", "EQUIPO", "OTRO"]
    cliente_id: Optional[int] = Field(None, gt=0)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Literal["ABIERTO", "COMPLETADO", "CANCELADO"]

    @field_validator("codigo", mode="before")
    @classmethod
    def limpiar_codigo(cls, value):
        if value is None or not str(value).strip():
            return None
        return str(value).strip().upper()

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, value):
        return " ".join(str(value or "").split())

    @field_validator("descripcion", mode="before")
    @classmethod
    def limpiar_descripcion(cls, value):
        if value is None:
            return None
        value = str(value).strip()
        return value or None


class AsignacionIn(BaseModel):
    fuente_tipo: Literal["FACTURA", "COMPRA", "PLANILLA"]
    fuente_detalle_id: int = Field(..., gt=0)
    categoria: Literal["INGRESO", "COSTO_DIRECTO", "MANO_OBRA", "COSTO_INDIRECTO"]
    monto: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)


def _money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _source_is_current(alias: str = "pa") -> str:
    return ASIGNACION_FUENTE_VIGENTE_SQL.replace("pa.", f"{alias}.")


def _project(db: Session, project_id: int, lock: bool = False):
    suffix = " FOR UPDATE" if lock else ""
    row = db.execute(text(f"SELECT * FROM proyecto WHERE id=:id{suffix}"), {"id": project_id}).mappings().first()
    if not row:
        raise HTTPException(404, "No se encontró el proyecto")
    return row


def _source(db: Session, source_type: str, detail_id: int, lock: bool = False):
    """Devuelve únicamente una línea de un documento con asiento vigente."""
    lock_clause = " FOR UPDATE OF d" if lock else ""
    queries = {
        "FACTURA": f"""SELECT d.id fuente_detalle_id, f.numero documento, f.fecha,
            c.nombre tercero, d.descripcion,
            ROUND(d.cantidad*d.precio_unitario,2) monto_total
          FROM factura_detalle d JOIN factura f ON f.id=d.factura_id
          JOIN asiento a ON a.id=f.asiento_id AND a.estado='VIGENTE'
          JOIN cliente c ON c.id=f.cliente_id
          WHERE d.id=:id AND f.tipo_dte IN ('CCF','FCON') {lock_clause}""",
        "COMPRA": f"""SELECT d.id fuente_detalle_id, c.numero documento, c.fecha,
            p.nombre tercero, d.descripcion,
            ROUND(d.cantidad*d.precio_unitario,2) monto_total
          FROM compra_detalle d JOIN compra c ON c.id=d.compra_id
          JOIN asiento a ON a.id=c.asiento_id AND a.estado='VIGENTE'
          JOIN proveedor p ON p.id=c.proveedor_id
          WHERE d.id=:id AND c.tipo_doc <> 'NCR' {lock_clause}""",
        "PLANILLA": f"""SELECT d.id fuente_detalle_id, p.codigo documento, p.fecha_pago fecha,
            e.nombres || ' ' || e.apellidos tercero,
            'Salario y aportes patronales: ' || e.cargo descripcion,
            ROUND(d.salario_base*d.dias_trabajados/30 + d.horas_extra + d.bonificaciones + d.comisiones,2)
              + d.isss_patronal + d.afp_patronal AS monto_total
          FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id
          JOIN asiento a ON a.id=p.asiento_id AND a.estado='VIGENTE'
          JOIN empleado e ON e.id=d.empleado_id
          WHERE d.id=:id {lock_clause}""",
    }
    query = queries.get(source_type)
    if not query:
        raise HTTPException(400, "Tipo de origen no válido")
    return db.execute(text(query), {"id": detail_id}).mappings().first()


def _allocated_total(db: Session, source_type: str, detail_id: int) -> Decimal:
    value = db.execute(text(f"""SELECT COALESCE(SUM(pa.monto),0)
        FROM proyecto_asignacion pa
        WHERE pa.fuente_tipo=:tipo AND pa.fuente_detalle_id=:id
          AND {ASIGNACION_FUENTE_VIGENTE_SQL}"""),
        {"tipo": source_type, "id": detail_id}).scalar_one()
    return _money(value)


@router.get("")
def listar_proyectos(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    rows = db.execute(text("""SELECT p.id,p.codigo,p.nombre,p.descripcion,p.tipo,p.cliente_id,
        c.nombre cliente,p.fecha_inicio,p.fecha_fin,p.estado,p.creado_en,p.actualizado_en
        FROM proyecto p LEFT JOIN cliente c ON c.id=p.cliente_id
        ORDER BY CASE p.estado WHEN 'ABIERTO' THEN 0 ELSE 1 END,p.nombre""")).mappings().all()
    return {"proyectos": [dict(row) for row in rows]}


@router.post("", status_code=201)
def crear_proyecto(data: ProyectoIn, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "crear"))):
    if data.fecha_inicio and data.fecha_fin and data.fecha_fin < data.fecha_inicio:
        raise HTTPException(400, "La fecha de cierre no puede ser anterior al inicio")
    if data.cliente_id and not db.execute(text("SELECT 1 FROM cliente WHERE id=:id"), {"id": data.cliente_id}).first():
        raise HTTPException(400, "El cliente seleccionado no existe")
    if data.codigo and db.execute(text("SELECT 1 FROM proyecto WHERE codigo=:codigo"), {"codigo": data.codigo}).first():
        raise HTTPException(409, "Ese código de proyecto ya está en uso")
    try:
        project_id = db.execute(text("""INSERT INTO proyecto
            (codigo,nombre,descripcion,tipo,cliente_id,fecha_inicio,fecha_fin,creado_por)
            VALUES(:codigo,:nombre,:descripcion,:tipo,:cliente,:inicio,:fin,:user) RETURNING id"""),
            {"codigo": data.codigo, "nombre": data.nombre, "descripcion": data.descripcion,
             "tipo": data.tipo, "cliente": data.cliente_id, "inicio": data.fecha_inicio,
             "fin": data.fecha_fin, "user": user.id}).scalar_one()
        code = data.codigo or f"PRY-{project_id:04d}"
        if not data.codigo:
            suffix = 1
            while db.execute(text("SELECT 1 FROM proyecto WHERE codigo=:codigo AND id<>:id"),
                             {"codigo": code, "id": project_id}).first():
                code = f"PRY-{project_id:04d}-{suffix:02d}"
                suffix += 1
        db.execute(text("UPDATE proyecto SET codigo=:codigo WHERE id=:id"), {"codigo": code, "id": project_id})
        registrar(db, user, "proyectos", "proyecto", "crear", registro_id=project_id,
                  registro_codigo=code, datos_despues={"nombre": data.nombre, "tipo": data.tipo})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": project_id, "codigo": code, "estado": "ABIERTO", "msg": "Proyecto creado"}


@router.put("/{project_id}")
def actualizar_proyecto(project_id: int, data: ProyectoUpdate, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "editar"))):
    current = _project(db, project_id, lock=True)
    if data.fecha_inicio and data.fecha_fin and data.fecha_fin < data.fecha_inicio:
        raise HTTPException(400, "La fecha de cierre no puede ser anterior al inicio")
    if data.cliente_id and not db.execute(text("SELECT 1 FROM cliente WHERE id=:id"), {"id": data.cliente_id}).first():
        raise HTTPException(400, "El cliente seleccionado no existe")
    if current["estado"] != "ABIERTO" and data.estado == "ABIERTO":
        raise HTTPException(409, "Un proyecto completado o cancelado no se puede reabrir")
    code = data.codigo or current["codigo"]
    if db.execute(text("SELECT 1 FROM proyecto WHERE codigo=:codigo AND id<>:id"),
                  {"codigo": code, "id": project_id}).first():
        raise HTTPException(409, "Ese código de proyecto ya está en uso")
    try:
        db.execute(text("""UPDATE proyecto SET codigo=:codigo,nombre=:nombre,descripcion=:descripcion,
            tipo=:tipo,cliente_id=:cliente,fecha_inicio=:inicio,fecha_fin=:fin,estado=:estado,
            actualizado_en=now() WHERE id=:id"""),
            {"codigo": code, "nombre": data.nombre, "descripcion": data.descripcion,
             "tipo": data.tipo, "cliente": data.cliente_id, "inicio": data.fecha_inicio,
             "fin": data.fecha_fin, "estado": data.estado, "id": project_id})
        registrar(db, user, "proyectos", "proyecto", "editar", registro_id=project_id,
                  registro_codigo=code, datos_antes={"estado": current["estado"]},
                  datos_despues={"nombre": data.nombre, "estado": data.estado})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": project_id, "codigo": code, "estado": data.estado, "msg": "Proyecto actualizado"}


@router.get("/{project_id}/fuentes/{source_type}")
def fuentes_disponibles(project_id: int, source_type: Literal["FACTURA", "COMPRA", "PLANILLA"],
                        db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    _project(db, project_id)
    permission = {"FACTURA": "asignar_ingresos", "COMPRA": "asignar_compras", "PLANILLA": "asignar_planilla"}[source_type]
    require_permission("proyectos", permission)(user=user, db=db)
    if source_type == "FACTURA":
        query = text("""SELECT d.id fuente_detalle_id, f.id documento_id, f.numero documento,
            f.fecha, c.nombre tercero, d.descripcion,
            ROUND(d.cantidad*d.precio_unitario,2) monto_total
            FROM factura_detalle d JOIN factura f ON f.id=d.factura_id
            JOIN asiento a ON a.id=f.asiento_id AND a.estado='VIGENTE'
            JOIN cliente c ON c.id=f.cliente_id
            WHERE f.tipo_dte IN ('CCF','FCON') ORDER BY f.fecha DESC,f.id DESC,d.id""")
    elif source_type == "COMPRA":
        query = text("""SELECT d.id fuente_detalle_id, c.id documento_id, c.numero documento,
            c.fecha, p.nombre tercero, d.descripcion, ROUND(d.cantidad*d.precio_unitario,2) monto_total
            FROM compra_detalle d JOIN compra c ON c.id=d.compra_id
            JOIN asiento a ON a.id=c.asiento_id AND a.estado='VIGENTE'
            JOIN proveedor p ON p.id=c.proveedor_id WHERE c.tipo_doc <> 'NCR'
            ORDER BY c.fecha DESC,c.id DESC,d.id""")
    else:
        query = text("""SELECT d.id fuente_detalle_id, p.id documento_id, p.codigo documento,
            p.fecha_pago fecha, e.nombres || ' ' || e.apellidos tercero,
            'Salario y aportes patronales: ' || e.cargo descripcion,
            ROUND(d.salario_base*d.dias_trabajados/30+d.horas_extra+d.bonificaciones+d.comisiones,2)
              + d.isss_patronal+d.afp_patronal monto_total
            FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id
            JOIN asiento a ON a.id=p.asiento_id AND a.estado='VIGENTE'
            JOIN empleado e ON e.id=d.empleado_id ORDER BY p.fecha_pago DESC,p.id DESC,d.id""")
    rows = db.execute(query).mappings().all()
    available = []
    for row in rows:
        allocated = _allocated_total(db, source_type, row["fuente_detalle_id"])
        remaining = _money(row["monto_total"]) - allocated
        if remaining > 0:
            available.append({**dict(row), "monto_total": _money(row["monto_total"]), "monto_disponible": remaining})
    return {"fuentes": available}


@router.get("/{project_id}/asignaciones/{source_type}")
def listar_asignaciones(project_id: int, source_type: Literal["FACTURA", "COMPRA", "PLANILLA"],
                         db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    _project(db, project_id)
    permission = {"FACTURA": "asignar_ingresos", "COMPRA": "asignar_compras", "PLANILLA": "asignar_planilla"}[source_type]
    require_permission("proyectos", permission)(user=user, db=db)
    query = text(f"""SELECT a.id,a.fuente_tipo,a.fuente_detalle_id,a.categoria,a.monto,a.creado_en,
        {_source_is_current('a')} AS fuente_vigente,
        CASE a.fuente_tipo
          WHEN 'FACTURA' THEN (SELECT f.numero FROM factura_detalle d JOIN factura f ON f.id=d.factura_id WHERE d.id=a.fuente_detalle_id)
          WHEN 'COMPRA' THEN (SELECT c.numero FROM compra_detalle d JOIN compra c ON c.id=d.compra_id WHERE d.id=a.fuente_detalle_id)
          ELSE (SELECT p.codigo FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id WHERE d.id=a.fuente_detalle_id)
        END documento,
        CASE a.fuente_tipo
          WHEN 'FACTURA' THEN (SELECT d.descripcion FROM factura_detalle d WHERE d.id=a.fuente_detalle_id)
          WHEN 'COMPRA' THEN (SELECT d.descripcion FROM compra_detalle d WHERE d.id=a.fuente_detalle_id)
          ELSE (SELECT 'Nómina: ' || e.nombres || ' ' || e.apellidos FROM planilla_detalle d JOIN empleado e ON e.id=d.empleado_id WHERE d.id=a.fuente_detalle_id)
        END descripcion
        FROM proyecto_asignacion a WHERE a.proyecto_id=:project AND a.fuente_tipo=:source
        ORDER BY a.creado_en DESC,a.id DESC""")
    rows = db.execute(query, {"project": project_id, "source": source_type}).mappings().all()
    return {"asignaciones": [dict(row) for row in rows]}


@router.post("/{project_id}/asignaciones")
def asignar_fuente(project_id: int, data: AsignacionIn, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    expected = {"FACTURA": ("INGRESO", "asignar_ingresos"),
                "COMPRA": (("COSTO_DIRECTO", "COSTO_INDIRECTO"), "asignar_compras"),
                "PLANILLA": ("MANO_OBRA", "asignar_planilla")}
    allowed_category, specific_permission = expected[data.fuente_tipo]
    if data.categoria not in ((allowed_category,) if isinstance(allowed_category, str) else allowed_category):
        raise HTTPException(400, "La clasificación no corresponde al tipo de operación")
    # A second permission check keeps the generic project-view permission from authorizing financial assignment.
    require_permission("proyectos", specific_permission)(user=user, db=db)
    project = _project(db, project_id, lock=True)
    if project["estado"] != "ABIERTO":
        raise HTTPException(409, "Solo se asignan movimientos a proyectos abiertos")
    source = _source(db, data.fuente_tipo, data.fuente_detalle_id, lock=True)
    if not source:
        raise HTTPException(404, "La línea no existe o su asiento aún no está vigente")
    available = _money(source["monto_total"]) - _allocated_total(db, data.fuente_tipo, data.fuente_detalle_id)
    amount = _money(data.monto)
    if amount > available:
        raise HTTPException(409, f"El importe excede lo disponible para asignar: ${available}")
    try:
        assignment_id = db.execute(text("""INSERT INTO proyecto_asignacion
            (proyecto_id,fuente_tipo,fuente_detalle_id,categoria,monto,creado_por)
            VALUES(:proyecto,:tipo,:fuente,:categoria,:monto,:user)
            ON CONFLICT (proyecto_id,fuente_tipo,fuente_detalle_id,categoria)
            DO UPDATE SET monto=proyecto_asignacion.monto+EXCLUDED.monto,
                          creado_por=EXCLUDED.creado_por,creado_en=now()
            RETURNING id"""),
            {"proyecto": project_id, "tipo": data.fuente_tipo,
             "fuente": data.fuente_detalle_id, "categoria": data.categoria,
             "monto": amount, "user": user.id}).scalar_one()
        registrar(db, user, "proyectos", "asignacion", "asignar", registro_id=assignment_id,
                  registro_codigo=project["codigo"], descripcion=f"{data.fuente_tipo} {source['documento']}: {source['descripcion']}",
                  datos_despues={"categoria": data.categoria, "monto": str(amount), "fuente": data.fuente_tipo})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": assignment_id, "msg": "Importe asignado al proyecto", "monto_disponible": str(available - amount)}


@router.delete("/{project_id}/asignaciones/{assignment_id}", status_code=204)
def quitar_asignacion(project_id: int, assignment_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    project = _project(db, project_id, lock=True)
    row = db.execute(text("""SELECT id,fuente_tipo,fuente_detalle_id,categoria,monto
        FROM proyecto_asignacion WHERE id=:id AND proyecto_id=:project FOR UPDATE"""),
        {"id": assignment_id, "project": project_id}).mappings().first()
    if not row:
        raise HTTPException(404, "No se encontró la asignación")
    permission = {"FACTURA": "asignar_ingresos", "COMPRA": "asignar_compras", "PLANILLA": "asignar_planilla"}[row["fuente_tipo"]]
    require_permission("proyectos", permission)(user=user, db=db)
    try:
        db.execute(text("DELETE FROM proyecto_asignacion WHERE id=:id"), {"id": assignment_id})
        registrar(db, user, "proyectos", "asignacion", "quitar", registro_id=assignment_id,
                  registro_codigo=project["codigo"], datos_antes={"fuente": row["fuente_tipo"], "categoria": row["categoria"], "monto": str(row["monto"])})
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.get("/{project_id}/rentabilidad")
def rentabilidad(project_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "rentabilidad"))):
    project = _project(db, project_id)
    totals = db.execute(text(f"""SELECT
        COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='INGRESO'),0) ingresos,
        COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='COSTO_DIRECTO'),0) costos_directos,
        COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='MANO_OBRA'),0) mano_obra,
        COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='COSTO_INDIRECTO'),0) costos_indirectos
        FROM proyecto_asignacion pa WHERE pa.proyecto_id=:id
          AND {_source_is_current('pa')}"""), {"id": project_id}).mappings().one()
    ingresos = _money(totals["ingresos"])
    directos = _money(totals["costos_directos"])
    labor = _money(totals["mano_obra"])
    indirectos = _money(totals["costos_indirectos"])
    costos = directos + labor + indirectos
    margin = ingresos - costos
    percent = _money(margin / ingresos * 100) if ingresos else Decimal("0.00")
    details = db.execute(text(f"""SELECT a.id,a.fuente_tipo,a.fuente_detalle_id,a.categoria,a.monto,a.creado_en,
        {_source_is_current('a')} AS fuente_vigente,
        CASE a.fuente_tipo
          WHEN 'FACTURA' THEN (SELECT f.numero FROM factura_detalle d JOIN factura f ON f.id=d.factura_id WHERE d.id=a.fuente_detalle_id)
          WHEN 'COMPRA' THEN (SELECT c.numero FROM compra_detalle d JOIN compra c ON c.id=d.compra_id WHERE d.id=a.fuente_detalle_id)
          ELSE (SELECT p.codigo FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id WHERE d.id=a.fuente_detalle_id)
        END documento,
        CASE a.fuente_tipo
          WHEN 'FACTURA' THEN (SELECT d.descripcion FROM factura_detalle d WHERE d.id=a.fuente_detalle_id)
          WHEN 'COMPRA' THEN (SELECT d.descripcion FROM compra_detalle d WHERE d.id=a.fuente_detalle_id)
          ELSE (SELECT 'Nómina: ' || e.nombres || ' ' || e.apellidos FROM planilla_detalle d JOIN empleado e ON e.id=d.empleado_id WHERE d.id=a.fuente_detalle_id)
        END descripcion
        FROM proyecto_asignacion a WHERE a.proyecto_id=:id ORDER BY a.creado_en DESC,a.id DESC"""), {"id": project_id}).mappings().all()
    return {"proyecto": dict(project), "ingresos": ingresos, "costos_directos": directos,
            "mano_obra": labor, "costos_indirectos": indirectos, "costos_totales": costos,
            "margen": margin, "margen_porcentaje": percent,
            "asignaciones": [dict(row) for row in details]}

