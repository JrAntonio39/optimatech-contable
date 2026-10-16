from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import cuentas, asientos, meta, clientes, facturas, compras, proveedores, empleados, planillas

app = FastAPI(title="OptimaTech API", version="1.0", description="API Contable - Catálogo 217 cuentas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cuentas.router)
app.include_router(asientos.router)
app.include_router(meta.router)
app.include_router(clientes.router)
app.include_router(facturas.router)
app.include_router(compras.router)
app.include_router(proveedores.router)
app.include_router(empleados.router)
app.include_router(planillas.router)

@app.get("/", tags=["Root"])
def root():
    return {"msg": "OptimaTech API - OK", "endpoints": {"/api/cuentas": "217 cuentas", "/api/cuentas?nivel=3": "cuentas de mayor", "/api/asientos": "libro diario", "/api/periodos": "periodos", "/api/sucursales": "sucursales", "/docs": "Swagger"}}

@app.get("/health")
def health():
    from app.database import engine
    from sqlalchemy import text
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return {"db": "ok", "port": "5434"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}
