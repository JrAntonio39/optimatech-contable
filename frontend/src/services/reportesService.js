/**
 * Servicio de reportes contables (solo lectura).
 * Backend: app/routers/reportes.py
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

  /** Movimientos paginados de una cuenta (mayorización con saldo acumulado). */
  mayorCuenta: (codigo, periodoId, limit = 50, offset = 0) => {
    const qs = new URLSearchParams({ limit, offset })
    if (periodoId) qs.set('periodo_id', periodoId)
    return api.get(`/api/reportes/mayor/${encodeURIComponent(codigo)}?${qs.toString()}`)
  },

  /** Balanza de Comprobación (cuentas de mayor, nivel 3). Acepta periodo_id. */
  balanza: periodoId =>
    api.get(
      periodoId
        ? `/api/reportes/balanza?periodo_id=${periodoId}`
        : '/api/reportes/balanza'
    ),

  /** Balance General (Activo = Pasivo + Patrimonio + resultado). */
  balanceGeneral: periodoId =>
    api.get(
      periodoId
        ? `/api/reportes/balance-general?periodo_id=${periodoId}`
        : '/api/reportes/balance-general'
    ),

  /** Estado de resultados de varios pasos. */
  resultados: periodoId =>
    api.get(
      periodoId
        ? `/api/reportes/resultados?periodo_id=${periodoId}`
        : '/api/reportes/resultados'
    )
}
