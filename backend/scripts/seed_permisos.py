"""
Catálogo de permisos y matriz de roles de OptimaTech.

Uso:
    python3 -m scripts.seed_permisos          # aplica permisos + matriz
    python3 -m scripts.seed_permisos --show   # solo muestra la matriz

Es idempotente: se puede volver a ejecutar sin duplicar nada.
Los permisos se nombran "modulo.accion" (ej: asientos.aprobar, periodos.cerrar).
"""

import sys
from app.database import SessionLocal
from app.models.auth import Rol, Permiso

# --------------------------------------------------------------------------
# 1. CATÁLOGO DE PERMISOS POR ACCIÓN
#    (modulo, accion) -> descripción
# --------------------------------------------------------------------------
PERMISOS = {
    # Catálogo de cuentas
    ("cuentas", "ver"): "Ver el catálogo de cuentas",
    ("cuentas", "crear"): "Agregar cuentas al catálogo",
    ("cuentas", "editar"): "Modificar cuentas del catálogo",
    ("cuentas", "eliminar"): "Eliminar cuentas del catálogo",
    # Asientos (libro diario)
    ("asientos", "ver"): "Ver asientos y libro diario",
    ("asientos", "crear"): "Registrar asientos contables",
    ("asientos", "editar"): "Modificar asientos en borrador",
    ("asientos", "eliminar"): "Eliminar asientos en borrador",
    ("asientos", "aprobar"): "Aprobar asientos para contabilizar",
    ("asientos", "anular"): "Anular asientos contabilizados",
    # Períodos contables
    ("periodos", "ver"): "Ver períodos contables",
    ("periodos", "crear"): "Abrir nuevos períodos",
    ("periodos", "editar"): "Modificar datos de períodos",
    ("periodos", "cerrar"): "Cerrar períodos contables",
    # Sucursales
    ("sucursales", "ver"): "Ver sucursales",
    ("sucursales", "crear"): "Crear sucursales",
    ("sucursales", "editar"): "Editar sucursales",
    # Facturación electrónica
    ("facturas", "ver"): "Ver facturas",
    ("facturas", "crear"): "Emitir facturas electrónicas",
    ("facturas", "editar"): "Editar facturas en borrador",
    ("facturas", "eliminar"): "Eliminar facturas en borrador sin asiento contable",
    ("facturas", "aprobar"): "Aprobar facturas para contabilizar",
    ("facturas", "anular"): "Anular facturas emitidas",
    # Libro de compras
    ("compras", "ver"): "Ver compras y proveedores",
    ("compras", "crear"): "Registrar compras",
    ("compras", "editar"): "Editar compras en borrador",
    ("compras", "aprobar"): "Aprobar compras para contabilizar",
    # Pago de salarios
    ("planilla", "ver"): "Ver planilla de salarios",
    ("planilla", "crear"): "Crear planilla de salarios",
    ("planilla", "editar"): "Editar planilla de salarios",
    ("planilla", "aprobar"): "Aprobar planilla para contabilizar",
    ("planilla", "pagar"): "Registrar pago de planillas ya contabilizadas",
    # Reportes
    ("reportes", "ver"): "Ver reportes contables",
    ("reportes", "crear"): "Exportar reportes",
    # Administración de usuarios y auditoría
    ("usuarios", "ver"): "Ver usuarios del sistema",
    ("usuarios", "crear"): "Crear usuarios",
    ("usuarios", "editar"): "Editar usuarios y roles",
    ("usuarios", "eliminar"): "Desactivar usuarios",
    ("auditoria", "ver"): "Ver bitácora de auditoría",
}

# --------------------------------------------------------------------------
# 2. MATRIZ DE ROLES
#    Cada rol declara los permisos que puede ejercer.
# --------------------------------------------------------------------------
MATRIZ_ROLES = {
    "admin": {
        "nombre": "Administrador",
        "descripcion": "Acceso total al sistema, incluida la administración de usuarios",
        "todos": True,  # se le asignan todos los permisos del catálogo
    },
    "contador": {
        "nombre": "Contador",
        "descripcion": "Gestión contable completa: catálogo, asientos, períodos y reportes",
        "todos": False,
        "permisos": [
            "cuentas.ver", "cuentas.crear",
            "asientos.ver", "asientos.crear",
            "asientos.eliminar", "asientos.aprobar", "asientos.anular",
            "periodos.ver", "periodos.crear", "periodos.editar", "periodos.cerrar",
            "sucursales.ver", "sucursales.crear", "sucursales.editar",
            "reportes.ver", "reportes.crear",
            "auditoria.ver",
            "facturas.ver", "compras.ver", "planilla.ver", "planilla.pagar",
        ],
    },
    "auxiliar": {
        "nombre": "Auxiliar Contable",
        "descripcion": "Registra operaciones y consulta catálogos; no aprueba ni cierra",
        "todos": False,
        "permisos": [
            "cuentas.ver",
            "asientos.ver", "asientos.crear",
            "periodos.ver", "sucursales.ver",
            "reportes.ver",
        ],
    },
    "ventas": {
        "nombre": "Ventas",
        "descripcion": "Gestiona clientes y facturas; no consulta reportes contables ni administra asientos",
        "todos": False,
        "permisos": [
            "cuentas.ver", "periodos.ver", "sucursales.ver",
            "facturas.ver", "facturas.crear", "facturas.editar",
            "facturas.eliminar", "facturas.aprobar",
        ],
    },
    "compras": {
        "nombre": "Compras",
        "descripcion": "Gestiona proveedores y compras; no consulta reportes contables ni administra asientos",
        "todos": False,
        "permisos": [
            "cuentas.ver", "periodos.ver", "sucursales.ver",
            "compras.ver", "compras.crear", "compras.editar", "compras.aprobar",
        ],
    },
    "planilla": {
        "nombre": "Planilla",
        "descripcion": "Gestiona empleados y planillas; no consulta reportes contables ni administra períodos",
        "todos": False,
        "permisos": [
            "cuentas.ver", "periodos.ver", "sucursales.ver",
            "planilla.ver", "planilla.crear", "planilla.editar", "planilla.aprobar", "planilla.pagar",
        ],
    },
    "auditor": {
        "nombre": "Auditor",
        "descripcion": "Solo lectura sobre todo el sistema, incluida la bitácora de auditoría",
        "todos": False,
        "solo_lectura": True,  # todos los permisos *.ver
    },
}


def aplicar():
    db = SessionLocal()
    try:
        # --- 1. Permisos ---
        creados = 0
        for (modulo, accion), descripcion in PERMISOS.items():
            codigo = f"{modulo}.{accion}"
            p = db.query(Permiso).filter_by(codigo=codigo).first()
            if not p:
                db.add(Permiso(
                    codigo=codigo,
                    nombre=f"{modulo.capitalize()} · {accion.capitalize()}",
                    modulo=modulo,
                    accion=accion,
                    descripcion=descripcion,
                ))
                creados += 1
        db.commit()
        print(f"Permisos: {len(PERMISOS)} en catálogo ({creados} nuevos)")

        # --- 2. Roles y su matriz ---
        for codigo, cfg in MATRIZ_ROLES.items():
            rol = db.query(Rol).filter_by(codigo=codigo).first()
            if not rol:
                rol = Rol(codigo=codigo, nombre=cfg["nombre"], descripcion=cfg["descripcion"])
                db.add(rol)
                db.flush()

            if cfg.get("todos"):
                asignados = db.query(Permiso).all()
            elif cfg.get("solo_lectura"):
                asignados = db.query(Permiso).filter(Permiso.accion == "ver").all()
            else:
                asignados = db.query(Permiso).filter(
                    Permiso.codigo.in_(cfg["permisos"])
                ).all()

            # Reemplaza la asignación completa del rol
            rol.permisos = asignados
            print(f"  Rol {codigo:10} -> {len(asignados)} permisos")

        db.commit()
        print("Matriz de roles aplicada.")
    finally:
        db.close()


def mostrar():
    db = SessionLocal()
    try:
        print("\nMATRIZ DE PERMISOS POR ROL")
        print("=" * 70)
        for codigo, cfg in MATRIZ_ROLES.items():
            rol = db.query(Rol).filter_by(codigo=codigo).first()
            n = len(rol.permisos) if rol else 0
            print(f"\n{codigo} ({cfg['nombre']}) - {n} permisos")
            print(f"  {cfg['descripcion']}")
    finally:
        db.close()


if __name__ == "__main__":
    if "--show" in sys.argv:
        mostrar()
    else:
        aplicar()
        mostrar()
