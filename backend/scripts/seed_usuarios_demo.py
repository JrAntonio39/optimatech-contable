"""
Crea un usuario de demostración por cada rol, para poder probar la matriz de
permisos sin crear cuentas a mano.

Uso:
    python3 -m scripts.seed_usuarios_demo

Contraseña de todos: Demo1234  (cámbiala en el primer inicio de sesión)
"""

from app.database import SessionLocal
from app.models.auth import Usuario, Rol
from app.routers.auth import hash_password

PASSWORD = "Demo1234"

USUARIOS = [
    ("contador", "Contador Demo", "contador@optimatech.com"),
    ("auxiliar", "Auxiliar Demo", "auxiliar@optimatech.com"),
    ("ventas", "Ventas Demo", "ventas@optimatech.com"),
    ("compras", "Compras Demo", "compras@optimatech.com"),
    ("planilla", "Planilla Demo", "planilla@optimatech.com"),
    ("auditor", "Auditor Demo", "auditor@optimatech.com"),
]


def main():
    db = SessionLocal()
    try:
        for username, nombre, email in USUARIOS:
            rol = db.query(Rol).filter_by(codigo=username).first()
            if not rol:
                print(f"  ! Falta el rol '{username}'. Ejecuta: python3 -m scripts.seed_permisos")
                continue
            u = db.query(Usuario).filter_by(username=username).first()
            if u:
                u.password_hash = hash_password(PASSWORD)
                u.activo = True
                u.nombre_completo = nombre
                u.roles = [rol]
                print(f"  {username:10} -> actualizado")
            else:
                u = Usuario(
                    username=username,
                    email=email,
                    nombre_completo=nombre,
                    password_hash=hash_password(PASSWORD),
                    activo=True,
                )
                u.roles = [rol]
                db.add(u)
                print(f"  {username:10} -> creado")
        db.commit()
        print(f"\nUsuarios demo listos. Contraseña: {PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
