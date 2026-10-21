"""
Crea la tabla de auditoría (bitácora) y sus índices.

Uso: python3 -m scripts.crear_auditoria
"""

from app.database import Base, engine
from app.models.auditoria import Auditoria  # noqa: F401  (registra la tabla)


def main():
    Base.metadata.create_all(bind=engine)
    print("Tabla 'auditoria' creada/actualizada.")


if __name__ == "__main__":
    main()
