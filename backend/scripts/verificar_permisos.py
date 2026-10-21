"""
Verificación del punto 8 del plan: usuarios, inicio de sesión y permisos.

Crea usuarios temporales con distintos roles, inicia sesión con cada uno y
comprueba que la API ACEPTA lo permitido y RECHAZA lo no permitido.

Uso:
    python3 -m scripts.verificar_permisos
"""

import sys
import requests

BASE = "http://localhost:8000"
PASSWORD = "Prueba12345"

# (usuario, rol) -> [(método, ruta, json|None, permitido)]
CASOS = {
    "ventas": [
        ("GET", "/api/cuentas?nivel=3", None, True),
        ("GET", "/api/reportes/balanza", None, True),   # ventas tiene reportes.ver
        ("GET", "/api/asientos", None, False),           # 403: no ve asientos
        ("POST", "/api/asientos", None, False),          # 403: no registra asientos
        ("GET", "/api/auth/usuarios", None, False),      # 403: solo admin
    ],
    "contador": [
        ("GET", "/api/cuentas?nivel=3", None, True),
        ("GET", "/api/reportes/balanza", None, True),
        ("GET", "/api/reportes/resultados", None, True),
        ("GET", "/api/asientos", None, True),
        ("GET", "/api/auth/usuarios", None, False),  # solo admin
    ],
    "auditor": [
        ("GET", "/api/cuentas?nivel=3", None, True),
        ("GET", "/api/reportes/balanza", None, True),
        ("GET", "/api/asientos", None, True),
        ("POST", "/api/cuentas", None, False),
    ],
}


def crear_usuario(username, rol_codigo):
    """Crea el usuario vía la API de admin (necesita token de admin)."""
    from app.database import SessionLocal
    from app.models.auth import Usuario, Rol
    from app.routers.auth import hash_password

    db = SessionLocal()
    try:
        if db.query(Usuario).filter_by(username=username).first():
            u = db.query(Usuario).filter_by(username=username).first()
            u.password_hash = hash_password(PASSWORD)
            u.email = f"{username}@optimatech.com"
            rol = db.query(Rol).filter_by(codigo=rol_codigo).first()
            u.roles = [rol]
            db.commit()
            return
        rol = db.query(Rol).filter_by(codigo=rol_codigo).first()
        if not rol:
            print(f"  ! Rol {rol_codigo} no existe")
            return
        u = Usuario(
            username=username,
            email=f"{username}@optimatech.com",
            nombre_completo=f"Prueba {rol_codigo}",
            password_hash=hash_password(PASSWORD),
            activo=True,
        )
        u.roles = [rol]
        db.add(u)
        db.commit()
    finally:
        db.close()


def main():
    print("=" * 74)
    print("VERIFICACIÓN DE PERMISOS (punto 8 del plan)")
    print("=" * 74)

    # 1. Login de admin
    r = requests.post(f"{BASE}/api/auth/login",
                      data={"username": "admin", "password": "iFa4tCw0nmzHd24d"})
    if r.status_code != 200:
        print(f"! No se pudo iniciar sesión como admin: {r.status_code} {r.text[:200]}")
        print("  (¿cambiaste la contraseña del admin? usa --reset en crear_admin.py)")
        return 1
    admin_token = r.json()["access_token"]
    print(f"\n[1] Login admin: OK ({len(r.json()['usuario']['permiso_codigos'])} permisos)")

    # 2. Crear usuarios de prueba
    print("\n[2] Usuarios de prueba:")
    for username, rol in [("prueba_ventas", "ventas"),
                          ("prueba_contador", "contador"),
                          ("prueba_auditor", "auditor")]:
        crear_usuario(username, rol)
        print(f"  {username} (rol: {rol})")

    # 3. Cada usuario hace login y prueba rutas
    print("\n[3] Pruebas de acceso por rol:")
    fallos = 0
    for username, rol in [("prueba_ventas", "ventas"),
                          ("prueba_contador", "contador"),
                          ("prueba_auditor", "auditor")]:
        r = requests.post(f"{BASE}/api/auth/login",
                          data={"username": username, "password": PASSWORD})
        if r.status_code != 200:
            print(f"  ! login fallido: {username} -> {r.status_code}")
            fallos += 1
            continue
        token = r.json()["access_token"]
        perms = r.json()["usuario"]["permiso_codigos"]
        print(f"\n  --- {username} (rol {rol}) -> {len(perms)} permisos")

        for metodo, ruta, body, permitido in CASOS[rol]:
            h = {"Authorization": f"Bearer {token}"}
            if metodo == "GET":
                resp = requests.get(f"{BASE}{ruta}", headers=h)
            else:
                resp = requests.post(f"{BASE}{ruta}", headers=h, json=body or {})

            if permitido:
                ok = resp.status_code != 403
                detalle = f"HTTP {resp.status_code}"
            else:
                ok = resp.status_code == 403
                detalle = f"HTTP {resp.status_code} (se esperaba 403)"

            marca = "OK  " if ok else "FALLA"
            if not ok:
                fallos += 1
            print(f"    [{marca}] {metodo:4} {ruta:35} {detalle}")

    # 4. Sin token
    print("\n[4] Acceso sin token:")
    resp = requests.get(f"{BASE}/api/cuentas")
    ok = resp.status_code == 401
    if not ok:
        fallos += 1
    print(f"    [{'OK  ' if ok else 'FALLA'}] GET /api/cuentas sin token -> HTTP {resp.status_code} (se esperaba 401)")

    print("\n" + "=" * 74)
    print(f"RESULTADO: {'TODO CORRECTO' if fallos == 0 else f'{fallos} FALLOS'}")
    print("=" * 74)
    return 0 if fallos == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
