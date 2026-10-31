# OptimaTech — Sistema Contable (App Web)

Proyecto de sistemas contables: empresa ficticia **OptimaTech Empresarial, S.A. de C.V.**
Catálogo, libro diario (normal, ajuste y cierre), libro mayor, balanza de
comprobación, estado de resultados y balance general. Incluye registro contable
de facturas, compras y planillas de salarios.

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
# Agregar el registro contable de desembolsos de planilla:
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/003_planilla_pagos.sql
# Agregar condiciones y formas de pago de las facturas:
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/004_factura_condiciones_pago.sql
# Agregar el catálogo de productos/servicios y datos tributarios complementarios:
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/005_catalogo_facturacion.sql
# Agregar distribución por cuenta de gasto y aportes patronales en planilla:
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/006_planilla_distribucion.sql
# Distinguir rechazo de asientos pendientes de la anulacion de vigentes:
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/007_rechazo_asientos_pendientes.sql
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/008_catalogo_cargos_empleado.sql
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/009_empleado_identificaciones_unicas.sql

> La pantalla de facturación genera comprobantes internos de práctica y una
> versión imprimible. No genera DTE autorizados: para validez fiscal el DTE debe
> ajustarse al formato de Hacienda, firmarse, transmitirse y recibir su Sello de
> Recepción.

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
| **contador** (Contador) | Catálogo, asientos (crear/aprobar/anular), **cerrar períodos**, sucursales, reportes, auditoría y registrar pagos de planilla |
| **auxiliar** (Auxiliar contable) | Ver catálogo, **registrar** asientos, ver reportes. No aprueba ni cierra |
| **ventas** (Ventas) | Emitir y anular facturas, ver reportes. No toca asientos ni cierra períodos |
| **compras** (Compras) | Registrar y aprobar compras, ver reportes. No toca asientos ni cierra períodos |
| **planilla** (Planilla) | Crear planillas, registrar su pago y consultar reportes. No aprueba asientos ni cierra períodos |
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

En la instalación local de demostración, la cuenta `admin` usa la contraseña `12345`.
Para actualizar una base ya creada (sin borrar datos), desde la raíz del proyecto ejecuta:

```bash
docker exec -i optimatech_db psql -v ON_ERROR_STOP=1 -U postgres -d optimatech_db < db/fix_demo_admin_password.sql
```

La base usa el volumen persistente `optimatech_pgdata`; apagar la PC no debería
restablecer la contraseña. Evita `docker compose down -v`, porque elimina ese volumen.

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
OPTIMATECH_ADMIN_PASSWORD='tu-clave' python3 -m scripts.probar_control  # aprobación, anulación y bitácora
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

## Facturación, compras y planillas

Los tres módulos guardan primero un borrador. Al enviarlo generan un asiento
`PENDIENTE`; un contador lo aprueba desde **Control y auditoría**. Al aprobarse
el asiento, la factura o compra pasa a `VIGENTE` y la planilla a
`CONTABILIZADA`. Las operaciones quedan en la misma bitácora.

| Módulo | Rutas principales |
| :--- | :--- |
| Facturación | `GET/POST /api/clientes`, `GET/POST /api/facturas`, `POST /api/facturas/{id}/enviar` |
| Compras | `GET/POST /api/proveedores`, `GET/POST /api/compras`, `POST /api/compras/{id}/enviar` |
| Planilla | `GET/POST /api/empleados`, `GET/POST /api/planillas`, `GET /api/planillas/{id}`, `POST /api/planillas/{id}/enviar`, `POST /api/planillas/{id}/pagar` |

El ejercicio del README aplica IVA del 13% a todas las líneas de facturas y
compras. Las deducciones y aportes patronales de planilla se ingresan
manualmente; no se calculan tasas legales. Son reglas didácticas para practicar
los asientos, no una integración con Hacienda ni un cálculo fiscal listo para
operaciones reales.

### Ejercicio integrado para probar el sistema

Usa la base inicial de demostración, con el período abierto 2026, sucursal
Casa Matriz, cliente **CLI-001 Ferretería El Perno**, empleado **EMP-001 Carlos
Rivas** y las cuentas del catálogo. Si tu base no trae esos datos, crea los
registros equivalentes primero. No cargues otra apertura: la base inicial ya
trae asientos de ejemplo.

1. **Ventas:** inicia sesión como `ventas` y crea una factura `EJ-F-2026-001`,
   tipo `CCF`, fecha `2026-04-03`, para Ferretería El Perno, en Casa Matriz y
   período 2026. Agrega `Servicio de desarrollo de software`, cantidad `1`,
   precio `$1,000.00`, cuenta de ingreso `5.1.1.01`. Guarda y pulsa **Enviar**.
   Debe quedar en espera de aprobación por un asiento de `$1,130.00`.
2. **Compras:** inicia sesión como `compras`, crea el proveedor
   `PRV-EJ-001 / Suministros de prueba` y una compra `EJ-C-2026-001`, tipo
   `CCF`, fecha `2026-04-05`, en Casa Matriz y período 2026. Registra
   `Equipo de cómputo`, cantidad `1`, precio `$500.00`, cuenta `1.1.5.01`.
   Guarda y envía; el asiento debe sumar `$565.00`.
3. **Salarios:** inicia sesión como `planilla`, crea la planilla de `2026-04`,
   fecha de pago `2026-04-30`, para Carlos Rivas. Ingresa 30 días, `$50.00` de
   horas extra, `$100.00` de bonificación, ISSS `$36.00`, AFP `$87.75`, renta
   `$85.00` y cero en otras deducciones. Guarda y envía. El bruto esperado es
   `$1,350.00` y el líquido `$1,141.25`.
4. **Aprobación:** inicia sesión como `contador`, entra en **Control y
   auditoría**, localiza los tres asientos pendientes y apruébalos. Los
   documentos deben pasar a `VIGENTE` (factura y compra) y `CONTABILIZADA`
   (planilla).
5. **Pago de salarios:** inicia sesión como `planilla`, pulsa **Registrar
   pago** en la planilla contabilizada, usa fecha `2026-04-30`, período 2026 y
   cuenta `1.1.1.01` (Caja General). Luego como `contador`, aprueba el nuevo
   asiento pendiente. La planilla debe pasar a `PAGADA`; el asiento carga
   Sueldos por pagar `$1,141.25` y abona Caja por el mismo monto.
6. **Reportes:** en período 2026 revisa Libro Diario, Libro Mayor, Balanza,
   Estado de Resultados y Balance General. Los movimientos nuevos deben
   mostrar: factura, Debe Clientes `$1,130.00`, Haber Ingresos `$1,000.00` e
   IVA `$130.00`; compra, Debe Inventario `$500.00` e IVA crédito `$65.00`,
   Haber Proveedores `$565.00`; planilla, Debe Costos de Personal `$1,350.00`,
   Haber Seguridad Social `$123.75`, Retenciones de renta `$85.00` y Sueldos
   por pagar `$1,141.25`, más el asiento posterior de desembolso. Cada asiento
   debe cuadrar.
7. **Permisos y período (opcional):** con el usuario `ventas`, verifica que
   puede enviar facturas pero no aprobar asientos. Al final, intenta cerrar el
   período 2026 como contador; se debe poder cerrar cuando no existan asientos
   pendientes. Reábrelo si continuarás probando en 2026.

La base de demostración puede contener datos de ejercicios anteriores. Compara
los importes de este ejercicio por fecha/concepto o contra el saldo inicial,
porque los reportes mostrarán también esos movimientos previos.

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
- Registro de clientes, facturas, proveedores, compras, empleados y planillas; documentos generan asientos pendientes para aprobación

## Pendiente

- Integrar transmisión electrónica/DTE y validaciones fiscales; el módulo de facturación aún no transmite documentos a Hacienda.
- Incorporar cálculo de retenciones y aportes patronales validado para uso real; actualmente los valores se ingresan manualmente.
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
