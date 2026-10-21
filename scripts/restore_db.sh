#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! -f "$1" ]]; then
  echo "Uso: bash scripts/restore_db.sh ruta/al/respaldo.dump" >&2
  exit 2
fi

container="${DB_CONTAINER:-optimatech_db}"
database="${DB_NAME:-optimatech_db}"
echo "Esto reemplazará los objetos existentes en la base '$database'."
read -r -p "Escribe RESTAURAR $database para continuar: " confirmacion
if [[ "$confirmacion" != "RESTAURAR $database" ]]; then
  echo "Restauración cancelada."
  exit 1
fi

docker exec -i "$container" pg_restore -U postgres -d "$database" --clean --if-exists --no-owner --single-transaction < "$1"
echo "Respaldo restaurado en '$database'."
