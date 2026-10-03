/**
 * Servicio de Facturación Electrónica (plus).
 * Al contabilizar una factura el backend genera un asiento automático:
 *   Debe:  1.1.3.01.x Clientes
 *   Haber: 5.1.x Ingresos + 2.1.10 IVA Débito
 * PENDIENTE: implementar endpoints en el backend FastAPI.
 */
import { api } from './api.js'

export const facturacionService = {
  listarClientes: () => api.get('/api/clientes'),
  crearCliente: data => api.post('/api/clientes', data),

  listarFacturas: () => api.get('/api/facturas'),
  crearFactura: data => api.post('/api/facturas', data),
  // data = { numero, tipo_dte, fecha, cliente_id, sucursal_id, periodo_id,
  //          detalles: [{ descripcion, cantidad, precio_unitario, cuenta_ingreso_codigo }] }

  totalesFactura: id => api.get(`/api/facturas/${id}/totales`),
  contabilizar: id => api.post(`/api/facturas/${id}/contabilizar`, {})
}
