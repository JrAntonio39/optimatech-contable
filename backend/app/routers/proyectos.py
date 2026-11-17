"""Proyectos y análisis de rentabilidad a partir de operaciones contabilizadas."""

from datetime import date, timedelta
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
        JOIN asiento asiento_fuente ON asiento_fuente.id=f.asiento_id
        WHERE fd.id=pa.fuente_detalle_id AND asiento_fuente.estado='VIGENTE'
          AND f.tipo_dte IN ('CCF','FCON')
    )) OR
    (pa.fuente_tipo='COMPRA' AND EXISTS (
        SELECT 1 FROM compra_detalle cd JOIN compra c ON c.id=cd.compra_id
        JOIN asiento asiento_fuente ON asiento_fuente.id=c.asiento_id
        WHERE cd.id=pa.fuente_detalle_id AND asiento_fuente.estado='VIGENTE'
          AND c.tipo_doc <> 'NCR'
    )) OR
    (pa.fuente_tipo='PLANILLA' AND EXISTS (
        SELECT 1 FROM planilla_detalle pd JOIN planilla p ON p.id=pd.planilla_id
        JOIN asiento asiento_fuente ON asiento_fuente.id=p.asiento_id
        WHERE pd.id=pa.fuente_detalle_id AND asiento_fuente.estado='VIGENTE'
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
    ingreso_estimado: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)
    costo_directo_estimado: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)
    mano_obra_estimada: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)
    costo_indirecto_estimado: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)

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
    ingreso_estimado: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)
    costo_directo_estimado: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)
    mano_obra_estimada: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)
    costo_indirecto_estimado: Optional[Decimal] = Field(None, ge=0, max_digits=14, decimal_places=2)

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
    categoria: Literal["INGRESO", "COSTO_DIRECTO", "MANO_OBRA", "COSTO_INDIRECTO", "HORAS_EXTRA"]
    monto: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)
    dias_asignados: Optional[Decimal] = Field(None, gt=0, max_digits=8, decimal_places=2)


class HoraProyectoIn(BaseModel):
    empleado_id: int = Field(..., gt=0)
    fecha: date
    actividad: str = Field(..., min_length=3, max_length=240)
    horas: Decimal = Field(..., gt=0, le=8, max_digits=6, decimal_places=2)

    @field_validator("actividad", mode="before")
    @classmethod
    def limpiar_actividad(cls, value):
        return " ".join(str(value or "").split())


class HorasProyectoLoteIn(BaseModel):
    empleado_id: int = Field(..., gt=0)
    fecha_inicio: date
    fecha_fin: date
    dias_semana: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5])
    actividad: str = Field(..., min_length=3, max_length=240)
    horas_por_dia: Decimal = Field(..., gt=0, le=8, max_digits=6, decimal_places=2)

    @field_validator("actividad", mode="before")
    @classmethod
    def limpiar_actividad(cls, value):
        return " ".join(str(value or "").split())


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
        "PLANILLA": f"""SELECT d.id fuente_detalle_id, p.codigo documento, p.fecha_pago fecha,p.periodo,
            e.nombres || ' ' || e.apellidos tercero,
            'Salario y aportes patronales: ' || e.cargo descripcion,
            ROUND(d.salario_base*d.dias_trabajados/30 + d.bonificaciones + d.comisiones,2)
              + d.isss_patronal + d.afp_patronal AS monto_total,
            COALESCE(d.horas_extra,0) AS monto_horas_extra, d.dias_trabajados
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


def _allocated_category_total(db: Session, detail_id: int, category: str) -> Decimal:
    value = db.execute(text(f"""SELECT COALESCE(SUM(pa.monto),0)
        FROM proyecto_asignacion pa WHERE pa.fuente_tipo='PLANILLA'
          AND pa.fuente_detalle_id=:id AND pa.categoria=:category
          AND {_source_is_current('pa')}"""),
        {"id": detail_id, "category": category}).scalar_one()
    return _money(value)


def _allocated_days(db: Session, detail_id: int) -> Decimal:
    value = db.execute(text("""SELECT COALESCE(SUM(pa.dias_asignados),0)
        FROM proyecto_asignacion pa
        WHERE pa.fuente_tipo='PLANILLA' AND pa.fuente_detalle_id=:id
          AND """ + _source_is_current("pa")), {"id": detail_id}).scalar_one()
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def _hourly_labor_totals(db: Session) -> dict[int, Decimal]:
    rows = db.execute(text("""WITH hours_by_project AS (
            SELECT proyecto_id,empleado_id,to_char(fecha,'YYYY-MM') periodo,SUM(horas) horas
            FROM proyecto_horas GROUP BY proyecto_id,empleado_id,to_char(fecha,'YYYY-MM')
        ), payroll_cost AS (
            SELECT d.empleado_id,p.periodo,
              SUM(ROUND(d.salario_base*d.dias_trabajados/30+d.bonificaciones+d.comisiones,2)
                  +d.isss_patronal+d.afp_patronal) costo,
              SUM(d.dias_trabajados*8) horas_pagadas
            FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id
            JOIN asiento a ON a.id=p.asiento_id AND a.estado='VIGENTE'
            GROUP BY d.empleado_id,p.periodo
        )
        SELECT h.proyecto_id,
          SUM(ROUND(pc.costo*h.horas/NULLIF(pc.horas_pagadas,0),2)) costo
        FROM hours_by_project h JOIN payroll_cost pc
          ON pc.empleado_id=h.empleado_id AND pc.periodo=h.periodo
        GROUP BY h.proyecto_id""")).mappings().all()
    return {row["proyecto_id"]: _money(row["costo"]) for row in rows}


def _manual_payroll_cost(db: Session, project_id: int) -> Decimal:
    value = db.execute(text(f"""SELECT COALESCE(SUM(pa.monto),0)
        FROM proyecto_asignacion pa
        JOIN planilla_detalle pd ON pd.id=pa.fuente_detalle_id
        JOIN planilla p ON p.id=pd.planilla_id
        WHERE pa.proyecto_id=:id AND pa.fuente_tipo='PLANILLA' AND pa.categoria IN ('MANO_OBRA','HORAS_EXTRA')
          AND {_source_is_current('pa')}
          AND (pa.categoria='HORAS_EXTRA' OR NOT EXISTS (SELECT 1 FROM proyecto_horas ph
              WHERE ph.empleado_id=pd.empleado_id AND to_char(ph.fecha,'YYYY-MM')=p.periodo))"""),
        {"id": project_id}).scalar_one()
    return _money(value)


@router.get("")
def listar_proyectos(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    puede_ver_presupuesto = (
        "admin" in user.rol_codigos
        or "proyectos.editar" in user.permiso_codigos
        or "proyectos.rentabilidad" in user.permiso_codigos
    )
    presupuesto = (
        "p.ingreso_estimado,p.costo_directo_estimado,p.mano_obra_estimada,p.costo_indirecto_estimado"
        if puede_ver_presupuesto else
        "NULL::numeric ingreso_estimado,NULL::numeric costo_directo_estimado,"
        "NULL::numeric mano_obra_estimada,NULL::numeric costo_indirecto_estimado"
    )
    rows = db.execute(text("""SELECT p.id,p.codigo,p.nombre,p.descripcion,p.tipo,p.cliente_id,
        c.nombre cliente,p.fecha_inicio,p.fecha_fin,p.estado,p.creado_en,p.actualizado_en,
        """ + presupuesto + """
        FROM proyecto p LEFT JOIN cliente c ON c.id=p.cliente_id
        ORDER BY CASE p.estado WHEN 'ABIERTO' THEN 0 ELSE 1 END,p.nombre""")).mappings().all()
    return {"proyectos": [dict(row) for row in rows]}


@router.get("/empleados-activos")
def empleados_activos_proyecto(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "asignar_planilla"))):
    rows = db.execute(text("""SELECT id,codigo,nombres,apellidos,cargo FROM empleado
        WHERE estado='ACTIVO' ORDER BY apellidos,nombres""")).mappings().all()
    return {"empleados": [dict(row) for row in rows]}


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
            (codigo,nombre,descripcion,tipo,cliente_id,fecha_inicio,fecha_fin,creado_por,
             ingreso_estimado,costo_directo_estimado,mano_obra_estimada,costo_indirecto_estimado)
            VALUES(:codigo,:nombre,:descripcion,:tipo,:cliente,:inicio,:fin,:user,
             :ingreso,:directo,:mano_obra,:indirecto) RETURNING id"""),
            {"codigo": data.codigo, "nombre": data.nombre, "descripcion": data.descripcion,
             "tipo": data.tipo, "cliente": data.cliente_id, "inicio": data.fecha_inicio,
             "fin": data.fecha_fin, "user": user.id, "ingreso": data.ingreso_estimado,
             "directo": data.costo_directo_estimado, "mano_obra": data.mano_obra_estimada,
             "indirecto": data.costo_indirecto_estimado}).scalar_one()
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
    fields_sent = data.model_fields_set
    ingreso_estimado = data.ingreso_estimado if "ingreso_estimado" in fields_sent else current["ingreso_estimado"]
    costo_directo_estimado = data.costo_directo_estimado if "costo_directo_estimado" in fields_sent else current["costo_directo_estimado"]
    mano_obra_estimada = data.mano_obra_estimada if "mano_obra_estimada" in fields_sent else current["mano_obra_estimada"]
    costo_indirecto_estimado = data.costo_indirecto_estimado if "costo_indirecto_estimado" in fields_sent else current["costo_indirecto_estimado"]
    if db.execute(text("SELECT 1 FROM proyecto WHERE codigo=:codigo AND id<>:id"),
                  {"codigo": code, "id": project_id}).first():
        raise HTTPException(409, "Ese código de proyecto ya está en uso")
    try:
        db.execute(text("""UPDATE proyecto SET codigo=:codigo,nombre=:nombre,descripcion=:descripcion,
            tipo=:tipo,cliente_id=:cliente,fecha_inicio=:inicio,fecha_fin=:fin,estado=:estado,
            ingreso_estimado=:ingreso,costo_directo_estimado=:directo,
            mano_obra_estimada=:mano_obra,costo_indirecto_estimado=:indirecto,
            actualizado_en=now() WHERE id=:id"""),
            {"codigo": code, "nombre": data.nombre, "descripcion": data.descripcion,
             "tipo": data.tipo, "cliente": data.cliente_id, "inicio": data.fecha_inicio,
             "fin": data.fecha_fin, "estado": data.estado, "id": project_id,
             "ingreso": ingreso_estimado, "directo": costo_directo_estimado,
             "mano_obra": mano_obra_estimada, "indirecto": costo_indirecto_estimado})
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
    project = _project(db, project_id)
    permission = {"FACTURA": "asignar_ingresos", "COMPRA": "asignar_compras", "PLANILLA": "asignar_planilla"}[source_type]
    require_permission("proyectos", permission)(user=user, db=db)
    if source_type == "FACTURA":
        if not project["cliente_id"]:
            return {"fuentes": []}
        query = text("""SELECT d.id fuente_detalle_id, f.id documento_id, f.numero documento,
            f.fecha, c.nombre tercero, d.descripcion,
            ROUND(d.cantidad*d.precio_unitario,2) monto_total
            FROM factura_detalle d JOIN factura f ON f.id=d.factura_id
            JOIN asiento a ON a.id=f.asiento_id AND a.estado='VIGENTE'
            JOIN cliente c ON c.id=f.cliente_id
            WHERE f.tipo_dte IN ('CCF','FCON') AND f.cliente_id=:cliente_id
            ORDER BY f.fecha DESC,f.id DESC,d.id""")
        query_params = {"cliente_id": project["cliente_id"]}
    elif source_type == "COMPRA":
        query = text("""SELECT d.id fuente_detalle_id, c.id documento_id, c.numero documento,
            c.fecha, p.nombre tercero, d.descripcion, ROUND(d.cantidad*d.precio_unitario,2) monto_total
            FROM compra_detalle d JOIN compra c ON c.id=d.compra_id
            JOIN asiento a ON a.id=c.asiento_id AND a.estado='VIGENTE'
            JOIN proveedor p ON p.id=c.proveedor_id WHERE c.tipo_doc <> 'NCR'
            ORDER BY c.fecha DESC,c.id DESC,d.id""")
        query_params = {}
    else:
        query = text(f"""WITH asignado AS (
            SELECT pa.fuente_detalle_id,
              COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='MANO_OBRA'),0) monto_regular_asignado,
              COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='HORAS_EXTRA'),0) monto_extra_asignado,
              COALESCE(SUM(pa.dias_asignados) FILTER (WHERE pa.categoria='MANO_OBRA'),0) dias_asignados
            FROM proyecto_asignacion pa
            WHERE pa.fuente_tipo='PLANILLA' AND {ASIGNACION_FUENTE_VIGENTE_SQL}
            GROUP BY pa.fuente_detalle_id
        )
        SELECT d.id fuente_detalle_id, p.id documento_id, p.codigo documento,
            p.fecha_pago fecha, e.nombres || ' ' || e.apellidos tercero,
            'Salario y aportes patronales: ' || e.cargo descripcion,
            ROUND(d.salario_base*d.dias_trabajados/30+d.bonificaciones+d.comisiones,2)
              + d.isss_patronal+d.afp_patronal monto_total,
            COALESCE(d.horas_extra,0) monto_horas_extra, d.dias_trabajados,
            COALESCE(asignado.monto_regular_asignado,0) monto_regular_asignado,
            COALESCE(asignado.monto_extra_asignado,0) monto_extra_asignado,
            COALESCE(asignado.dias_asignados,0) dias_asignados,
            EXISTS (SELECT 1 FROM proyecto_horas ph
              WHERE ph.empleado_id=d.empleado_id AND to_char(ph.fecha,'YYYY-MM')=p.periodo) horas_registradas
            FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id
            JOIN asiento a ON a.id=p.asiento_id AND a.estado='VIGENTE'
            JOIN empleado e ON e.id=d.empleado_id
            LEFT JOIN asignado ON asignado.fuente_detalle_id=d.id
            WHERE (:fecha_inicio IS NULL OR p.periodo >= to_char(date_trunc('month', CAST(:fecha_inicio AS date)), 'YYYY-MM'))
              AND (:fecha_fin IS NULL OR p.periodo <= to_char(date_trunc('month', CAST(:fecha_fin AS date)), 'YYYY-MM'))
            ORDER BY p.fecha_pago DESC,p.id DESC,d.id""")
        query_params = {"fecha_inicio": project["fecha_inicio"], "fecha_fin": project["fecha_fin"]}
    rows = db.execute(query, query_params).mappings().all()
    available = []
    for row in rows:
        source = dict(row)
        if source_type == "PLANILLA":
            regular_remaining = _money(row["monto_total"]) - _money(row["monto_regular_asignado"])
            extra_remaining = _money(row["monto_horas_extra"]) - _money(row["monto_extra_asignado"])
            if row["horas_registradas"]:
                regular_remaining = Decimal("0.00")
            days_remaining = Decimal(row["dias_trabajados"]) - Decimal(str(row["dias_asignados"]))
            source["monto_total"] = _money(row["monto_total"])
            source["monto_disponible"] = max(regular_remaining, Decimal("0.00"))
            source["monto_horas_extra"] = _money(row["monto_horas_extra"])
            source["monto_extra_disponible"] = max(extra_remaining, Decimal("0.00"))
            source["dias_disponibles"] = max(days_remaining, Decimal("0.00"))
            if source["monto_disponible"] <= 0 and source["monto_extra_disponible"] <= 0:
                continue
        else:
            remaining = _money(row["monto_total"]) - _allocated_total(db, source_type, row["fuente_detalle_id"])
            if remaining <= 0:
                continue
            source["monto_total"] = _money(row["monto_total"])
            source["monto_disponible"] = remaining
        available.append(source)
    return {"fuentes": available}


@router.get("/{project_id}/asignaciones/{source_type}")
def listar_asignaciones(project_id: int, source_type: Literal["FACTURA", "COMPRA", "PLANILLA"],
                         db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    _project(db, project_id)
    permission = {"FACTURA": "asignar_ingresos", "COMPRA": "asignar_compras", "PLANILLA": "asignar_planilla"}[source_type]
    require_permission("proyectos", permission)(user=user, db=db)
    query = text(f"""SELECT a.id,a.fuente_tipo,a.fuente_detalle_id,a.categoria,a.monto,a.dias_asignados,a.creado_en,
        {_source_is_current('a')} AS fuente_vigente,
        CASE WHEN a.fuente_tipo='PLANILLA' AND a.categoria='MANO_OBRA' THEN EXISTS (
          SELECT 1 FROM planilla_detalle pd JOIN planilla p ON p.id=pd.planilla_id
          JOIN proyecto_horas ph ON ph.empleado_id=pd.empleado_id AND to_char(ph.fecha,'YYYY-MM')=p.periodo
          WHERE pd.id=a.fuente_detalle_id
        ) ELSE FALSE END AS sustituido_por_horas,
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
                "PLANILLA": (("MANO_OBRA", "HORAS_EXTRA"), "asignar_planilla")}
    allowed_category, specific_permission = expected[data.fuente_tipo]
    if data.categoria not in ((allowed_category,) if isinstance(allowed_category, str) else allowed_category):
        raise HTTPException(400, "La clasificación no corresponde al tipo de operación")
    if data.fuente_tipo == "PLANILLA" and data.categoria == "MANO_OBRA" and data.dias_asignados is None:
        raise HTTPException(400, "Indica cuántos días trabajados corresponden a este proyecto")
    if data.fuente_tipo == "PLANILLA" and data.categoria == "HORAS_EXTRA" and data.dias_asignados is not None:
        raise HTTPException(400, "Las horas extra se asignan por importe, no por días")
    if data.fuente_tipo != "PLANILLA" and data.dias_asignados is not None:
        raise HTTPException(400, "Los días asignados solo aplican a planillas")
    # A second permission check keeps the generic project-view permission from authorizing financial assignment.
    require_permission("proyectos", specific_permission)(user=user, db=db)
    project = _project(db, project_id, lock=True)
    if project["estado"] != "ABIERTO":
        raise HTTPException(409, "Solo se asignan movimientos a proyectos abiertos")
    source = _source(db, data.fuente_tipo, data.fuente_detalle_id, lock=True)
    if not source:
        raise HTTPException(404, "La línea no existe o su asiento aún no está vigente")
    if data.fuente_tipo == "PLANILLA":
        source_period = source["periodo"]
        start_period = project["fecha_inicio"].strftime("%Y-%m") if project["fecha_inicio"] else None
        end_period = project["fecha_fin"].strftime("%Y-%m") if project["fecha_fin"] else None
        if ((start_period and source_period < start_period)
                or (end_period and source_period > end_period)):
            raise HTTPException(400, "La planilla debe corresponder al período de ejecución del proyecto")
    if data.fuente_tipo == "PLANILLA" and data.categoria == "MANO_OBRA" and db.execute(text("""SELECT EXISTS (
        SELECT 1 FROM planilla_detalle pd JOIN planilla p ON p.id=pd.planilla_id
        JOIN proyecto_horas ph ON ph.empleado_id=pd.empleado_id AND to_char(ph.fecha,'YYYY-MM')=p.periodo
        WHERE pd.id=:id)"""), {"id": data.fuente_detalle_id}).scalar_one():
        raise HTTPException(409, "Este empleado ya tiene horas registradas en el período; asigna la mano de obra desde la bitácora")
    if data.fuente_tipo == "PLANILLA":
        source_amount = _money(source["monto_horas_extra"] if data.categoria == "HORAS_EXTRA" else source["monto_total"])
        available = source_amount - _allocated_category_total(db, data.fuente_detalle_id, data.categoria)
    else:
        available = _money(source["monto_total"]) - _allocated_total(db, data.fuente_tipo, data.fuente_detalle_id)
    amount = _money(data.monto)
    if data.fuente_tipo == "FACTURA" and project["cliente_id"]:
        invoice_client_id = db.execute(text("SELECT f.cliente_id FROM factura_detalle d JOIN factura f ON f.id=d.factura_id WHERE d.id=:id"), {"id": data.fuente_detalle_id}).scalar_one()
        if invoice_client_id != project["cliente_id"]:
            raise HTTPException(400, "La factura debe pertenecer al cliente asignado al proyecto")
    if data.fuente_tipo == "FACTURA" and not project["cliente_id"]:
        raise HTTPException(400, "Asigna un cliente al proyecto antes de vincular facturas")
    days = None
    if data.fuente_tipo == "PLANILLA" and data.categoria == "MANO_OBRA":
        days = data.dias_asignados.quantize(Decimal("0.01"))
        days_available = Decimal(source["dias_trabajados"]) - _allocated_days(db, data.fuente_detalle_id)
        if days > days_available:
            raise HTTPException(409, f"Los días exceden el saldo disponible: {days_available}")
        expected_amount = available if days == days_available else _money(Decimal(str(source["monto_total"])) * days / Decimal(source["dias_trabajados"]))
        if amount != expected_amount:
            raise HTTPException(400, f"El importe de esos días debe ser ${expected_amount}")
    if amount > available:
        raise HTTPException(409, f"El importe excede lo disponible para asignar: ${available}")
    try:
        assignment_id = db.execute(text("""INSERT INTO proyecto_asignacion
            (proyecto_id,fuente_tipo,fuente_detalle_id,categoria,monto,dias_asignados,creado_por)
            VALUES(:proyecto,:tipo,:fuente,:categoria,:monto,:dias,:user)
            ON CONFLICT (proyecto_id,fuente_tipo,fuente_detalle_id,categoria)
            DO UPDATE SET monto=proyecto_asignacion.monto+EXCLUDED.monto,
                          dias_asignados=COALESCE(proyecto_asignacion.dias_asignados,0)+COALESCE(EXCLUDED.dias_asignados,0),
                          creado_por=EXCLUDED.creado_por,creado_en=now()
            RETURNING id"""),
            {"proyecto": project_id, "tipo": data.fuente_tipo,
             "fuente": data.fuente_detalle_id, "categoria": data.categoria,
             "monto": amount, "dias": days, "user": user.id}).scalar_one()
        registrar(db, user, "proyectos", "asignacion", "asignar", registro_id=assignment_id,
                  registro_codigo=project["codigo"], descripcion=f"{data.fuente_tipo} {source['documento']}: {source['descripcion']}",
                  datos_despues={"categoria": data.categoria, "monto": str(amount), "dias_asignados": str(days) if days is not None else None, "fuente": data.fuente_tipo})
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


@router.get("/{project_id}/horas")
def listar_horas_proyecto(project_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "ver"))):
    _project(db, project_id)
    puede_ver_costos = "admin" in user.rol_codigos or "proyectos.rentabilidad" in user.permiso_codigos
    rows = db.execute(text("""WITH payroll_cost AS (
            SELECT d.empleado_id,p.periodo,
              SUM(ROUND(d.salario_base*d.dias_trabajados/30+d.horas_extra+d.bonificaciones+d.comisiones,2)
                  +d.isss_patronal+d.afp_patronal) costo,
              SUM(d.dias_trabajados*8) horas_pagadas
            FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id
            JOIN asiento a ON a.id=p.asiento_id AND a.estado='VIGENTE'
            GROUP BY d.empleado_id,p.periodo
        )
        SELECT h.id,h.empleado_id,e.codigo empleado_codigo,
          e.nombres || ' ' || e.apellidos empleado,h.fecha,h.actividad,h.horas,h.creado_en,
          CASE WHEN :puede_ver THEN ROUND(pc.costo*h.horas/NULLIF(pc.horas_pagadas,0),2) END costo_calculado,
          (pc.empleado_id IS NOT NULL) costo_disponible
        FROM proyecto_horas h JOIN empleado e ON e.id=h.empleado_id
        LEFT JOIN payroll_cost pc ON pc.empleado_id=h.empleado_id AND pc.periodo=to_char(h.fecha,'YYYY-MM')
        WHERE h.proyecto_id=:project ORDER BY h.fecha DESC,h.id DESC"""),
        {"project": project_id, "puede_ver": puede_ver_costos}).mappings().all()
    return {"horas": [dict(row) for row in rows]}


@router.post("/{project_id}/horas", status_code=201)
def registrar_horas_proyecto(project_id: int, data: HoraProyectoIn, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "asignar_planilla"))):
    project = _project(db, project_id, lock=True)
    if project["estado"] != "ABIERTO":
        raise HTTPException(409, "Solo se registran horas en proyectos abiertos")
    if project["fecha_inicio"] and data.fecha < project["fecha_inicio"]:
        raise HTTPException(400, "La fecha de trabajo es anterior al inicio del proyecto")
    if project["fecha_fin"] and data.fecha > project["fecha_fin"]:
        raise HTTPException(400, "La fecha de trabajo es posterior al cierre del proyecto")
    employee = db.execute(text("SELECT id,codigo FROM empleado WHERE id=:id AND estado='ACTIVO' FOR UPDATE"), {"id": data.empleado_id}).mappings().first()
    if not employee:
        raise HTTPException(404, "El empleado no existe o está inactivo")
    day_hours = db.execute(text("SELECT COALESCE(SUM(horas),0) FROM proyecto_horas WHERE empleado_id=:employee AND fecha=:day"),
        {"employee": data.empleado_id, "day": data.fecha}).scalar_one()
    if Decimal(str(day_hours)) + data.horas > Decimal("8"):
        raise HTTPException(409, "Las horas registradas para una persona no pueden superar 8 en un día")
    payroll_capacity = db.execute(text("""SELECT SUM(d.dias_trabajados*8)
        FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id
        JOIN asiento a ON a.id=p.asiento_id AND a.estado='VIGENTE'
        WHERE d.empleado_id=:employee AND p.periodo=:period"""),
        {"employee": data.empleado_id, "period": data.fecha.strftime("%Y-%m")}).scalar_one()
    if payroll_capacity is not None:
        month_hours = db.execute(text("""SELECT COALESCE(SUM(horas),0) FROM proyecto_horas
            WHERE empleado_id=:employee AND to_char(fecha,'YYYY-MM')=:period"""),
            {"employee": data.empleado_id, "period": data.fecha.strftime("%Y-%m")}).scalar_one()
        if Decimal(str(month_hours)) + data.horas > Decimal(str(payroll_capacity)):
            raise HTTPException(409, f"Las horas exceden las {payroll_capacity} horas pagadas disponibles en ese período")
    try:
        entry_id = db.execute(text("""INSERT INTO proyecto_horas
            (proyecto_id,empleado_id,fecha,actividad,horas,creado_por)
            VALUES(:project,:employee,:date,:activity,:hours,:user) RETURNING id"""),
            {"project": project_id, "employee": data.empleado_id, "date": data.fecha,
             "activity": data.actividad, "hours": data.horas, "user": user.id}).scalar_one()
        registrar(db, user, "proyectos", "horas", "registrar", registro_id=entry_id,
            registro_codigo=project["codigo"], descripcion=f"{employee['codigo']} · {data.actividad}",
            datos_despues={"fecha": data.fecha.isoformat(), "horas": str(data.horas), "empleado_id": data.empleado_id})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": entry_id, "msg": "Horas registradas"}


@router.post("/{project_id}/horas/lote", status_code=201)
def registrar_horas_proyecto_lote(project_id: int, data: HorasProyectoLoteIn, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "asignar_planilla"))):
    project = _project(db, project_id, lock=True)
    if project["estado"] != "ABIERTO":
        raise HTTPException(409, "Solo se registran horas en proyectos abiertos")
    if data.fecha_fin < data.fecha_inicio:
        raise HTTPException(400, "La fecha final debe ser igual o posterior a la fecha inicial")
    if (data.fecha_fin - data.fecha_inicio).days > 62:
        raise HTTPException(400, "Registra un período máximo de 63 días por operación")
    if not data.dias_semana or len(set(data.dias_semana)) != len(data.dias_semana) or any(day < 1 or day > 7 for day in data.dias_semana):
        raise HTTPException(400, "Selecciona uno o más días válidos de la semana")
    employee = db.execute(text("SELECT id,codigo FROM empleado WHERE id=:id AND estado='ACTIVO' FOR UPDATE"),
        {"id": data.empleado_id}).mappings().first()
    if not employee:
        raise HTTPException(404, "El empleado no existe o está inactivo")

    selected_weekdays = set(data.dias_semana)
    dates = []
    current = data.fecha_inicio
    while current <= data.fecha_fin:
        if current.isoweekday() in selected_weekdays:
            dates.append(current)
        current += timedelta(days=1)
    if not dates:
        raise HTTPException(400, "El rango no contiene ninguno de los días seleccionados")
    if project["fecha_inicio"] and dates[0] < project["fecha_inicio"]:
        raise HTTPException(400, "El período incluye fechas anteriores al inicio del proyecto")
    if project["fecha_fin"] and dates[-1] > project["fecha_fin"]:
        raise HTTPException(400, "El período incluye fechas posteriores al cierre del proyecto")

    day_rows = db.execute(text("""SELECT fecha,COALESCE(SUM(horas),0) horas
        FROM proyecto_horas WHERE empleado_id=:employee AND fecha BETWEEN :start AND :end
        GROUP BY fecha"""), {"employee": data.empleado_id, "start": data.fecha_inicio, "end": data.fecha_fin}).mappings().all()
    hours_by_date = {row["fecha"]: Decimal(str(row["horas"])) for row in day_rows}
    overbooked = [day for day in dates if hours_by_date.get(day, Decimal("0")) + data.horas_por_dia > Decimal("8")]
    if overbooked:
        raise HTTPException(409, f"El empleado ya tiene horas registradas que exceden el máximo diario en: {', '.join(day.isoformat() for day in overbooked)}")

    additions_by_month = {}
    for day in dates:
        period = day.strftime("%Y-%m")
        additions_by_month[period] = additions_by_month.get(period, Decimal("0")) + data.horas_por_dia
    for period, added_hours in additions_by_month.items():
        payroll_capacity = db.execute(text("""SELECT SUM(d.dias_trabajados*8)
            FROM planilla_detalle d JOIN planilla p ON p.id=d.planilla_id
            JOIN asiento a ON a.id=p.asiento_id AND a.estado='VIGENTE'
            WHERE d.empleado_id=:employee AND p.periodo=:period"""),
            {"employee": data.empleado_id, "period": period}).scalar_one()
        if payroll_capacity is not None:
            existing_hours = db.execute(text("""SELECT COALESCE(SUM(horas),0) FROM proyecto_horas
                WHERE empleado_id=:employee AND to_char(fecha,'YYYY-MM')=:period"""),
                {"employee": data.empleado_id, "period": period}).scalar_one()
            if Decimal(str(existing_hours)) + added_hours > Decimal(str(payroll_capacity)):
                raise HTTPException(409, f"El rango excede las {payroll_capacity} horas pagadas disponibles en {period}")

    total_hours = data.horas_por_dia * len(dates)
    try:
        db.execute(text("""INSERT INTO proyecto_horas
            (proyecto_id,empleado_id,fecha,actividad,horas,creado_por)
            VALUES(:project,:employee,:date,:activity,:hours,:user)"""), [
                {"project": project_id, "employee": data.empleado_id, "date": day,
                 "activity": data.actividad, "hours": data.horas_por_dia, "user": user.id}
                for day in dates
            ])
        registrar(db, user, "proyectos", "horas", "registrar_lote",
            registro_codigo=project["codigo"], descripcion=f"{employee['codigo']} · {data.actividad}",
            datos_despues={"fecha_inicio": data.fecha_inicio.isoformat(), "fecha_fin": data.fecha_fin.isoformat(),
                "fechas_registradas": [day.isoformat() for day in dates], "horas_por_dia": str(data.horas_por_dia),
                "horas_totales": str(total_hours), "empleado_id": data.empleado_id})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"registros": len(dates), "horas_totales": str(total_hours), "msg": "Horas registradas"}


@router.delete("/{project_id}/horas/{entry_id}", status_code=204)
def quitar_horas_proyecto(project_id: int, entry_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "asignar_planilla"))):
    project = _project(db, project_id, lock=True)
    if project["estado"] != "ABIERTO":
        raise HTTPException(409, "Solo se quitan horas de proyectos abiertos")
    row = db.execute(text("SELECT id,empleado_id,fecha,actividad,horas FROM proyecto_horas WHERE id=:id AND proyecto_id=:project FOR UPDATE"),
        {"id": entry_id, "project": project_id}).mappings().first()
    if not row:
        raise HTTPException(404, "No se encontró el registro de horas")
    try:
        db.execute(text("DELETE FROM proyecto_horas WHERE id=:id"), {"id": entry_id})
        registrar(db, user, "proyectos", "horas", "quitar", registro_id=entry_id,
            registro_codigo=project["codigo"], datos_antes={"empleado_id": row["empleado_id"], "fecha": row["fecha"].isoformat(), "horas": str(row["horas"])})
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.get("/reporte-rentabilidad")
def reporte_rentabilidad_proyectos(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "rentabilidad"))):
    projects = db.execute(text("SELECT id,codigo,nombre,cliente_id,estado,ingreso_estimado,costo_directo_estimado,mano_obra_estimada,costo_indirecto_estimado FROM proyecto ORDER BY nombre")).mappings().all()
    hourly_labor = _hourly_labor_totals(db)
    result = []
    for project in projects:
        totals = db.execute(text(f"""SELECT
            COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='INGRESO'),0) ingresos,
            COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='COSTO_DIRECTO'),0) costos_directos,
            COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='COSTO_INDIRECTO'),0) costos_indirectos
            FROM proyecto_asignacion pa WHERE pa.proyecto_id=:id AND {_source_is_current('pa')}"""),
            {"id": project["id"]}).mappings().one()
        ingresos = _money(totals["ingresos"])
        directos = _money(totals["costos_directos"])
        indirectos = _money(totals["costos_indirectos"])
        labor = _manual_payroll_cost(db, project["id"]) + hourly_labor.get(project["id"], Decimal("0.00"))
        costs = directos + labor + indirectos
        margin = ingresos - costs
        result.append({"id": project["id"], "codigo": project["codigo"], "nombre": project["nombre"],
            "estado": project["estado"], "ingresos": ingresos, "costos_directos": directos,
            "mano_obra": labor, "costos_indirectos": indirectos, "costos_totales": costs,
            "margen": margin, "margen_porcentaje": _money(margin / ingresos * 100) if ingresos else Decimal("0.00")})
    return {"proyectos": result}


@router.get("/{project_id}/rentabilidad")
def rentabilidad(project_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("proyectos", "rentabilidad"))):
    project = _project(db, project_id)
    project = dict(project)
    totals = db.execute(text(f"""SELECT
        COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='INGRESO'),0) ingresos,
        COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='COSTO_DIRECTO'),0) costos_directos,
        COALESCE(SUM(pa.monto) FILTER (WHERE pa.categoria='COSTO_INDIRECTO'),0) costos_indirectos
        FROM proyecto_asignacion pa WHERE pa.proyecto_id=:id
          AND {_source_is_current('pa')}"""), {"id": project_id}).mappings().one()
    ingresos = _money(totals["ingresos"])
    directos = _money(totals["costos_directos"])
    labor = _manual_payroll_cost(db, project_id) + _hourly_labor_totals(db).get(project_id, Decimal("0.00"))
    indirectos = _money(totals["costos_indirectos"])
    costos = directos + labor + indirectos
    margin = ingresos - costos
    percent = _money(margin / ingresos * 100) if ingresos else Decimal("0.00")
    budget_values = {
        "INGRESO": project["ingreso_estimado"],
        "COSTO_DIRECTO": project["costo_directo_estimado"],
        "MANO_OBRA": project["mano_obra_estimada"],
        "COSTO_INDIRECTO": project["costo_indirecto_estimado"],
    }
    actual_values = {
        "INGRESO": ingresos,
        "COSTO_DIRECTO": directos,
        "MANO_OBRA": labor,
        "COSTO_INDIRECTO": indirectos,
    }
    comparison = []
    for category, label in (
        ("INGRESO", "Ingresos"), ("COSTO_DIRECTO", "Costos directos"),
        ("MANO_OBRA", "Mano de obra"), ("COSTO_INDIRECTO", "Costos indirectos"),
    ):
        estimate = budget_values[category]
        comparison.append({
            "categoria": category,
            "concepto": label,
            "estimado": _money(estimate) if estimate is not None else None,
            "real_asignado": actual_values[category],
            "variacion": _money(actual_values[category] - Decimal(str(estimate))) if estimate is not None else None,
        })
    budget_complete = all(value is not None for value in budget_values.values())
    estimate_margin = None
    estimate_margin_percent = None
    if budget_complete:
        estimate_costs = sum((Decimal(str(budget_values[key])) for key in ("COSTO_DIRECTO", "MANO_OBRA", "COSTO_INDIRECTO")), Decimal("0"))
        estimate_margin = _money(Decimal(str(budget_values["INGRESO"])) - estimate_costs)
        estimate_margin_percent = _money(estimate_margin / Decimal(str(budget_values["INGRESO"])) * 100) if budget_values["INGRESO"] else Decimal("0.00")
    details = db.execute(text(f"""SELECT a.id,a.fuente_tipo,a.fuente_detalle_id,a.categoria,a.monto,a.dias_asignados,a.creado_en,
        {_source_is_current('a')} AS fuente_vigente,
        CASE WHEN a.fuente_tipo='PLANILLA' THEN EXISTS (
          SELECT 1 FROM planilla_detalle pd JOIN planilla p ON p.id=pd.planilla_id
          JOIN proyecto_horas ph ON ph.empleado_id=pd.empleado_id AND to_char(ph.fecha,'YYYY-MM')=p.periodo
          WHERE pd.id=a.fuente_detalle_id
        ) ELSE FALSE END AS sustituido_por_horas,
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
    return {"proyecto": project, "ingresos": ingresos, "costos_directos": directos,
            "mano_obra": labor, "costos_indirectos": indirectos, "costos_totales": costos,
            "margen": margin, "margen_porcentaje": percent,
            "comparativo": comparison, "presupuesto_completo": budget_complete,
            "margen_estimado": estimate_margin, "margen_estimado_porcentaje": estimate_margin_percent,
            "asignaciones": [dict(row) for row in details]}

