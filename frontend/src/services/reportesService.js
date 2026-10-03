/**
 * Servicio de reportes contables (solo lectura, vienen de vistas SQL).
 * PENDIENTE: implementar estos endpoints en el backend FastAPI.
 *  - /api/libro-mayor      <- v_libro_mayor
 *  - /api/balanza          <- v_balanza_comprobacion
 *  - /api/balance-general  <- clases 1, 2, 3
 *  - /api/resultados       <- clases 4 y 5 (Pérdidas y Ganancias)
 */
import { api } from './api.js'

export const reportesService = {
  /** Libro Mayor: saldos por cuenta. */
  libroMayor: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.codigo) qs.set('codigo', params.codigo)
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return api.get(`/api/libro-mayor${suffix}`)
  },

  /** Balanza de Comprobación (cuentas de mayor, nivel 3). */
  balanza: () => api.get('/api/balanza'),

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
