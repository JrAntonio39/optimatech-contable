/**
 * Servicio de Control del sistema: aprobaciones, anulaciones, administración
 * de períodos y sucursales, y bitácora de auditoría.
 */
import { api } from './api.js'

export const controlService = {
  // --- Aprobaciones y anulaciones ---
  /** Asientos en estado PENDIENTE (por aprobar). */
  pendientes: periodoId =>
    api.get(
      periodoId
        ? `/api/asientos/pendientes?periodo_id=${periodoId}`
        : '/api/asientos/pendientes'
    ),

  /** Aprueba un asiento: PENDIENTE -> VIGENTE. */
  aprobar: id => api.post(`/api/asientos/${id}/aprobar`),

  /**
   * Anula un asiento. El backend genera el asiento de reversión (contra-asiento)
   * dentro de un período abierto, por eso pide periodo_id y fecha_reversion.
   */
  anular: (id, { motivo, periodo_id, fecha_reversion }) =>
    api.post(`/api/asientos/${id}/anular`, {
      motivo,
      periodo_id,
      fecha_reversion
    }),

  // --- Períodos contables ---
  listarPeriodos: () => api.get('/api/periodos'),
  crearPeriodo: data => api.post('/api/periodos', data),
  actualizarPeriodo: (id, data) => api.put(`/api/periodos/${id}`, data),
  cerrarPeriodo: id => api.post(`/api/periodos/${id}/cerrar`),
  abrirPeriodo: id => api.post(`/api/periodos/${id}/abrir`),

  // --- Sucursales ---
  listarSucursales: () => api.get('/api/sucursales'),
  crearSucursal: data => api.post('/api/sucursales', data),
  actualizarSucursal: (id, data) => api.put(`/api/sucursales/${id}`, data),

  // --- Auditoría ---
  /** Bitácora. Acepta { modulo, accion, usuario_id, registro_id, desde, hasta, q } */
  auditoria: (params = {}) => {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== '') qs.set(k, v)
    })
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return api.get(`/api/auditoria${suffix}`)
  },
  resumenAuditoria: () => api.get('/api/auditoria/resumen')
}
