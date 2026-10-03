/**
 * Servicio de Asientos / Transacciones (Libro Diario).
 * Incluye Balance Inicial (tipo APERTURA), ajustes y cierre.
 * PENDIENTE: implementar router de asientos en el backend FastAPI.
 */
import { api } from './api.js'

export const TIPOS_ASIENTO = ['APERTURA', 'DIARIO', 'AJUSTE', 'CIERRE']

export const asientosService = {
  /** Lista asientos. Acepta { tipo, periodo_id, sucursal_id } */
  listar: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.tipo) qs.set('tipo', params.tipo)
    if (params.periodo_id) qs.set('periodo_id', params.periodo_id)
    if (params.sucursal_id) qs.set('sucursal_id', params.sucursal_id)
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return api.get(`/api/asientos${suffix}`)
  },

  /** Crear asiento con detalle. El backend valida debe == haber. */
  crear: data => api.post('/api/asientos', data),
  // data = { codigo, fecha, concepto, tipo, periodo_id, sucursal_id,
  //          detalles: [{ cuenta_codigo, debe, haber, descripcion }] }

  /** Detalle de un asiento con sus líneas. */
  detalle: id => api.get(`/api/asientos/${id}`),

  /** Totales calculados (vista v_asiento_totales: CUADRADO/DESCUADRADO). */
  totales: () => api.get('/api/asientos/totales'),

  /** Periodos contables (para el selector del formulario). */
  periodos: () => api.get('/api/periodos'),

  /** Sucursales (para el selector del formulario). */
  sucursales: () => api.get('/api/sucursales')
}
