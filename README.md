# OptimaTech — Sistema Contable (App Web)

Proyecto de sistemas contables: empresa ficticia **OptimaTech Empresarial, S.A. de C.V.**
Catálogo, libro diario (normal, ajuste y cierre), libro mayor, balanza de
comprobación, estado de resultados y balance general. Extras: facturación
electrónica, libro de compras y pago de salarios.

## Stack

- **BD:** PostgreSQL 17 (Docker, puerto `5434`) — NO usa Supabase.
- **Backend:** Python + FastAPI (`backend/`, puerto `8000`).
- **Frontend:** Vue 3 + Quasar + Pinia (`frontend/`, puerto `9000`).

## Cómo probar la app (para el compañero)

Requisitos: Docker, Python 3.11+ y Node 20+.

```bash
# 1. Clonar y entrar
git clone https://github.com/JrAntonio39/optimatech-contable.git
cd optimatech-contable

# 2. Base de datos (Postgres local en Docker)
docker compose up -d
# Verifica: docker ps  ->  optimatech_db en 5434

# 2b. Cargar esquema + datos (217 cuentas del catálogo y tablas del sistema)
# Solo la primera vez (o para resetear la BD):
docker exec -i optimatech_db psql -U postgres -d optimatech_db < db/optimatech_init.sql
# Aplicar controles operativos (auditoría, estados de aprobación y reversos):
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/002_operational_controls.sql

# 3. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ya apunta a localhost:5434
uvicorn app.main:app --reload --host :: --port 8000
# Verifica: http://localhost:8000/health  ->  {"db":"ok"}

# 4. Frontend (otra terminal)
cd frontend
npm install
quasar dev            # o: npx quasar dev
# Abre http://localhost:9000  ->  te redirige a /login
```

> El frontend usa proxy en desarrollo (`quasar.config.js`): el navegador solo
> habla con el frontend y Vite reenvía `/api` y `/health` al backend. No hay
> que configurar CORS ni URLs.

## Usuarios, roles y permisos

El acceso se controla en el **backend** (la interfaz solo oculta lo que no
puede hacer, pero la API es la que rechaza).

### Matriz de permisos

Permisos con formato `modulo.accion`. Módulos: `cuentas`, `asientos`,
`periodos`, `sucursales`, `facturas`, `compras`, `planilla`, `reportes`,
`usuarios`, `auditoria`.

| Rol | Puede hacer |
| :--- | :--- |
| **admin** (Administrador) | Todo, incluida la gestión de usuarios y roles |
| **contador** (Contador) | Catálogo, asientos (crear/aprobar/anular), **cerrar períodos**, sucursales, reportes, auditoría |
| **auxiliar** (Auxiliar contable) | Ver catálogo, **registrar** asientos, ver reportes. No aprueba ni cierra |
| **ventas** (Ventas) | Emitir y anular facturas, ver reportes. No toca asientos ni cierra períodos |
| **compras** (Compras) | Registrar y aprobar compras, ver reportes. No toca asientos ni cierra períodos |
| **planilla** (Planilla) | Crear y aprobar planilla de salarios, ver reportes. No toca asientos ni cierra períodos |
| **auditor** (Auditor) | Solo lectura en todo el sistema, incluida la bitácora de auditoría |

### Cargar o ajustar la matriz (sin tocar código)

```bash
cd backend
python3 -m scripts.seed_permisos          # aplica permisos + matriz de roles
python3 -m scripts.seed_permisos --show   # solo muestra la matriz
```

### Crear el primer administrador (de forma segura)

Genera una contraseña aleatoria y la muestra por pantalla; **no queda ninguna
contraseña fija en el código ni en el repo**.

```bash
cd backend
python3 -m scripts.crear_admin --username admin --nombre "Administrador"
# Si el usuario ya existe y quieres rotar su contraseña:
python3 -m scripts.crear_admin --username admin --reset
```

### Usuarios de demostración (uno por rol)

```bash
cd backend
python3 -m scripts.seed_usuarios_demo
```

Crea `contador`, `auxiliar`, `ventas`, `compras`, `planilla` y `auditor`, todos
con contraseña `Demo1234`. Sirve para probar la matriz de permisos.

### Verificar que los permisos se aplican

```bash
cd backend
python3 -m scripts.verificar_permisos   # matriz de permisos por rol
python3 -m scripts.probar_control       # flujo de aprobación, anulación y bitácora
```

## Control del sistema (aprobaciones, períodos e historial)

- **Ciclo de vida del asiento:** todo asiento se registra en estado
  `PENDIENTE` y no suma a los reportes hasta que alguien con
  `asientos.aprobar` lo aprueba (pasa a `VIGENTE`).
- **Anulación con reversión:** anular un asiento vigente no lo borra: genera un
  **asiento de reversión** (contra-asiento) por el mismo monto dentro de un
  período abierto, marca el original como `ANULADO` y guarda el motivo.
- **Períodos contables:** se pueden abrir, editar, **cerrar** (bloquea
  movimientos) y reabrir. No se cierra un período con asientos `PENDIENTE`.
- **Sucursales:** alta y edición.
- **Bitácora de auditoría:** tabla `auditoria` con quién hizo cada operación
  (crear, editar, aprobar, anular, cerrar), cuándo y qué cambió.

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| GET | `/api/asientos/pendientes` | Asientos por aprobar (`asientos.ver`) |
| POST | `/api/asientos/{id}/aprobar` | Aprueba un asiento (`asientos.aprobar`) |
| POST | `/api/asientos/{id}/anular` | Anula con reversión (`asientos.anular`) |
| GET/POST/PUT | `/api/periodos` | Períodos contables |
| POST | `/api/periodos/{id}/cerrar` | Cierra el período (`periodos.cerrar`) |
| POST | `/api/periodos/{id}/abrir` | Reabre el período (`periodos.cerrar`) |
| GET/POST/PUT | `/api/sucursales` | Sucursales |
| GET | `/api/auditoria` | Bitácora con filtros (`auditoria.ver`) |

### Endpoints de autenticación

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| POST | `/api/auth/login` | Inicia sesión y devuelve el JWT |
| GET | `/api/auth/me` | Usuario autenticado + sus permisos |
| GET | `/api/auth/usuarios` | Listar usuarios (`usuarios.ver`) |
| POST | `/api/auth/register` | Crear usuario (`usuarios.crear`) |
| GET/POST/PUT | `/api/auth/roles` | Gestionar roles y su matriz de permisos |
| GET | `/api/auth/permisos` | Catálogo de permisos disponibles |

## Estructura

```
APP_Optimal_TECH/
├── docker-compose.yml   # BD Postgres + pgAdmin (http://localhost:5051)
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI + CORS
│   │   ├── database.py     # SQLAlchemy (lee DATABASE_URL del .env)
│   │   ├── models/         # catalogo.py, auth.py, empresa.py
│   │   ├── schemas/        # validación de entrada/salida
│   │   └── routers/        # auth, cuentas, asientos, reportes, meta
│   ├── scripts/            # seed de permisos, crear admin, verificación
│   └── requirements.txt
├── db/
│   └── optimatech_init.sql # esquema + 217 cuentas + datos seed
└── frontend/
    ├── quasar.config.js    # incluye proxy /api -> 127.0.0.1:8000
    └── src/
        ├── boot/pinia.js   # instala Pinia antes que el router
        ├── services/       # api.js + *Service.js (conexión REST)
        ├── stores/auth.js  # sesión, token y permisos
        ├── pages/          # CatalogoPage, TransaccionesPage, ...
        ├── layouts/        # MainLayout + menú por permisos
        └── constants/menu.js
```

## Módulos implementados

- Catálogo de cuentas (vista de árbol, se despliega por niveles)
- Balance inicial (asiento de apertura)
- Libro diario (filtros por tipo, período y sucursal)
- Libro mayor (movimientos con saldo acumulado)
- Balanza de comprobación
- Pérdidas y ganancias
- Balance general
- Usuarios, roles, permisos e inicio de sesión
- Aprobación y reversión auditable de asientos
- Administración de períodos y sucursales, y consulta de auditoría
- Filtros por estado y rango de fechas en el libro diario
- Exportación CSV y salida PDF mediante impresión del navegador en reportes principales

## Pendiente

- Completar los flujos funcionales de Facturación, Compras y Planilla (las pantallas actuales siguen siendo informativas).
- Integrar facturación electrónica/DTE real y sus validaciones fiscales; la app aún no transmite documentos a Hacienda.
- Exportación Excel XLSX; el CSV se puede abrir en Excel y el PDF se obtiene con la impresión del navegador.
- Revisión contable y tributaria de las cuentas y reglas antes de usar con operaciones reales.

## Seguridad en ejecución

Define `JWT_SECRET` como secreto aleatorio en el `.env` de backend antes de exponer el servicio. En `APP_ENV=production` la API no inicia si falta. La limitación de intentos de login actual vive en memoria del proceso y se reinicia al reiniciar el backend; para despliegues con varias instancias hay que moverla a un almacén compartido.

### Respaldos locales

```bash
bash scripts/backup_db.sh
# La restauración reemplaza los objetos actuales; exige confirmación escrita.
bash scripts/restore_db.sh backups/optimatech_db_FECHA_HORA.dump
```

Los respaldos se guardan en `backups/`, carpeta excluida de Git. Conserva una copia fuera del equipo para poder recuperarte de una falla del disco.
