/**
 * Servicio de reportes contables (solo lectura).
 * Backend: app/routers/reportes.py
 * PENDIENTE en backend:
 *  - /api/balance-general  <- clases 1, 2, 3
 *  - /api/resultados       <- clases 4 y 5 (Pérdidas y Ganancias)
 */
import { api } from './api.js'

export const reportesService = {
  /** Libro Mayor: totales por cuenta hoja con movimiento. Acepta { periodo_id, q } */
  libroMayor: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.periodo_id) qs.set('periodo_id', params.periodo_id)
    if (params.q) qs.set('q', params.q)
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return api.get(`/api/reportes/mayor${suffix}`)
  },

  /** Movimientos de una cuenta (mayorización con saldo acumulado). */
  mayorCuenta: (codigo, periodoId) =>
    api.get(
      periodoId
        ? `/api/reportes/mayor/${encodeURIComponent(codigo)}?periodo_id=${periodoId}`
        : `/api/reportes/mayor/${encodeURIComponent(codigo)}`
    ),

  /** Balanza de Comprobación (cuentas de mayor, nivel 3). Acepta periodo_id. */
  balanza: periodoId =>
    api.get(
      periodoId
        ? `/api/reportes/balanza?periodo_id=${periodoId}`
        : '/api/reportes/balanza'
    ),

  /** Balance General (Activo = Pasivo + Patrimonio). */
  balanceGeneral: periodoId =>
    api.get(
      periodoId
        ? `/api/balance-general?periodo_id=${periodoId}`
        : '/api/balance-general'
    ),

  /** Estado de Pérdidas y Ganancias (ingresos 5.x menos costos/gastos 4.x). */
  resultados: periodoId =>
    api.get(
      periodoId ? `/api/resultados?periodo_id=${periodoId}` : '/api/resultados'
    )
}
