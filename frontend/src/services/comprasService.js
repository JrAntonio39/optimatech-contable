/**
 * Servicio de Compras y Proveedores (plus Libro de Compras).
 * Al contabilizar una compra el backend genera un asiento automático:
 *   Debe:  1.1.5/1.2.3 Activo + 1.1.8 IVA Crédito
 *   Haber: 2.1.1 Proveedores
 * PENDIENTE: implementar endpoints en el backend FastAPI.
 */
import { api } from './api.js'

export const comprasService = {
  listarProveedores: () => api.get('/api/proveedores'),
  crearProveedor: data => api.post('/api/proveedores', data),

  listarCompras: () => api.get('/api/compras'),
  crearCompra: data => api.post('/api/compras', data),
  // data = { numero, tipo_doc, fecha, proveedor_id, sucursal_id, periodo_id,
  //          detalles: [{ descripcion, cantidad, precio_unitario, cuenta_activo_codigo }] }

  totalesCompra: id => api.get(`/api/compras/${id}/totales`),
  contabilizar: id => api.post(`/api/compras/${id}/contabilizar`, {})
}
