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

### Verificar que los permisos se aplican

```bash
cd backend
python3 -m scripts.verificar_permisos
```

Crea usuarios temporales de prueba (ventas, contador, auditor), hace login con
cada uno y comprueba que la API acepta lo permitido y responde **403** en lo
no permitido.

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

## Pendiente (para repartir)

- Seed de clases 2 (Pasivo), 4, 5, 6 y 7 en el catálogo.
- Páginas funcionales: Facturación, Compras y Planilla.
- Bitácora de auditoría (quién creó, editó, aprobó o anuló cada operación).
- Aprobación/anulación de asientos con estados (borrador, pendiente, aprobado).
- Administración de períodos y sucursales con bloqueo de períodos cerrados.
- Exportación de reportes a Excel/PDF.
