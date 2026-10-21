#!/usr/bin/env bash
set -euo pipefail

container="${DB_CONTAINER:-optimatech_db}"
database="${DB_NAME:-optimatech_db}"
backup_dir="${BACKUP_DIR:-./backups}"
mkdir -p "$backup_dir"
timestamp="$(date +%Y%m%d_%H%M%S)"
output="$backup_dir/${database}_${timestamp}.dump"

docker exec "$container" pg_dump -U postgres -d "$database" -Fc > "$output"
printf 'Respaldo creado: %s\n' "$output"
