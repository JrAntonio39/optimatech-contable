/**
 * Servicio de Catálogo de Cuentas.
 * Endpoints reales del backend FastAPI (app/routers/cuentas.py).
 */
import { api } from './api.js'

export const cuentasService = {
  /** Todas las cuentas (217). Acepta { nivel: 1-5, q: 'texto' } */
  listar: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.nivel) qs.set('nivel', params.nivel)
    if (params.q) qs.set('q', params.q)
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return api.get(`/api/cuentas${suffix}`)
  },

  /** Solo cuentas de mayor (nivel 3, las del Manual). */
  mayor: () => api.get('/api/cuentas/mayor'),

  /** Detalle de una cuenta + sus hijas. Ej: '1.1.1' */
  detalle: codigo => api.get(`/api/cuentas/${encodeURIComponent(codigo)}`),

  /** Crear cuenta (PENDIENTE: implementar POST /api/cuentas en el backend). */
  crear: data => api.post('/api/cuentas', data)
}
