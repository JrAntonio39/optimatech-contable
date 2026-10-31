/**
 * Servicio de Asientos / Transacciones (Libro Diario).
 * Incluye Balance Inicial (tipo APERTURA), ajustes y cierre.
 * Backend: app/routers/asientos.py.
 */
import { api } from './api.js'

export const TIPOS_ASIENTO = ['APERTURA', 'DIARIO', 'AJUSTE', 'CIERRE']

export const asientosService = {
  /** Lista asientos. Acepta tipo, período, sucursal, estado y rango de fechas. */
  listar: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.tipo) qs.set('tipo', params.tipo)
    if (params.periodo_id) qs.set('periodo_id', params.periodo_id)
    if (params.sucursal_id) qs.set('sucursal_id', params.sucursal_id)
    if (params.estado) qs.set('estado', params.estado)
    if (params.desde) qs.set('desde', params.desde)
    if (params.hasta) qs.set('hasta', params.hasta)
    if (params.asiento_id) qs.set('asiento_id', params.asiento_id)
    const suffix = qs.toString() ? `?${qs.toString()}` : ''
    return api.get(`/api/asientos${suffix}`)
  },

  /** Crear asiento con detalle. El backend valida debe == haber. */
  crear: data => api.post('/api/asientos', data),
  /** Elimina solo asientos pendientes y manuales, si el rol tiene permiso. */
  eliminar: id => api.del(`/api/asientos/${id}`),
  // data = { codigo, fecha, concepto, tipo, periodo_id, sucursal_id,
  //          detalles: [{ cuenta_codigo, debe, haber, descripcion }] }

  /** Detalle de un asiento con sus líneas. */
  detalle: id => api.get(`/api/asientos/${id}`),

  /** Periodos contables (para el selector del formulario). */
  periodos: () => api.get('/api/periodos'),

  /** Sucursales (para el selector del formulario). */
  sucursales: () => api.get('/api/sucursales')
}
