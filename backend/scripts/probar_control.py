"""
Prueba end-to-end del módulo de Control: aprobación, anulación con reversión,
cierre de período y bitácora de auditoría.

Uso: python3 -m scripts.probar_control
"""

import sys
import requests

BASE = "http://localhost:8000"
ADMIN = ("admin", "lBd1DzihB1Uao0Nc")
AUXILIAR = ("auxiliar", "Demo1234")
CONTADOR = ("contador", "Demo1234")


def login(user, password):
    r = requests.post(f"{BASE}/api/auth/login", data={"username": user, "password": password})
    if r.status_code != 200:
        print(f"! login {user}: {r.status_code} {r.text[:150]}")
        return None
    return r.json()["access_token"]


def hdr(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    fallos = 0
    print("=" * 70)
    print("PRUEBA END-TO-END: Control, aprobaciones y auditoría")
    print("=" * 70)

    tok_admin = login(*ADMIN)
    tok_aux = login(*AUXILIAR)
    tok_cont = login(*CONTADOR)
    if not all([tok_admin, tok_aux, tok_cont]):
        print("\n! Faltan sesiones. Ejecuta primero: python3 -m scripts.seed_usuarios_demo")
        return 1

    # --- Periodo de trabajo ---
    per = requests.get(f"{BASE}/api/periodos", headers=hdr(tok_admin)).json()
    periodo = next((p for p in per["periodos"] if p["estado"] == "ABIERTO"), None)
    if not periodo:
        print("! No hay período abierto")
        return 1
    print(f"\n[0] Período abierto: {periodo['anio']} (id {periodo['id']})")

    # --- 1. El auxiliar registra un asiento -> debe quedar PENDIENTE ---
    print("\n[1] Auxiliar registra un asiento (no tiene 'asientos.aprobar'):")
    r = requests.post(
        f"{BASE}/api/asientos",
        headers=hdr(tok_aux),
        json={
            "fecha": f"{periodo['anio']}-06-15",
            "concepto": "Prueba de control: compra de equipo",
            "tipo": "DIARIO",
            "periodo_id": periodo["id"],
            "sucursal_id": 1,
            "detalles": [
                {"cuenta_codigo": "1.1.5.01", "debe": 1500, "haber": 0, "descripcion": "Equipo"},
                {"cuenta_codigo": "2.1.1.01", "debe": 0, "haber": 1500, "descripcion": "Proveedor"},
            ],
        },
    )
    if r.status_code != 201:
        print(f"    [FALLA] POST /api/asientos -> {r.status_code} {r.text[:200]}")
        return 1
    asiento = r.json()["asiento"]
    estado = r.json().get("estado")
    ok = estado == "PENDIENTE"
    if not ok:
        fallos += 1
    print(f"    [{'OK  ' if ok else 'FALLA'}] asiento {asiento['codigo']} creado con estado {estado} (se esperaba PENDIENTE)")

    # --- 2. El auxiliar NO puede aprobar ---
    print("\n[2] Auxiliar intenta aprobar su propio asiento:")
    r = requests.post(f"{BASE}/api/asientos/{asiento['id']}/aprobar", headers=hdr(tok_aux))
    ok = r.status_code == 403
    if not ok:
        fallos += 1
    print(f"    [{'OK  ' if ok else 'FALLA'}] HTTP {r.status_code} (se esperaba 403)")

    # --- 3. El auxiliar NO puede cerrar el período ---
    print("\n[3] Auxiliar intenta cerrar el período:")
    r = requests.post(f"{BASE}/api/periodos/{periodo['id']}/cerrar", headers=hdr(tok_aux))
    ok = r.status_code == 403
    if not ok:
        fallos += 1
    print(f"    [{'OK  ' if ok else 'FALLA'}] HTTP {r.status_code} (se esperaba 403)")

    # --- 4. El contador aprueba ---
    print("\n[4] Contador aprueba el asiento:")
    r = requests.post(f"{BASE}/api/asientos/{asiento['id']}/aprobar", headers=hdr(tok_cont))
    ok = r.status_code == 200
    if not ok:
        fallos += 1
        print(f"    [FALLA] HTTP {r.status_code} {r.text[:200]}")
    else:
        print(f"    [OK  ] HTTP 200 -> estado {r.json().get('asiento', {}).get('estado')}")

    # --- 5. El contador anula (con reversión) ---
    print("\n[5] Contador anula el asiento (se genera reversión):")
    r = requests.post(
        f"{BASE}/api/asientos/{asiento['id']}/anular",
        headers=hdr(tok_cont),
        json={
            "motivo": "Prueba automática: anulación con asiento de reversión",
            "periodo_id": periodo["id"],
            "fecha_reversion": f"{periodo['anio']}-06-20",
        },
    )
    ok = r.status_code == 200
    if not ok:
        fallos += 1
        print(f"    [FALLA] HTTP {r.status_code} {r.text[:250]}")
    else:
        rev = r.json().get("reversion", {}).get("asiento", {})
        print(f"    [OK  ] anulado. Reversión generada: {rev.get('codigo')}")

    # --- 6. La bitácora registra todo ---
    print("\n[6] Bitácora de auditoría:")
    r = requests.get(f"{BASE}/api/auditoria", headers=hdr(tok_cont))
    ok = r.status_code == 200
    if not ok:
        fallos += 1
        print(f"    [FALLA] HTTP {r.status_code}")
    else:
        regs = r.json()["registros"]
        acciones = [x["accion"] for x in regs]
        print(f"    [OK  ] {len(regs)} registro(s): {acciones}")
        esperados = {"crear", "aprobar", "anular"}
        faltan = esperados - set(acciones)
        if faltan:
            fallos += 1
            print(f"    [FALLA] faltan acciones en la bitácora: {faltan}")
        else:
            print(f"    [OK  ] la bitácora registró: {', '.join(sorted(esperados))}")

    # --- 7. El auxiliar NO puede ver la auditoría ---
    print("\n[7] Auxiliar intenta consultar la auditoría:")
    r = requests.get(f"{BASE}/api/auditoria", headers=hdr(tok_aux))
    ok = r.status_code == 403
    if not ok:
        fallos += 1
    print(f"    [{'OK  ' if ok else 'FALLA'}] HTTP {r.status_code} (se esperaba 403)")

    print("\n" + "=" * 70)
    print(f"RESULTADO: {'TODO CORRECTO' if fallos == 0 else f'{fallos} FALLOS'}")
    print("=" * 70)
    return 0 if fallos == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
