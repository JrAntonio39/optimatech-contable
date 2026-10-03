# OptimaTech — Sistema Contable (App Web)

Proyecto de sistemas contables: empresa ficticia **OptimaTech Empresarial, S.A. de C.V.**
Catálogo, libro diario (normal, ajuste y cierre), libro mayor, balanza de
comprobación, estado de resultados y balance general. Extras: facturación
electrónica, libro de compras y pago de salarios.

## Stack

- **BD:** PostgreSQL 17 (Docker, puerto `5434`) — NO usa Supabase.
- **Backend:** Python + FastAPI (`backend/`, puerto `8000`).
- **Frontend:** Vue 3 + Quasar (`frontend/`, puerto `9000`/`9001`).

## Cómo probar la app (para el compañero)

Requisitos: Docker, Python 3.11+ y Node 20+.

```bash
# 1. Clonar y entrar
git clone <URL_DEL_REPO>
cd APP_Optimal_TECH

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
# Abre http://localhost:9000/#/catalogo
```

> El frontend usa proxy en desarrollo (`quasar.config.js`): el navegador solo
> habla con el frontend y Vite reenvía `/api` y `/health` al backend. No hay
> que configurar CORS ni URLs.

## Estructura

```
APP_Optimal_TECH/
├── docker-compose.yml   # BD Postgres + pgAdmin (http://localhost:5051)
├── backend/
│   ├── app/
│   │   ├── main.py      # FastAPI + CORS
│   │   ├── database.py  # SQLAlchemy (lee DATABASE_URL del .env)
│   │   └── routers/     # cuentas.py, asientos.py, meta.py
│   └── requirements.txt
└── frontend/
    ├── quasar.config.js       # incluye proxy /api -> 127.0.0.1:8000
    └── src/
        ├── services/          # api.js + *Service.js (conexión REST)
        ├── pages/             # CatalogoPage, TransaccionesPage, ...
        ├── layouts/           # MainLayout + menú
        └── constants/menu.js  # apartados de la app
```

## Pendiente (para repartir)

- Seed de clases 2 (Pasivo), 4, 5, 6 y 7 en el catálogo.
- `POST /api/cuentas` en el backend (crear cuenta desde la app).
- Páginas funcionales: Transacciones, Libro Diario/Mayor, Balanza,
  Resultados, Balance General, Facturación, Compras, Planilla.
- Validación partida doble (Debe = Haber) en asientos.
