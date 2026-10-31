"""Facturación, compras y planillas: documentos auxiliares que generan asientos pendientes."""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import Usuario
from app.routers.auth import require_permission
from app.services.auditoria import registrar

router = APIRouter(prefix="/api", tags=["Operaciones"])
CENT = Decimal("0.01")
IVA = Decimal("0.13")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def check_period(db: Session, period_id: int, day: date):
    period = db.execute(text("SELECT * FROM periodo_contable WHERE id=:id"), {"id": period_id}).mappings().first()
    if not period:
        raise HTTPException(400, "El período contable no existe")
    if period["estado"] != "ABIERTO":
        raise HTTPException(400, "El período contable está cerrado")
    if not period["fecha_inicio"] <= day <= period["fecha_fin"]:
        raise HTTPException(400, "La fecha del documento está fuera del período seleccionado")
    return period


def check_leaf_account(db: Session, code: str, label: str):
    account = db.execute(text("SELECT codigo FROM catalogo_cuenta WHERE codigo=:c"), {"c": code}).first()
    if not account:
        raise HTTPException(400, f"{label}: la cuenta {code} no existe")
    if db.execute(text("SELECT 1 FROM catalogo_cuenta WHERE codigo_padre=:c LIMIT 1"), {"c": code}).first():
        raise HTTPException(400, f"{label}: la cuenta {code} es de agrupación; seleccione una subcuenta")


def next_journal_code(db: Session, year: int) -> tuple[str, int]:
    row = db.execute(text("SELECT nextval(pg_get_serial_sequence('asiento','id')) AS id")).mappings().first()
    return f"AST-{year}-{int(row['id']):04d}", int(row["id"])


def create_pending_journal(db: Session, user: Usuario, *, day: date, concept: str, period_id: int,
                           branch_id: Optional[int], lines: list[dict], module: str, doc_id: int, doc_code: str):
    period = check_period(db, period_id, day)
    debit = money(sum((Decimal(str(x["debe"])) for x in lines), Decimal(0)))
    credit = money(sum((Decimal(str(x["haber"])) for x in lines), Decimal(0)))
    if debit <= 0 or debit != credit:
        raise HTTPException(400, "El asiento generado no cuadra; revise los importes y cuentas")
    for line in lines:
        check_leaf_account(db, line["cuenta_codigo"], "Asiento")
    code, journal_id = next_journal_code(db, period["anio"])
    db.execute(text("""INSERT INTO asiento
        (id,codigo,fecha,concepto,tipo,periodo_id,sucursal_id,estado,creado_por)
        VALUES (:id,:c,:f,:co,'DIARIO',:p,:s,'PENDIENTE',:u)"""),
        {"id": journal_id, "c": code, "f": day, "co": concept, "p": period_id, "s": branch_id, "u": user.id})
    for line in lines:
        db.execute(text("""INSERT INTO detalle_asiento
            (asiento_id,cuenta_codigo,debe,haber,descripcion)
            VALUES (:a,:c,:d,:h,:desc)"""),
            {"a": journal_id, "c": line["cuenta_codigo"], "d": line["debe"], "h": line["haber"], "desc": line.get("descripcion")})
    registrar(db, user, module, module[:-1] if module.endswith("s") else module, "enviar_a_aprobacion",
              registro_id=doc_id, registro_codigo=doc_code,
              datos_despues={"estado": "PENDIENTE", "asiento_id": journal_id, "asiento_codigo": code})
    return journal_id, code


class PartyIn(BaseModel):
    codigo: str = Field(..., min_length=6, max_length=20, pattern=r"^[A-Z]{2,5}-\d{3,6}$")
    nombre: str = Field(..., min_length=2, max_length=150)
    nit: Optional[str] = Field(None, max_length=20)
    nrc: Optional[str] = Field(None, max_length=20)
    giro: Optional[str] = Field(None, max_length=250)
    direccion: Optional[str] = Field(None, max_length=250)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    cuenta_codigo: Optional[str] = Field(None, max_length=20)
    sucursal_id: Optional[int] = None

    @field_validator("codigo", mode="before")
    @classmethod
    def normalizar_codigo(cls, value):
        return str(value).strip().upper() if value is not None else value

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, value):
        if value is None:
            return value
        cleaned = " ".join(str(value).split())
        if cleaned and not any(char.isalpha() for char in cleaned):
            raise ValueError("El nombre o razón social debe incluir letras")
        return cleaned

    @field_validator("nit", mode="before")
    @classmethod
    def normalizar_nit(cls, value):
        if value is None or not str(value).strip():
            return None
        raw = str(value).strip()
        formats = (r"\d{9}", r"\d{14}", r"\d{8}-\d", r"\d{4}-\d{6}-\d{3}-\d")
        if not any(re.fullmatch(pattern, raw) for pattern in formats):
            raise ValueError("El NIT debe tener 9 o 14 dígitos, sin guiones o en el formato agrupado mostrado")
        digits = raw.replace("-", "")
        return digits

    @field_validator("nrc", mode="before")
    @classmethod
    def normalizar_nrc(cls, value):
        if value is None or not str(value).strip():
            return None
        # Hacienda define el NRC del DTE sin guiones, con 2 a 8 dígitos;
        # se acepta un guion de separación visual y se guarda sin él.
        raw = str(value).strip()
        if not re.fullmatch(r"\d{2,8}|\d{2,7}-\d", raw):
            raise ValueError("El NRC debe tener de 2 a 8 dígitos, sin guion o con un dígito verificador separado")
        digits = raw.replace("-", "")
        if not 2 <= len(digits) <= 8:
            raise ValueError("El NRC debe tener entre 2 y 8 dígitos")
        return digits

    @field_validator("giro", mode="before")
    @classmethod
    def limpiar_giro(cls, value):
        if value is None:
            return None
        cleaned = " ".join(str(value).split())
        if cleaned and not any(char.isalpha() for char in cleaned):
            raise ValueError("El giro debe describir una actividad económica con texto")
        return cleaned or None

    @field_validator("direccion", mode="before")
    @classmethod
    def limpiar_direccion(cls, value):
        if value is None:
            return None
        cleaned = " ".join(str(value).split())
        if cleaned and len(cleaned) < 5:
            raise ValueError("Escribe una dirección más completa (mínimo 5 caracteres)")
        return cleaned or None

    @field_validator("telefono", mode="before")
    @classmethod
    def normalizar_telefono(cls, value):
        if value is None or not str(value).strip():
            return None
        raw = str(value).strip()
        if not re.fullmatch(r"[+0-9()\-\s]+", raw):
            raise ValueError("El teléfono solo debe contener números, espacios, paréntesis o guiones")
        digits = re.sub(r"\D", "", raw)
        if len(digits) == 11 and digits.startswith("503"):
            return f"+{digits}"
        if len(digits) == 8:
            return digits
        raise ValueError("El teléfono debe tener 8 dígitos; puedes anteponer el código +503")

    @field_validator("email", mode="before")
    @classmethod
    def validar_correo(cls, value):
        if value is None or not str(value).strip():
            return None
        email = str(value).strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Escribe un correo con formato nombre@dominio.com")
        return email


class CustomerIn(PartyIn):
    """Datos obligatorios de identificación fiscal para clientes."""
    codigo: Optional[str] = Field(None, min_length=7, max_length=10, pattern=r"^CLI-\d{3,6}$")
    nombre: str = Field(..., min_length=2, max_length=150)
    nit: str = Field(..., min_length=9, max_length=17)
    nrc: str = Field(..., min_length=2, max_length=9)
    giro: str = Field(..., min_length=3, max_length=250)
    direccion: str = Field(..., min_length=5, max_length=250)

    @field_validator("codigo", mode="before")
    @classmethod
    def normalizar_codigo_cliente(cls, value):
        code = str(value).strip().upper() if value is not None else ""
        return code or None

    @field_validator("nit", mode="before")
    @classmethod
    def validar_nit_cliente(cls, value):
        raw = str(value or "").strip()
        if not re.fullmatch(r"(?:\d{9}|\d{14}|\d{8}-\d|\d{4}-\d{6}-\d{3}-\d)", raw):
            raise ValueError("El NIT es obligatorio: escribe 9 dígitos (formato DUI) o 14 dígitos. Ejemplo: 0614-010199-001-1")
        return raw.replace("-", "")

    @field_validator("nrc", mode="before")
    @classmethod
    def validar_nrc_cliente(cls, value):
        raw = str(value or "").strip()
        if not re.fullmatch(r"\d{2,8}|\d{2,7}-\d", raw):
            raise ValueError("El NRC es obligatorio y debe tener de 2 a 8 dígitos. Ejemplo: 123456-7")
        return raw.replace("-", "")

    @field_validator("giro", mode="before")
    @classmethod
    def validar_giro_cliente(cls, value):
        cleaned = " ".join(str(value or "").split())
        if len(cleaned) < 3 or not any(char.isalpha() for char in cleaned):
            raise ValueError("El giro o actividad económica es obligatorio; escribe la actividad registrada del cliente")
        return cleaned

    @field_validator("direccion", mode="before")
    @classmethod
    def validar_direccion_cliente(cls, value):
        cleaned = " ".join(str(value or "").split())
        if len(cleaned) < 5:
            raise ValueError("La dirección es obligatoria y debe tener al menos 5 caracteres")
        return cleaned


class SupplierIn(PartyIn):
    """Datos requeridos para identificar y registrar correctamente a un proveedor."""
    codigo: Optional[str] = Field(None, min_length=7, max_length=10, pattern=r"^PRO-\d{3,6}$")
    nombre: str = Field(..., min_length=2, max_length=150)
    nit: str = Field(..., min_length=9, max_length=17)
    nrc: str = Field(..., min_length=2, max_length=9)
    direccion: str = Field(..., min_length=5, max_length=250)

    @field_validator("codigo", mode="before")
    @classmethod
    def normalizar_codigo_proveedor(cls, value):
        code = str(value).strip().upper() if value is not None else ""
        return code or None

    @field_validator("nit", mode="before")
    @classmethod
    def validar_nit_proveedor(cls, value):
        raw = str(value or "").strip()
        if not re.fullmatch(r"(?:\d{9}|\d{14}|\d{8}-\d|\d{4}-\d{6}-\d{3}-\d)", raw):
            raise ValueError("El NIT es obligatorio: escribe 9 dígitos (formato DUI) o 14. Ejemplo: 0614-010199-001-1")
        return raw.replace("-", "")

    @field_validator("nrc", mode="before")
    @classmethod
    def validar_nrc_proveedor(cls, value):
        raw = str(value or "").strip()
        if not re.fullmatch(r"\d{2,8}|\d{2,7}-\d", raw):
            raise ValueError("El NRC es obligatorio y debe tener de 2 a 8 dígitos. Ejemplo: 123456-7")
        return raw.replace("-", "")

    @field_validator("direccion", mode="before")
    @classmethod
    def validar_direccion_proveedor(cls, value):
        cleaned = " ".join(str(value or "").split())
        if len(cleaned) < 5:
            raise ValueError("La dirección es obligatoria y debe tener al menos 5 caracteres")
        return cleaned


class LineIn(BaseModel):
    descripcion: str = Field(..., min_length=2, max_length=500)
    cantidad: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    precio_unitario: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)
    unidad_medida: str = Field("UNIDAD", min_length=1, max_length=20)
    tipo_venta: str = Field("GRAVADA", pattern=r"^(GRAVADA|EXENTA|NO_SUJETA)$")
    producto_codigo: Optional[str] = Field(None, max_length=20)
    cuenta_codigo: str = Field(..., min_length=1, max_length=20)

    @field_validator("cantidad", "precio_unitario", mode="before")
    @classmethod
    def redondear_a_dos_decimales(cls, value):
        try:
            return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
        except Exception as exc:
            raise ValueError("Debe ser un número válido con hasta dos decimales") from exc


class InvoiceIn(BaseModel):
    numero: str = Field(..., min_length=13, max_length=13, pattern=r"^FAC-\d{4}-\d{4}$")
    tipo_dte: str = "CCF"
    fecha: date
    cliente_id: int
    sucursal_id: int
    periodo_id: int
    condicion_operacion: str = "CONTADO"
    forma_pago: Optional[str] = None
    plazo_pago: Optional[int] = Field(None, ge=1, le=365)
    cuenta_pago_codigo: Optional[str] = Field(None, max_length=20)
    nota_remision_numero: Optional[str] = Field(None, max_length=30)
    nota_remision_fecha: Optional[date] = None
    detalles: list[LineIn] = Field(..., min_length=1)

    @field_validator("numero", mode="before")
    @classmethod
    def normalizar_numero_interno(cls, value):
        return str(value).strip().upper() if value is not None else value


class PurchaseLineIn(LineIn):
    tipo_iva: str = Field("GRAVADA", pattern=r"^(GRAVADA|EXENTA|NO_SUJETA)$")


class PurchaseIn(BaseModel):
    numero: Optional[str] = Field(None, max_length=30)
    tipo_doc: str = "CCF"
    fecha: date
    proveedor_id: int
    sucursal_id: int
    periodo_id: int
    detalles: list[PurchaseLineIn] = Field(..., min_length=1)

    @field_validator("numero", mode="before")
    @classmethod
    def limpiar_numero_documento(cls, value):
        if value is None or not str(value).strip():
            return None
        return str(value).strip()


class EmployeeIn(BaseModel):
    codigo: Optional[str] = Field(None, min_length=7, max_length=10, pattern=r"^EMP-\d{3,6}$")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    dui: str = Field(..., min_length=10, max_length=10)
    nit: Optional[str] = Field(None, max_length=20)
    cargo: str = Field(..., min_length=2, max_length=100)
    salario_base: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2)
    fecha_ingreso: date
    sucursal_id: int

    @field_validator("codigo", mode="before")
    @classmethod
    def limpiar_codigo_empleado(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("nombres", "apellidos", "cargo", mode="before")
    @classmethod
    def limpiar_texto_empleado(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("dui")
    @classmethod
    def validar_dui_empleado(cls, value):
        raw = re.sub(r"\D", "", value or "")
        if len(raw) != 9:
            raise ValueError("Use 9 dígitos. Ejemplo: 01234567-8")
        return f"{raw[:8]}-{raw[8]}"

    @field_validator("nit")
    @classmethod
    def validar_nit_empleado(cls, value):
        if value is None or not value.strip():
            return None
        raw = value.strip()
        if not re.fullmatch(r"(?:\d{9}|\d{14}|\d{8}-\d|\d{4}-\d{6}-\d{3}-\d)", raw):
            raise ValueError("Use 9 o 14 dígitos. Ejemplo: 0614-010199-001-1")
        return raw


class PayrollLineIn(BaseModel):
    empleado_id: int
    dias_trabajados: int = Field(30, ge=1, le=31)
    cuenta_gasto_codigo: str = Field("4.1.3.01", min_length=1, max_length=20)
    horas_extra: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    bonificaciones: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    comisiones: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    isss_patronal: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    afp_patronal: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    deduccion_isss: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    deduccion_afp: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    deduccion_renta: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)
    otras_deducciones: Decimal = Field(0, ge=0, max_digits=14, decimal_places=2)


class PayrollIn(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    periodo: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    fecha_pago: date
    sucursal_id: Optional[int] = None
    periodo_id: int
    detalles: list[PayrollLineIn] = Field(..., min_length=1)


class PayrollPaymentIn(BaseModel):
    fecha_pago: date
    periodo_id: int
    cuenta_pago_codigo: str = Field(..., min_length=1, max_length=20)


@router.get("/productos-servicios")
def invoice_products(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "ver"))):
    rows = db.execute(text("""
        SELECT codigo, nombre, linea_negocio, tipo, unidad_medida, cuenta_ingreso_codigo
          FROM catalogo_producto_servicio
         WHERE activo = true
         ORDER BY linea_negocio, nombre
    """)).mappings().all()
    return {"productos": [dict(row) for row in rows]}


@router.get("/clientes")
def customers(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "ver"))):
    rows = db.execute(text("SELECT id,codigo,nombre,nit,nrc,giro,direccion,telefono,email,cuenta_codigo,sucursal_id,estado FROM cliente ORDER BY nombre")).mappings().all()
    return {"clientes": [dict(r) for r in rows]}


@router.post("/clientes", status_code=201)
def create_customer(data: CustomerIn, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "crear"))):
    if data.codigo:
        codigo = data.codigo
    else:
        # Serialize automatic numbering so two simultaneous registrations do not receive the same code.
        db.execute(text("LOCK TABLE cliente IN EXCLUSIVE MODE"))
        siguiente = db.execute(text("""SELECT COALESCE(MAX(substring(codigo from 5)::integer), 0) + 1
            FROM cliente WHERE codigo ~ '^CLI-[0-9]{3,6}$'""")).scalar_one()
        if siguiente > 999999:
            raise HTTPException(409, "Se agotaron los códigos automáticos de cliente CLI")
        codigo = f"CLI-{int(siguiente):03d}"
    if db.execute(text("SELECT 1 FROM cliente WHERE codigo=:c"), {"c": codigo}).first():
        raise HTTPException(409, "El código de cliente ya existe")
    if data.cuenta_codigo:
        check_leaf_account(db, data.cuenta_codigo, "Cliente")
    result = db.execute(text("""INSERT INTO cliente (codigo,nombre,nit,nrc,giro,direccion,telefono,email,cuenta_codigo,sucursal_id,estado)
      VALUES (:codigo,:nombre,:nit,:nrc,:giro,:direccion,:telefono,:email,:cuenta,:sucursal,'ACTIVO') RETURNING id"""),
      {**data.model_dump(), "codigo": codigo, "nombre": data.nombre.strip(), "cuenta": data.cuenta_codigo, "sucursal": data.sucursal_id}).mappings().first()
    after = data.model_dump(mode="json")
    after["codigo"] = codigo
    registrar(db,user,"facturas","cliente","crear",registro_id=result["id"],registro_codigo=codigo,datos_despues=after)
    db.commit()
    return {"id": result["id"], "codigo": codigo, "msg": "Cliente creado"}


@router.put("/clientes/{cliente_id}")
def update_customer(cliente_id: int, data: CustomerIn, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "editar"))):
    current = db.execute(text("SELECT * FROM cliente WHERE id=:id"), {"id": cliente_id}).mappings().first()
    if not current:
        raise HTTPException(404, "No se encontró el cliente")
    codigo = data.codigo or current["codigo"]
    if db.execute(text("SELECT 1 FROM cliente WHERE id<>:id AND codigo=:codigo"), {"id": cliente_id, "codigo": codigo}).first():
        raise HTTPException(409, "Ese código ya pertenece a otro cliente")
    if data.cuenta_codigo:
        check_leaf_account(db, data.cuenta_codigo, "Cliente")
    before = {key: current.get(key) for key in ("codigo", "nombre", "nit", "nrc", "giro", "direccion", "telefono", "email", "cuenta_codigo", "sucursal_id", "estado")}
    db.execute(text("""UPDATE cliente SET codigo=:codigo,nombre=:nombre,nit=:nit,nrc=:nrc,giro=:giro,
        direccion=:direccion,telefono=:telefono,email=:email,cuenta_codigo=:cuenta,sucursal_id=:sucursal
        WHERE id=:id"""),
        {**data.model_dump(), "id": cliente_id, "codigo": codigo, "nombre": data.nombre,
         "cuenta": data.cuenta_codigo, "sucursal": data.sucursal_id})
    after = data.model_dump(mode="json")
    after["codigo"] = codigo
    after["estado"] = current["estado"]
    registrar(db, user, "facturas", "cliente", "editar", registro_id=cliente_id,
              registro_codigo=codigo, datos_antes=before, datos_despues=after)
    db.commit()
    return {"id": cliente_id, "msg": "Cliente actualizado"}


@router.delete("/clientes/{cliente_id}")
def deactivate_customer(cliente_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "eliminar"))):
    current = db.execute(text("SELECT id,codigo,nombre,estado FROM cliente WHERE id=:id"), {"id": cliente_id}).mappings().first()
    if not current:
        raise HTTPException(404, "No se encontró el cliente")
    if current["estado"] == "INACTIVO":
        return {"id": cliente_id, "estado": "INACTIVO", "msg": "El cliente ya estaba dado de baja"}
    db.execute(text("UPDATE cliente SET estado='INACTIVO' WHERE id=:id"), {"id": cliente_id})
    registrar(db, user, "facturas", "cliente", "dar_de_baja", registro_id=cliente_id,
              registro_codigo=current["codigo"], datos_antes={"estado": current["estado"]},
              datos_despues={"estado": "INACTIVO"})
    db.commit()
    return {"id": cliente_id, "estado": "INACTIVO", "msg": "Cliente dado de baja; sus facturas e historial se conservan"}


@router.post("/clientes/{cliente_id}/activar")
def activate_customer(cliente_id: int, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "editar"))):
    current = db.execute(text("SELECT id,codigo,estado FROM cliente WHERE id=:id"), {"id": cliente_id}).mappings().first()
    if not current:
        raise HTTPException(404, "No se encontró el cliente")
    db.execute(text("UPDATE cliente SET estado='ACTIVO' WHERE id=:id"), {"id": cliente_id})
    registrar(db, user, "facturas", "cliente", "reactivar", registro_id=cliente_id,
              registro_codigo=current["codigo"], datos_antes={"estado": current["estado"]},
              datos_despues={"estado": "ACTIVO"})
    db.commit()
    return {"id": cliente_id, "estado": "ACTIVO", "msg": "Cliente reactivado"}


@router.get("/facturas")
def invoices(db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "ver")),
             desde: Optional[date] = None, hasta: Optional[date] = None):
    if desde and hasta and desde > hasta: raise HTTPException(400, "Rango de fechas inválido")
    rows = db.execute(text("""SELECT f.id,f.numero,f.tipo_dte,f.fecha,f.cliente_id,c.nombre cliente,
      f.sucursal_id,f.periodo_id,f.estado,f.asiento_id,COUNT(d.id) lineas,
      COALESCE(SUM(ROUND(d.cantidad*d.precio_unitario,2)),0) subtotal,
      COALESCE(SUM(CASE WHEN d.tipo_venta='GRAVADA' THEN ROUND(d.cantidad*d.precio_unitario,2) ELSE 0 END),0) gravada,
      COALESCE(SUM(CASE WHEN d.tipo_venta='EXENTA' THEN ROUND(d.cantidad*d.precio_unitario,2) ELSE 0 END),0) exenta,
      COALESCE(SUM(CASE WHEN d.tipo_venta='NO_SUJETA' THEN ROUND(d.cantidad*d.precio_unitario,2) ELSE 0 END),0) no_sujeta,
      ROUND(COALESCE(SUM(CASE WHEN d.tipo_venta='GRAVADA' THEN ROUND(d.cantidad*d.precio_unitario,2) ELSE 0 END),0)*0.13,2) iva,
      COALESCE(SUM(ROUND(d.cantidad*d.precio_unitario,2)),0)+ROUND(COALESCE(SUM(CASE WHEN d.tipo_venta='GRAVADA' THEN ROUND(d.cantidad*d.precio_unitario,2) ELSE 0 END),0)*0.13,2) total
      FROM factura f JOIN cliente c ON c.id=f.cliente_id LEFT JOIN factura_detalle d ON d.factura_id=f.id
      WHERE (:desde IS NULL OR f.fecha>=:desde) AND (:hasta IS NULL OR f.fecha<=:hasta)
      GROUP BY f.id,c.nombre ORDER BY f.fecha DESC,f.id DESC"""), {"desde":desde,"hasta":hasta}).mappings().all()
    return {"facturas":[dict(r) for r in rows]}


@router.get("/facturas/{doc_id}")
def invoice_detail(doc_id: int, db: Session = Depends(get_db),
                   user: Usuario = Depends(require_permission("facturas", "ver"))):
    doc = db.execute(text("""
        SELECT f.id, f.numero, f.tipo_dte, f.fecha, f.creado_en, f.estado,
               f.condicion_operacion, f.forma_pago, f.plazo_pago, f.cuenta_pago_codigo,
               f.nota_remision_numero, f.nota_remision_fecha,
               c.codigo cliente_codigo, c.nombre cliente, c.nit cliente_nit,
               c.nrc cliente_nrc, c.giro cliente_giro, c.direccion cliente_direccion,
               c.telefono cliente_telefono, c.email cliente_email,
               s.nombre sucursal, s.direccion sucursal_direccion,
               COALESCE(s.razon_social, e.razon_social, s.nombre, e.nombre_comercial) emisor_nombre,
               COALESCE(s.nit, e.nit) emisor_nit, COALESCE(s.nrc, e.nrc) emisor_nrc,
               e.nombre_comercial, e.giro
          FROM factura f
          JOIN cliente c ON c.id = f.cliente_id
          JOIN sucursal s ON s.id = f.sucursal_id
          LEFT JOIN (SELECT * FROM empresa ORDER BY id LIMIT 1) e ON TRUE
         WHERE f.id = :id
    """), {"id": doc_id}).mappings().first()
    if not doc:
        raise HTTPException(404, "Factura no encontrada")

    detalles = db.execute(text("""
        SELECT descripcion, cantidad, precio_unitario, unidad_medida, tipo_venta, producto_codigo
          FROM factura_detalle
         WHERE factura_id = :id
         ORDER BY id
    """), {"id": doc_id}).mappings().all()
    lineas = []
    subtotal = Decimal("0.00")
    for linea in detalles:
        importe = money(linea["cantidad"] * linea["precio_unitario"])
        subtotal += importe
        lineas.append({
            "descripcion": linea["descripcion"],
            "cantidad": linea["cantidad"],
            "precio_unitario": linea["precio_unitario"],
            "unidad_medida": linea["unidad_medida"],
            "tipo_venta": linea["tipo_venta"],
            "producto_codigo": linea["producto_codigo"],
            "importe": importe,
        })
    subtotal = money(subtotal)
    gravada = money(sum((line["importe"] for line in lineas if line["tipo_venta"] == "GRAVADA"), Decimal("0.00")))
    exenta = money(sum((line["importe"] for line in lineas if line["tipo_venta"] == "EXENTA"), Decimal("0.00")))
    no_sujeta = money(sum((line["importe"] for line in lineas if line["tipo_venta"] == "NO_SUJETA"), Decimal("0.00")))
    iva = money(gravada * IVA)
    return {
        "factura": dict(doc),
        "detalles": lineas,
        "subtotal": subtotal,
        "gravada": gravada,
        "exenta": exenta,
        "no_sujeta": no_sujeta,
        "iva": iva,
        "total": subtotal + iva,
        "representacion_interna": True,
    }


@router.post("/facturas", status_code=201)
def create_invoice(data: InvoiceIn, db: Session = Depends(get_db), user: Usuario = Depends(require_permission("facturas", "crear"))):
    if data.tipo_dte not in ("CCF", "FCON"): raise HTTPException(400,"Tipo de documento: CCF o FCON")
    if data.condicion_operacion not in ("CONTADO", "CREDITO"):
        raise HTTPException(400, "Condición de operación inválida")
    if data.condicion_operacion == "CREDITO" and not data.plazo_pago:
        raise HTTPException(400, "Indique el plazo en días para una venta al crédito")
    if data.nota_remision_numero and not data.nota_remision_fecha:
        raise HTTPException(400, "Indique la fecha de la nota de remisión")
    if not data.forma_pago:
        raise HTTPException(400, "Seleccione cómo se realiza o realizará el pago")
    if data.forma_pago not in ("EFECTIVO", "TARJETA", "TRANSFERENCIA", "CHEQUE"):
        raise HTTPException(400, "Forma de pago inválida")
    check_period(db,data.periodo_id,data.fecha)
    client=db.execute(text("SELECT * FROM cliente WHERE id=:i AND estado='ACTIVO'"),{"i":data.cliente_id}).mappings().first()
    if not client: raise HTTPException(400,"Cliente inexistente o inactivo")
    if data.tipo_dte == "CCF" and any(not client[field] or not str(client[field]).strip() for field in ("nit", "nrc", "giro", "direccion")):
        raise HTTPException(400, "Para un CCF registre en el cliente: NIT, NRC, giro o actividad y dirección")
    if data.tipo_dte == "CCF":
        nit = str(client["nit"]).strip()
        nit_formats = (r"\d{9}", r"\d{14}", r"\d{8}-\d", r"\d{4}-\d{6}-\d{3}-\d")
        if not any(re.fullmatch(pattern, nit) for pattern in nit_formats):
            raise HTTPException(400, "El NIT del cliente debe tener 9 o 14 dígitos; actualiza su ficha desde Nuevo cliente")
        nrc = str(client["nrc"]).strip()
        if not re.fullmatch(r"\d{2,8}|\d{2,7}-\d", nrc):
            raise HTTPException(400, "El NRC del cliente debe tener de 2 a 8 dígitos; actualiza su ficha desde Nuevo cliente")
    if data.condicion_operacion != "CREDITO":
        if not data.cuenta_pago_codigo:
            raise HTTPException(400, "Seleccione la cuenta de caja o bancos que recibió el pago")
        if not data.cuenta_pago_codigo.startswith(("1.1.1.", "1.1.2.")):
            raise HTTPException(400, "La cuenta de cobro debe ser de caja, bancos o inversiones temporales")
        check_leaf_account(db, data.cuenta_pago_codigo, "Cuenta de cobro")
    if not db.execute(text("SELECT 1 FROM sucursal WHERE id=:i"),{"i":data.sucursal_id}).first(): raise HTTPException(400,"Sucursal inexistente")
    if db.execute(text("SELECT 1 FROM factura WHERE numero=:n"),{"n":data.numero.strip()}).first(): raise HTTPException(409,"El número de factura ya existe")
    lineas_validadas = []
    for line in data.detalles:
        cuenta_codigo = line.cuenta_codigo
        if line.producto_codigo:
            producto = db.execute(text("""SELECT codigo, cuenta_ingreso_codigo, unidad_medida
                FROM catalogo_producto_servicio WHERE codigo=:codigo AND activo=true"""),
                {"codigo": line.producto_codigo}).mappings().first()
            if not producto:
                raise HTTPException(400, f"El producto o servicio {line.producto_codigo} ya no está disponible")
            cuenta_codigo = producto["cuenta_ingreso_codigo"]
        if not cuenta_codigo.startswith("5."):
            raise HTTPException(400, "Las líneas de una factura deben usar cuentas de ingreso (clase 5)")
        check_leaf_account(db,cuenta_codigo,"Ingreso")
        lineas_validadas.append((line, cuenta_codigo))
    try:
        fid=db.execute(text("""INSERT INTO factura(numero,tipo_dte,fecha,cliente_id,sucursal_id,periodo_id,
          condicion_operacion,forma_pago,plazo_pago,cuenta_pago_codigo,nota_remision_numero,nota_remision_fecha,estado,creado_por)
          VALUES(:n,:t,:f,:c,:s,:p,:cond,:forma,:plazo,:cuenta_pago,:nota_numero,:nota_fecha,'BORRADOR',:u) RETURNING id"""),
          {"n":data.numero.strip(),"t":data.tipo_dte,"f":data.fecha,"c":data.cliente_id,"s":data.sucursal_id,
           "p":data.periodo_id,"cond":data.condicion_operacion,"forma":data.forma_pago,"plazo":data.plazo_pago,
           "cuenta_pago":data.cuenta_pago_codigo,"nota_numero":data.nota_remision_numero,
           "nota_fecha":data.nota_remision_fecha,"u":user.id}).scalar_one()
        for line, cuenta_codigo in lineas_validadas:
            db.execute(text("""INSERT INTO factura_detalle
                (factura_id,descripcion,cantidad,precio_unitario,unidad_medida,tipo_venta,producto_codigo,cuenta_ingreso_codigo)
                VALUES(:f,:d,:c,:p,:unidad,:tipo,:producto,:cuenta)"""),
             {"f":fid,"d":line.descripcion.strip(),"c":line.cantidad,"p":line.precio_unitario,
              "unidad":line.unidad_medida,"tipo":line.tipo_venta,"producto":line.producto_codigo,"cuenta":cuenta_codigo})
        registrar(db,user,"facturas","factura","crear",registro_id=fid,registro_codigo=data.numero,datos_despues={"estado":"BORRADOR","tipo":data.tipo_dte})
        db.commit()
    except Exception:
        db.rollback(); raise
    return {"id":fid,"estado":"BORRADOR","msg":"Factura guardada en borrador"}


@router.delete("/facturas/{doc_id}")
def delete_draft_invoice(
    doc_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permission("facturas", "eliminar")),
):
    doc = db.execute(
        text("SELECT id, numero, estado, asiento_id FROM factura WHERE id=:id FOR UPDATE"),
        {"id": doc_id},
    ).mappings().first()
    if not doc:
        raise HTTPException(404, "No se encontró la factura")
    if doc["estado"] != "BORRADOR" or doc["asiento_id"] is not None:
        raise HTTPException(
            409,
            "Solo se pueden eliminar facturas en borrador que aún no se hayan enviado a contabilidad. Las demás deben conservar su historial.",
        )

    try:
        registrar(
            db,
            user,
            "facturas",
            "factura",
            "eliminar",
            registro_id=doc_id,
            registro_codigo=doc["numero"],
            descripcion="Se eliminó una factura en borrador que no tenía asiento contable.",
            datos_antes={"numero": doc["numero"], "estado": doc["estado"]},
        )
        # factura_detalle usa ON DELETE CASCADE; la bitácora retiene quién,
        # cuándo y cuál número interno se eliminó.
        db.execute(text("DELETE FROM factura WHERE id=:id"), {"id": doc_id})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": doc_id, "numero": doc["numero"], "msg": "Factura en borrador eliminada"}


@router.post("/facturas/{doc_id}/enviar")
def send_invoice(doc_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("facturas","aprobar"))):
    doc=db.execute(text("SELECT f.*,c.cuenta_codigo FROM factura f JOIN cliente c ON c.id=f.cliente_id WHERE f.id=:i FOR UPDATE"),{"i":doc_id}).mappings().first()
    if not doc: raise HTTPException(404,"Factura no encontrada")
    if doc["estado"]!="BORRADOR": raise HTTPException(409,"Solo se envían facturas en borrador")
    lines=db.execute(text("SELECT descripcion,cantidad,precio_unitario,tipo_venta,cuenta_ingreso_codigo FROM factura_detalle WHERE factura_id=:i ORDER BY id"),{"i":doc_id}).mappings().all()
    if not lines: raise HTTPException(400,"La factura debe incluir detalles")
    subtotal=money(sum((money(x["cantidad"]*x["precio_unitario"]) for x in lines),Decimal(0)))
    base_gravada=money(sum((money(x["cantidad"]*x["precio_unitario"]) for x in lines if x["tipo_venta"]=="GRAVADA"),Decimal(0)))
    iva=money(base_gravada*IVA); total=subtotal+iva
    if doc["condicion_operacion"] == "CREDITO":
        settlement_account = doc["cuenta_codigo"] or "1.1.3.01.02"
        settlement_label = f"Cliente {doc['numero']}"
    else:
        settlement_account = doc["cuenta_pago_codigo"] or "1.1.1.01"
        settlement_label = f"Cobro factura {doc['numero']}"
    journal=[{"cuenta_codigo":settlement_account,"debe":total,"haber":0,"descripcion":settlement_label}]
    for line in lines: journal.append({"cuenta_codigo":line["cuenta_ingreso_codigo"],"debe":0,"haber":money(line["cantidad"]*line["precio_unitario"]),"descripcion":line["descripcion"]})
    journal.append({"cuenta_codigo":"2.1.10.01","debe":0,"haber":iva,"descripcion":"IVA débito fiscal 13%"})
    try:
        jid,jcode=create_pending_journal(db,user,day=doc["fecha"],concept=f"Factura {doc['numero']} - {doc['tipo_dte']}",period_id=doc["periodo_id"],branch_id=doc["sucursal_id"],lines=journal,module="facturas",doc_id=doc_id,doc_code=doc["numero"])
        db.execute(text("UPDATE factura SET estado='PENDIENTE',asiento_id=:a,aprobado_por=:u,aprobado_en=:d WHERE id=:i"),{"a":jid,"u":user.id,"d":datetime.utcnow(),"i":doc_id})
        db.commit()
    except Exception:
        db.rollback(); raise
    return {"estado":"PENDIENTE","asiento_id":jid,"asiento_codigo":jcode,"subtotal":str(subtotal),"iva":str(iva),"total":str(total),"msg":"Factura enviada; falta aprobar el asiento en Control"}


@router.get("/proveedores")
def suppliers(db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","ver"))):
    rows=db.execute(text("SELECT id,codigo,nombre,nit,nrc,direccion,telefono,email,cuenta_codigo,sucursal_id,estado FROM proveedor ORDER BY nombre")).mappings().all()
    return {"proveedores":[dict(r) for r in rows]}


@router.post("/proveedores",status_code=201)
def create_supplier(data:SupplierIn,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","crear"))):
    if data.codigo:
        codigo=data.codigo
    else:
        db.execute(text("LOCK TABLE proveedor IN EXCLUSIVE MODE"))
        siguiente=db.execute(text("""SELECT COALESCE(MAX(substring(codigo from 5)::integer),0)+1
            FROM proveedor WHERE codigo ~ '^PRO-[0-9]{3,6}$'""")).scalar_one()
        if siguiente>999999: raise HTTPException(409,"Se agotaron los códigos automáticos de proveedor PRO")
        codigo=f"PRO-{int(siguiente):03d}"
    if db.execute(text("SELECT 1 FROM proveedor WHERE codigo=:c"),{"c":codigo}).first(): raise HTTPException(409,"El código de proveedor ya existe")
    account=data.cuenta_codigo or "2.1.1.01"
    check_leaf_account(db,account,"Proveedor")
    result=db.execute(text("""INSERT INTO proveedor(codigo,nombre,nit,nrc,direccion,telefono,email,cuenta_codigo,sucursal_id,estado)
      VALUES(:codigo,:nombre,:nit,:nrc,:direccion,:telefono,:email,:cuenta,:sucursal,'ACTIVO') RETURNING id"""),
      {**data.model_dump(),"codigo":codigo,"nombre":data.nombre.strip(),"cuenta":account,"sucursal":data.sucursal_id}).mappings().first()
    after=data.model_dump(mode="json"); after["codigo"]=codigo
    registrar(db,user,"compras","proveedor","crear",registro_id=result["id"],registro_codigo=codigo,datos_despues=after)
    db.commit(); return {"id":result["id"],"codigo":codigo,"msg":"Proveedor creado"}


@router.put("/proveedores/{proveedor_id}")
def update_supplier(proveedor_id:int,data:SupplierIn,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","editar"))):
    current=db.execute(text("SELECT * FROM proveedor WHERE id=:id"),{"id":proveedor_id}).mappings().first()
    if not current: raise HTTPException(404,"No se encontró el proveedor")
    codigo=data.codigo or current["codigo"]
    if db.execute(text("SELECT 1 FROM proveedor WHERE id<>:id AND codigo=:codigo"),{"id":proveedor_id,"codigo":codigo}).first():
        raise HTTPException(409,"Ese código ya pertenece a otro proveedor")
    account=data.cuenta_codigo or current["cuenta_codigo"] or "2.1.1.01"
    check_leaf_account(db,account,"Proveedor")
    before={key:current.get(key) for key in ("codigo","nombre","nit","nrc","direccion","telefono","email","cuenta_codigo","sucursal_id","estado")}
    db.execute(text("""UPDATE proveedor SET codigo=:codigo,nombre=:nombre,nit=:nit,nrc=:nrc,direccion=:direccion,
        telefono=:telefono,email=:email,cuenta_codigo=:cuenta,sucursal_id=:sucursal WHERE id=:id"""),
        {**data.model_dump(),"id":proveedor_id,"codigo":codigo,"nombre":data.nombre.strip(),"cuenta":account,"sucursal":data.sucursal_id})
    after={key:data.model_dump(mode="json").get(key) for key in ("codigo","nombre","nit","nrc","direccion","telefono","email","cuenta_codigo","sucursal_id")}
    after["codigo"]=codigo
    after["cuenta_codigo"]=account
    after["estado"]=current["estado"]
    registrar(db,user,"compras","proveedor","editar",registro_id=proveedor_id,registro_codigo=codigo,
              datos_antes=before,datos_despues=after)
    db.commit(); return {"id":proveedor_id,"msg":"Proveedor actualizado"}


@router.delete("/proveedores/{proveedor_id}")
def deactivate_supplier(proveedor_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","editar"))):
    current=db.execute(text("SELECT id,codigo,nombre,estado FROM proveedor WHERE id=:id"),{"id":proveedor_id}).mappings().first()
    if not current: raise HTTPException(404,"No se encontró el proveedor")
    if current["estado"]=="INACTIVO": return {"id":proveedor_id,"estado":"INACTIVO","msg":"El proveedor ya estaba dado de baja"}
    db.execute(text("UPDATE proveedor SET estado='INACTIVO' WHERE id=:id"),{"id":proveedor_id})
    registrar(db,user,"compras","proveedor","dar_de_baja",registro_id=proveedor_id,registro_codigo=current["codigo"],
              datos_antes={"estado":current["estado"]},datos_despues={"estado":"INACTIVO"})
    db.commit(); return {"id":proveedor_id,"estado":"INACTIVO","msg":"Proveedor dado de baja; su historial se conserva"}


@router.post("/proveedores/{proveedor_id}/activar")
def activate_supplier(proveedor_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","editar"))):
    current=db.execute(text("SELECT id,codigo,nombre,estado FROM proveedor WHERE id=:id"),{"id":proveedor_id}).mappings().first()
    if not current: raise HTTPException(404,"No se encontró el proveedor")
    if current["estado"]=="ACTIVO": return {"id":proveedor_id,"estado":"ACTIVO","msg":"El proveedor ya estaba activo"}
    db.execute(text("UPDATE proveedor SET estado='ACTIVO' WHERE id=:id"),{"id":proveedor_id})
    registrar(db,user,"compras","proveedor","reactivar",registro_id=proveedor_id,registro_codigo=current["codigo"],
              datos_antes={"estado":current["estado"]},datos_despues={"estado":"ACTIVO"})
    db.commit(); return {"id":proveedor_id,"estado":"ACTIVO","msg":"Proveedor reactivado"}


@router.get("/compras")
def purchases(db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","ver"))):
    rows=db.execute(text("""SELECT c.id,c.numero,c.tipo_doc,c.fecha,c.proveedor_id,p.nombre proveedor,c.sucursal_id,c.periodo_id,c.estado,c.asiento_id,
      COALESCE(SUM(d.cantidad*d.precio_unitario),0) subtotal,
      ROUND(COALESCE(SUM(CASE WHEN d.tipo_iva='GRAVADA' THEN d.cantidad*d.precio_unitario ELSE 0 END),0)*0.13,2) iva,
      COALESCE(SUM(d.cantidad*d.precio_unitario),0)+ROUND(COALESCE(SUM(CASE WHEN d.tipo_iva='GRAVADA' THEN d.cantidad*d.precio_unitario ELSE 0 END),0)*0.13,2) total
      FROM compra c JOIN proveedor p ON p.id=c.proveedor_id
      LEFT JOIN compra_detalle d ON d.compra_id=c.id GROUP BY c.id,p.nombre ORDER BY c.fecha DESC,c.id DESC""")).mappings().all()
    return {"compras":[dict(r) for r in rows]}


@router.post("/compras",status_code=201)
def create_purchase(data:PurchaseIn,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","crear"))):
    if data.tipo_doc not in ("CCF","FCON","TICKET"): raise HTTPException(400,"Tipo de documento no admitido")
    check_period(db,data.periodo_id,data.fecha)
    if not db.execute(text("SELECT 1 FROM proveedor WHERE id=:i AND estado='ACTIVO'"),{"i":data.proveedor_id}).first(): raise HTTPException(400,"Proveedor inexistente o inactivo")
    if not db.execute(text("SELECT 1 FROM sucursal WHERE id=:i"),{"i":data.sucursal_id}).first(): raise HTTPException(400,"Sucursal inexistente")
    if data.numero:
        numero=data.numero
    else:
        year=data.fecha.year
        db.execute(text("LOCK TABLE compra IN EXCLUSIVE MODE"))
        siguiente=db.execute(text("""SELECT COALESCE(MAX(substring(numero from 11)::integer),0)+1
            FROM compra WHERE numero ~ :pattern"""),{"pattern":rf"^COMP-{year}-[0-9]{{4,6}}$"}).scalar_one()
        if siguiente>999999: raise HTTPException(409,f"Se agotaron los correlativos internos de compras para {year}")
        numero=f"COMP-{year}-{int(siguiente):04d}"
    if db.execute(text("SELECT 1 FROM compra WHERE numero=:n"),{"n":numero}).first(): raise HTTPException(409,"El número de documento ya existe; verifica el correlativo ingresado")
    for line in data.detalles: check_leaf_account(db,line.cuenta_codigo,"Activo o gasto")
    try:
        cid=db.execute(text("INSERT INTO compra(numero,tipo_doc,fecha,proveedor_id,sucursal_id,periodo_id,estado,creado_por) VALUES(:n,:t,:f,:p,:s,:r,'BORRADOR',:u) RETURNING id"),
        {"n":numero,"t":data.tipo_doc,"f":data.fecha,"p":data.proveedor_id,"s":data.sucursal_id,"r":data.periodo_id,"u":user.id}).scalar_one()
        for line in data.detalles: db.execute(text("INSERT INTO compra_detalle(compra_id,descripcion,cantidad,precio_unitario,cuenta_activo_codigo,tipo_iva) VALUES(:c,:d,:q,:p,:a,:iva)"),{"c":cid,"d":line.descripcion.strip(),"q":line.cantidad,"p":line.precio_unitario,"a":line.cuenta_codigo,"iva":line.tipo_iva})
        registrar(db,user,"compras","compra","crear",registro_id=cid,registro_codigo=numero,datos_despues={"estado":"BORRADOR","tipo":data.tipo_doc}); db.commit()
    except Exception:
        db.rollback(); raise
    return {"id":cid,"numero":numero,"estado":"BORRADOR","msg":"Compra guardada en borrador"}


@router.post("/compras/{doc_id}/enviar")
def send_purchase(doc_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("compras","aprobar"))):
    doc=db.execute(text("SELECT c.*,p.cuenta_codigo FROM compra c JOIN proveedor p ON p.id=c.proveedor_id WHERE c.id=:i FOR UPDATE"),{"i":doc_id}).mappings().first()
    if not doc: raise HTTPException(404,"Compra no encontrada")
    if doc["estado"]!="BORRADOR": raise HTTPException(409,"Solo se envían compras en borrador")
    lines=db.execute(text("SELECT descripcion,cantidad,precio_unitario,cuenta_activo_codigo,tipo_iva FROM compra_detalle WHERE compra_id=:i ORDER BY id"),{"i":doc_id}).mappings().all()
    if not lines: raise HTTPException(400,"La compra debe incluir detalles")
    subtotal=money(sum((money(x["cantidad"]*x["precio_unitario"]) for x in lines),Decimal(0)))
    base_gravada=money(sum((money(x["cantidad"]*x["precio_unitario"]) for x in lines if x["tipo_iva"]=="GRAVADA"),Decimal(0)))
    iva=money(base_gravada*IVA); total=subtotal+iva
    journal=[{"cuenta_codigo":x["cuenta_activo_codigo"],"debe":money(x["cantidad"]*x["precio_unitario"]),"haber":0,"descripcion":x["descripcion"]} for x in lines]
    if iva>0: journal.append({"cuenta_codigo":"1.1.8.01","debe":iva,"haber":0,"descripcion":"IVA crédito fiscal 13%"})
    journal.append({"cuenta_codigo":doc["cuenta_codigo"] or "2.1.1.01","debe":0,"haber":total,"descripcion":f"Proveedor {doc['numero']}"})
    try:
        jid,jcode=create_pending_journal(db,user,day=doc["fecha"],concept=f"Compra {doc['numero']} - {doc['tipo_doc']}",period_id=doc["periodo_id"],branch_id=doc["sucursal_id"],lines=journal,module="compras",doc_id=doc_id,doc_code=doc["numero"])
        db.execute(text("UPDATE compra SET estado='PENDIENTE',asiento_id=:a,aprobado_por=:u,aprobado_en=:d WHERE id=:i"),{"a":jid,"u":user.id,"d":datetime.utcnow(),"i":doc_id}); db.commit()
    except Exception:
        db.rollback(); raise
    return {"estado":"PENDIENTE","asiento_id":jid,"asiento_codigo":jcode,"subtotal":str(subtotal),"iva":str(iva),"total":str(total),"msg":"Compra enviada; falta aprobar el asiento en Control"}


@router.get("/empleados")
def employees(db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","ver"))):
    rows=db.execute(text("SELECT id,codigo,nombres,apellidos,dui,nit,cargo,salario_base,fecha_ingreso,sucursal_id,estado FROM empleado ORDER BY apellidos,nombres")).mappings().all()
    return {"empleados":[dict(r) for r in rows]}


@router.get("/cargos-empleado")
def employee_positions(db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","ver"))):
    rows=db.execute(text("SELECT codigo,nombre FROM cargo_empleado WHERE activo=TRUE ORDER BY orden,nombre")).mappings().all()
    return {"cargos":[dict(r) for r in rows]}


@router.post("/empleados",status_code=201)
def create_employee(data:EmployeeIn,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","crear"))):
    if not db.execute(text("SELECT 1 FROM sucursal WHERE id=:id"), {"id": data.sucursal_id}).first():
        raise HTTPException(400, "Selecciona una sucursal válida para el empleado")
    dui_digits = re.sub(r"\D", "", data.dui)
    nit_digits = re.sub(r"\D", "", data.nit or "")
    if db.execute(text("SELECT 1 FROM empleado WHERE regexp_replace(dui, '[^0-9]', '', 'g')=:dui"), {"dui": dui_digits}).first():
        raise HTTPException(409, "Ese DUI ya está registrado en otro empleado")
    if nit_digits and db.execute(text("SELECT 1 FROM empleado WHERE NULLIF(regexp_replace(nit, '[^0-9]', '', 'g'), '')=:nit"), {"nit": nit_digits}).first():
        raise HTTPException(409, "Ese NIT ya está registrado en otro empleado")
    code = data.codigo
    if not code:
        db.execute(text("LOCK TABLE empleado IN EXCLUSIVE MODE"))
        next_number = db.execute(text("SELECT COALESCE(MAX(substring(codigo from 5)::integer),0)+1 FROM empleado WHERE codigo ~ '^EMP-[0-9]{3,6}$'")).scalar_one()
        if next_number > 999999:
            raise HTTPException(409, "No se pudo generar el código automático: se alcanzó el límite de empleados EMP-999999.")
        code = f"EMP-{next_number:03d}"
    if db.execute(text("SELECT 1 FROM empleado WHERE codigo=:c"),{"c":code}).first(): raise HTTPException(409,"El código del empleado ya está registrado")
    result=db.execute(text("""INSERT INTO empleado(codigo,nombres,apellidos,dui,nit,cargo,salario_base,fecha_ingreso,sucursal_id,estado)
      VALUES(:codigo,:nombres,:apellidos,:dui,:nit,:cargo,:salario,:fecha,:sucursal,'ACTIVO') RETURNING id"""),
      {"codigo":code,"nombres":data.nombres.strip(),"apellidos":data.apellidos.strip(),"dui":data.dui,"nit":data.nit,"cargo":data.cargo,"salario":data.salario_base,"fecha":data.fecha_ingreso,"sucursal":data.sucursal_id}).mappings().first()
    after = data.model_dump(mode="json")
    after["codigo"] = code
    registrar(db,user,"planilla","empleado","crear",registro_id=result["id"],registro_codigo=code,datos_despues=after); db.commit()
    return {"id":result["id"],"codigo":code,"msg":"Empleado creado"}


@router.put("/empleados/{employee_id}")
def update_employee(employee_id:int,data:EmployeeIn,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","editar"))):
    current=db.execute(text("SELECT * FROM empleado WHERE id=:id"),{"id":employee_id}).mappings().first()
    if not current:
        raise HTTPException(404,"No se encontró el empleado")
    if not db.execute(text("SELECT 1 FROM sucursal WHERE id=:id"), {"id": data.sucursal_id}).first():
        raise HTTPException(400, "Selecciona una sucursal válida para el empleado")
    dui_digits = re.sub(r"\D", "", data.dui)
    nit_digits = re.sub(r"\D", "", data.nit or "")
    if db.execute(text("SELECT 1 FROM empleado WHERE id<>:id AND regexp_replace(dui, '[^0-9]', '', 'g')=:dui"), {"id": employee_id, "dui": dui_digits}).first():
        raise HTTPException(409, "Ese DUI ya está registrado en otro empleado")
    if nit_digits and db.execute(text("SELECT 1 FROM empleado WHERE id<>:id AND NULLIF(regexp_replace(nit, '[^0-9]', '', 'g'), '')=:nit"), {"id": employee_id, "nit": nit_digits}).first():
        raise HTTPException(409, "Ese NIT ya está registrado en otro empleado")
    code=data.codigo or current["codigo"]
    duplicate=db.execute(text("SELECT 1 FROM empleado WHERE id<>:id AND codigo=:codigo"),{"id":employee_id,"codigo":code}).first()
    if duplicate:
        raise HTTPException(409,"El código ya pertenece a otro empleado")
    before={k:current[k] for k in ("codigo","nombres","apellidos","dui","nit","cargo","salario_base","fecha_ingreso","sucursal_id","estado")}
    db.execute(text("""UPDATE empleado SET codigo=:codigo,nombres=:nombres,apellidos=:apellidos,dui=:dui,nit=:nit,cargo=:cargo,
      salario_base=:salario,fecha_ingreso=:fecha,sucursal_id=:sucursal WHERE id=:id"""),
      {"id":employee_id,"codigo":code,"nombres":data.nombres,"apellidos":data.apellidos,"dui":data.dui,"nit":data.nit,
       "cargo":data.cargo,"salario":data.salario_base,"fecha":data.fecha_ingreso,"sucursal":data.sucursal_id})
    after=data.model_dump(mode="json");after["codigo"]=code;after["estado"]=current["estado"]
    registrar(db,user,"planilla","empleado","editar",registro_id=employee_id,registro_codigo=code,
      datos_antes={k:str(v) if v is not None else None for k,v in before.items()},datos_despues=after)
    db.commit()
    return {"id":employee_id,"codigo":code,"msg":"Empleado actualizado"}


@router.delete("/empleados/{employee_id}")
def deactivate_employee(employee_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","editar"))):
    current=db.execute(text("SELECT id,codigo,estado FROM empleado WHERE id=:id"),{"id":employee_id}).mappings().first()
    if not current:
        raise HTTPException(404,"No se encontró el empleado")
    if current["estado"]=="INACTIVO":
        return {"id":employee_id,"estado":"INACTIVO","msg":"El empleado ya estaba desactivado"}
    db.execute(text("UPDATE empleado SET estado='INACTIVO' WHERE id=:id"),{"id":employee_id})
    registrar(db,user,"planilla","empleado","desactivar",registro_id=employee_id,registro_codigo=current["codigo"],
      datos_antes={"estado":current["estado"]},datos_despues={"estado":"INACTIVO"})
    db.commit()
    return {"id":employee_id,"estado":"INACTIVO","msg":"Empleado desactivado; se conserva su historial de planillas"}


@router.post("/empleados/{employee_id}/activar")
def activate_employee(employee_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","editar"))):
    current=db.execute(text("SELECT id,codigo,estado FROM empleado WHERE id=:id"),{"id":employee_id}).mappings().first()
    if not current:
        raise HTTPException(404,"No se encontró el empleado")
    db.execute(text("UPDATE empleado SET estado='ACTIVO' WHERE id=:id"),{"id":employee_id})
    registrar(db,user,"planilla","empleado","activar",registro_id=employee_id,registro_codigo=current["codigo"],
      datos_antes={"estado":current["estado"]},datos_despues={"estado":"ACTIVO"})
    db.commit()
    return {"id":employee_id,"estado":"ACTIVO","msg":"Empleado reactivado"}


@router.get("/planillas")
def payrolls(db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","ver"))):
    rows=db.execute(text("""SELECT p.id,p.codigo,p.periodo,p.fecha_pago,p.sucursal_id,p.tipo,p.estado,p.asiento_id,p.periodo_id,
      COUNT(d.id) empleados,COALESCE(SUM(d.salario_base*d.dias_trabajados/30+d.horas_extra+d.bonificaciones+d.comisiones),0) bruto,
      COALESCE(SUM(d.deduccion_isss+d.deduccion_afp+d.deduccion_renta+d.otras_deducciones),0) deducciones,
      COALESCE(SUM(d.isss_patronal+d.afp_patronal),0) aportes_patronales,
      COALESCE(SUM(d.salario_base*d.dias_trabajados/30+d.horas_extra+d.bonificaciones+d.comisiones-d.deduccion_isss-d.deduccion_afp-d.deduccion_renta-d.otras_deducciones),0) liquido
      FROM planilla p LEFT JOIN planilla_detalle d ON d.planilla_id=p.id GROUP BY p.id ORDER BY p.periodo DESC,p.id DESC""")).mappings().all()
    return {"planillas":[dict(r) for r in rows]}


@router.get("/planillas/{doc_id}")
def payroll_detail(doc_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","ver"))):
    doc=db.execute(text("SELECT id,codigo,periodo,fecha_pago,estado,asiento_id,periodo_id FROM planilla WHERE id=:i"),{"i":doc_id}).mappings().first()
    if not doc: raise HTTPException(404,"Planilla no encontrada")
    rows=db.execute(text("""SELECT e.codigo,e.nombres,e.apellidos,e.cargo,d.dias_trabajados,d.salario_base,
      d.horas_extra,d.bonificaciones,d.comisiones,d.deduccion_isss,d.deduccion_afp,d.deduccion_renta,d.otras_deducciones,
      d.cuenta_gasto_codigo,d.isss_patronal,d.afp_patronal,
      (d.salario_base*d.dias_trabajados/30+d.horas_extra+d.bonificaciones+d.comisiones) bruto,
      (d.deduccion_isss+d.deduccion_afp+d.deduccion_renta+d.otras_deducciones) deducciones,
      (d.salario_base*d.dias_trabajados/30+d.horas_extra+d.bonificaciones+d.comisiones-d.deduccion_isss-d.deduccion_afp-d.deduccion_renta-d.otras_deducciones) liquido
      FROM planilla_detalle d JOIN empleado e ON e.id=d.empleado_id WHERE d.planilla_id=:i ORDER BY e.apellidos,e.nombres"""),{"i":doc_id}).mappings().all()
    return {"planilla":dict(doc),"detalles":[dict(r) for r in rows]}


@router.post("/planillas",status_code=201)
def create_payroll(data:PayrollIn,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","crear"))):
    check_period(db,data.periodo_id,data.fecha_pago)
    if data.periodo != data.fecha_pago.strftime("%Y-%m"): raise HTTPException(400,"El período YYYY-MM debe coincidir con la fecha de pago")
    ids=[x.empleado_id for x in data.detalles]
    if len(ids)!=len(set(ids)): raise HTTPException(400,"No repita empleados en la misma planilla")
    by_id={}
    for employee_id in ids:
        employee_row=db.execute(text("SELECT id,salario_base FROM empleado WHERE id=:id AND estado='ACTIVO'"),{"id":employee_id}).mappings().first()
        if not employee_row: raise HTTPException(400,"Uno o más empleados no existen o están inactivos")
        by_id[employee_id]=employee_row
    for line in data.detalles:
        if line.cuenta_gasto_codigo not in ("4.1.1.09", "4.1.3.01", "4.1.4.01"):
            raise HTTPException(400,"Seleccione una cuenta de gasto permitida: personal técnico, administración o ventas")
        check_leaf_account(db,line.cuenta_gasto_codigo,"Gasto de planilla")
    code=(data.codigo or f"PL-{data.periodo.replace('-','')}-{int(db.execute(text('SELECT COALESCE(MAX(id),0)+1 FROM planilla')).scalar_one()):04d}").strip()
    if db.execute(text("SELECT 1 FROM planilla WHERE codigo=:c"),{"c":code}).first(): raise HTTPException(409,"El código de planilla ya existe")
    try:
        pid=db.execute(text("INSERT INTO planilla(codigo,periodo,fecha_pago,sucursal_id,tipo,estado,periodo_id,creado_por) VALUES(:c,:p,:f,:s,'MENSUAL','BORRADOR',:r,:u) RETURNING id"),
          {"c":code,"p":data.periodo,"f":data.fecha_pago,"s":data.sucursal_id,"r":data.periodo_id,"u":user.id}).scalar_one()
        for line in data.detalles:
            gross=money(Decimal(str(by_id[line.empleado_id]["salario_base"]))*line.dias_trabajados/30 + line.horas_extra + line.bonificaciones + line.comisiones)
            deductions=sum((money(getattr(line,k)) for k in ("deduccion_isss","deduccion_afp","deduccion_renta","otras_deducciones")),Decimal(0))
            if line.isss_patronal or line.afp_patronal:
                check_leaf_account(db,"2.1.5.01","ISSS patronal por pagar")
                check_leaf_account(db,"2.1.5.02","AFP patronal por pagar")
            if deductions>gross: raise HTTPException(400,f"Las deducciones exceden el salario de empleado {line.empleado_id}")
            db.execute(text("""INSERT INTO planilla_detalle(planilla_id,empleado_id,dias_trabajados,salario_base,horas_extra,bonificaciones,comisiones,deduccion_isss,deduccion_afp,deduccion_renta,otras_deducciones,cuenta_gasto_codigo,isss_patronal,afp_patronal)
              VALUES(:p,:e,:d,:s,:h,:b,:c,:i,:a,:r,:o,:g,:ip,:ap)"""),{"p":pid,"e":line.empleado_id,"d":line.dias_trabajados,"s":by_id[line.empleado_id]["salario_base"],"h":line.horas_extra,"b":line.bonificaciones,"c":line.comisiones,"i":line.deduccion_isss,"a":line.deduccion_afp,"r":line.deduccion_renta,"o":line.otras_deducciones,"g":line.cuenta_gasto_codigo,"ip":line.isss_patronal,"ap":line.afp_patronal})
        registrar(db,user,"planilla","planilla","crear",registro_id=pid,registro_codigo=code,datos_despues={"estado":"BORRADOR","periodo":data.periodo,"empleados":len(ids)}); db.commit()
    except Exception:
        db.rollback(); raise
    return {"id":pid,"codigo":code,"estado":"BORRADOR","msg":"Planilla guardada en borrador"}


@router.post("/planillas/{doc_id}/enviar")
def send_payroll(doc_id:int,db:Session=Depends(get_db),user:Usuario=Depends(require_permission("planilla","aprobar"))):
    doc=db.execute(text("SELECT * FROM planilla WHERE id=:i FOR UPDATE"),{"i":doc_id}).mappings().first()
    if not doc: raise HTTPException(404,"Planilla no encontrada")
    if doc["estado"]!="BORRADOR": raise HTTPException(409,"Solo se envían planillas en borrador")
    details=db.execute(text("""SELECT e.codigo,e.nombres,e.apellidos,d.salario_base,d.dias_trabajados,d.horas_extra,d.bonificaciones,d.comisiones,
      d.deduccion_isss,d.deduccion_afp,d.deduccion_renta,d.otras_deducciones,d.cuenta_gasto_codigo,d.isss_patronal,d.afp_patronal
      FROM planilla_detalle d JOIN empleado e ON e.id=d.empleado_id WHERE d.planilla_id=:i ORDER BY e.apellidos,e.nombres"""),{"i":doc_id}).mappings().all()
    if not details: raise HTTPException(400,"La planilla no tiene empleados")
    gross=Decimal(0); isss=Decimal(0); afp=Decimal(0); renta=Decimal(0); other=Decimal(0); isss_patronal=Decimal(0); afp_patronal=Decimal(0)
    expense_by_account={}
    for d in details:
        line_gross=money(Decimal(str(d["salario_base"]))*d["dias_trabajados"]/30+d["horas_extra"]+d["bonificaciones"]+d["comisiones"])
        gross+=line_gross
        non_commission=money(Decimal(str(d["salario_base"]))*d["dias_trabajados"]/30+d["horas_extra"]+d["bonificaciones"])
        expense_by_account[d["cuenta_gasto_codigo"]]=expense_by_account.get(d["cuenta_gasto_codigo"],Decimal(0))+non_commission+money(d["isss_patronal"])+money(d["afp_patronal"])
        if money(d["comisiones"]):
            check_leaf_account(db,"4.1.4.02","Gasto de comisiones")
            expense_by_account["4.1.4.02"]=expense_by_account.get("4.1.4.02",Decimal(0))+money(d["comisiones"])
        isss+=money(d["deduccion_isss"]); afp+=money(d["deduccion_afp"]); renta+=money(d["deduccion_renta"]); other+=money(d["otras_deducciones"])
        isss_patronal+=money(d["isss_patronal"]); afp_patronal+=money(d["afp_patronal"])
    gross=money(gross); isss=money(isss); afp=money(afp); renta=money(renta); other=money(other); isss_patronal=money(isss_patronal); afp_patronal=money(afp_patronal); net=gross-isss-afp-renta-other
    journal=[{"cuenta_codigo":code,"debe":money(amount),"haber":0,"descripcion":f"Salarios y aportes patronales {doc['periodo']}"} for code,amount in expense_by_account.items() if amount]
    for code,amount,label in (("2.1.3.02",isss+afp,"Retenciones ISSS/AFP"),("2.1.3.01",renta,"Retención renta"),("2.1.3.03",other,"Otras deducciones"),("2.1.4.03",net,"Salario líquido por pagar")):
        if amount: journal.append({"cuenta_codigo":code,"debe":0,"haber":amount,"descripcion":label})
    for code,amount,label in (("2.1.5.01",isss_patronal,"ISSS patronal por pagar"),("2.1.5.02",afp_patronal,"AFP patronal por pagar")):
        if amount: journal.append({"cuenta_codigo":code,"debe":0,"haber":amount,"descripcion":label})
    try:
        jid,jcode=create_pending_journal(db,user,day=doc["fecha_pago"],concept=f"Planilla {doc['codigo']} - {doc['periodo']}",period_id=doc["periodo_id"],branch_id=doc["sucursal_id"],lines=journal,module="planilla",doc_id=doc_id,doc_code=doc["codigo"])
        db.execute(text("UPDATE planilla SET estado='APROBADA',asiento_id=:a,aprobado_por=:u,aprobado_en=:d WHERE id=:i"),{"a":jid,"u":user.id,"d":datetime.utcnow(),"i":doc_id}); db.commit()
    except Exception:
        db.rollback(); raise
    return {"estado":"APROBADA","asiento_id":jid,"asiento_codigo":jcode,"bruto":str(gross),"deducciones":str(isss+afp+renta+other),"aportes_patronales":str(isss_patronal+afp_patronal),"liquido":str(net),"msg":"Planilla enviada; falta aprobar el asiento en Control"}


@router.post("/planillas/{doc_id}/pagar")
def pay_payroll(doc_id: int, data: PayrollPaymentIn, db: Session = Depends(get_db),
                user: Usuario = Depends(require_permission("planilla", "pagar"))):
    if not db.execute(text("SELECT to_regclass('public.planilla_pago')")).scalar():
        raise HTTPException(
            503,
            "Falta instalar la migración de pagos de planilla. Desde la carpeta del proyecto, ejecute db/003_planilla_pagos.sql y reinicie el backend.",
        )
    doc = db.execute(text("SELECT * FROM planilla WHERE id=:i FOR UPDATE"), {"i": doc_id}).mappings().first()
    if not doc:
        raise HTTPException(404, "Planilla no encontrada")
    if doc["estado"] != "CONTABILIZADA":
        raise HTTPException(409, "Solo se puede pagar una planilla ya contabilizada")
    if db.execute(text("SELECT 1 FROM planilla_pago WHERE planilla_id=:i AND estado IN ('PENDIENTE','PAGADA')"), {"i": doc_id}).first():
        raise HTTPException(409, "Esta planilla ya tiene un pago registrado")
    check_period(db, data.periodo_id, data.fecha_pago)
    if not doc["periodo"].startswith(data.fecha_pago.strftime("%Y-%m")):
        raise HTTPException(400, "La fecha del pago debe estar dentro del mes de la planilla")
    if not data.cuenta_pago_codigo.startswith(("1.1.1.", "1.1.2.")):
        raise HTTPException(400, "Seleccione una cuenta hoja de caja o bancos")
    check_leaf_account(db, data.cuenta_pago_codigo, "Cuenta de pago")
    details = db.execute(text("""SELECT salario_base,dias_trabajados,horas_extra,bonificaciones,comisiones,
      deduccion_isss,deduccion_afp,deduccion_renta,otras_deducciones FROM planilla_detalle WHERE planilla_id=:i"""),
      {"i": doc_id}).mappings().all()
    gross = money(sum((money(Decimal(str(x["salario_base"])) * x["dias_trabajados"] / 30 + x["horas_extra"] + x["bonificaciones"] + x["comisiones"]) for x in details), Decimal(0)))
    deductions = money(sum((money(x["deduccion_isss"] + x["deduccion_afp"] + x["deduccion_renta"] + x["otras_deducciones"]) for x in details), Decimal(0)))
    net = gross - deductions
    if net <= 0:
        raise HTTPException(400, "El líquido a pagar debe ser mayor que cero")
    try:
        jid, jcode = create_pending_journal(
            db, user, day=data.fecha_pago, concept=f"Pago de planilla {doc['codigo']} - {doc['periodo']}",
            period_id=data.periodo_id, branch_id=doc["sucursal_id"],
            lines=[
                {"cuenta_codigo": "2.1.4.03", "debe": net, "haber": 0, "descripcion": f"Pago salarios {doc['periodo']}"},
                {"cuenta_codigo": data.cuenta_pago_codigo, "debe": 0, "haber": net, "descripcion": f"Desembolso planilla {doc['codigo']}"},
            ], module="planilla", doc_id=doc_id, doc_code=doc["codigo"],
        )
        db.execute(text("""INSERT INTO planilla_pago
          (planilla_id,asiento_id,fecha_pago,periodo_id,cuenta_pago_codigo,monto,creado_por)
          VALUES(:p,:a,:f,:r,:c,:m,:u)"""),
          {"p": doc_id, "a": jid, "f": data.fecha_pago, "r": data.periodo_id,
           "c": data.cuenta_pago_codigo, "m": net, "u": user.id})
        registrar(db, user, "planilla", "planilla_pago", "enviar_a_aprobacion",
                  registro_id=doc_id, registro_codigo=doc["codigo"],
                  datos_despues={"estado": "PENDIENTE", "monto": str(net), "asiento_id": jid})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"estado": "PENDIENTE", "asiento_id": jid, "asiento_codigo": jcode,
            "monto": str(net), "msg": "Pago enviado; falta aprobar el asiento de desembolso en Control"}
