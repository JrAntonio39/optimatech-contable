"""
Creación segura del primer administrador.

Genera una contraseña aleatoria y la muestra SOLO por pantalla, de modo que
no quede ninguna credencial fija en el código ni en el repositorio.

Uso:
    python3 -m scripts.crear_admin --username admin --nombre "Administrador"

Opciones:
    --email     correo (por defecto admin@optimatech.local)
    --password  contraseña específica (si se omite, se genera aleatoria)

Para crear más usuarios después, usa la API (POST /api/auth/register) con un
usuario administrador ya existente.
"""

import argparse
import secrets
import string
import sys

from app.database import SessionLocal
from app.models.auth import Usuario, Rol
from app.routers.auth import hash_password

# Evita que la contraseña contenga caracteres problemáticos en consola
ALFABETO = string.ascii_letters + string.digits


def generar_password(largo: int = 16) -> str:
    return "".join(secrets.choice(ALFABETO) for _ in range(largo))


def main():
    ap = argparse.ArgumentParser(description="Crea el usuario administrador inicial")
    ap.add_argument("--username", default="admin")
    ap.add_argument("--nombre", default="Administrador")
    ap.add_argument("--email", default="admin@optimatech.com")
    ap.add_argument("--password", default=None, help="Si se omite, se genera una aleatoria")
    ap.add_argument("--reset", action="store_true", help="Restablece la contraseña si el usuario ya existe")
    args = ap.parse_args()

    db = SessionLocal()
    try:
        existente = db.query(Usuario).filter_by(username=args.username).first()
        if existente and not args.reset:
            print(f"El usuario '{args.username}' ya existe. Nada que hacer.")
            print("Usa --reset para regenerar su contraseña.")
            return 1

        rol = db.query(Rol).filter_by(codigo="admin").first()
        if not rol:
            print("No existe el rol 'admin'. Ejecuta primero: python3 -m scripts.seed_permisos")
            return 1

        password = args.password or generar_password()
        autogenerada = args.password is None

        if existente:
            existente.password_hash = hash_password(password)
            existente.activo = True
            db.commit()
            accion = "CONTRASEÑA RESTABLECIDA"
        else:
            user = Usuario(
                username=args.username,
                email=args.email,
                nombre_completo=args.nombre,
                password_hash=hash_password(password),
                activo=True,
            )
            user.roles = [rol]
            db.add(user)
            db.commit()
            accion = "ADMINISTRADOR CREADO"

        print("=" * 58)
        print(f"  {accion}")
        print("=" * 58)
        print(f"  Usuario:     {args.username}")
        print(f"  Email:       {args.email}")
        print(f"  Contraseña:  {password}")
        print(f"  Rol:         admin")
        if autogenerada:
            print("  (generada aleatoriamente: anótala, no se vuelve a mostrar)")
        print("=" * 58)
        print("  Cambia la contraseña después del primer inicio de sesión.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
