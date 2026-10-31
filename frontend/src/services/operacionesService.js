import { api } from './api.js'

export const operacionesService = {
  productosServicios: () => api.get('/api/productos-servicios'),
  clientes: () => api.get('/api/clientes'),
  crearCliente: data => api.post('/api/clientes', data),
  facturas: () => api.get('/api/facturas'),
  factura: id => api.get(`/api/facturas/${id}`),
  crearFactura: data => api.post('/api/facturas', data),
  eliminarFactura: id => api.del(`/api/facturas/${id}`),
  enviarFactura: id => api.post(`/api/facturas/${id}/enviar`),
  proveedores: () => api.get('/api/proveedores'),
  crearProveedor: data => api.post('/api/proveedores', data),
  actualizarProveedor: (id, data) => api.put(`/api/proveedores/${id}`, data),
  darDeBajaProveedor: id => api.del(`/api/proveedores/${id}`),
  activarProveedor: id => api.post(`/api/proveedores/${id}/activar`, {}),
  compras: () => api.get('/api/compras'),
  crearCompra: data => api.post('/api/compras', data),
  enviarCompra: id => api.post(`/api/compras/${id}/enviar`),
  empleados: () => api.get('/api/empleados'),
  crearEmpleado: data => api.post('/api/empleados', data),
  planillas: () => api.get('/api/planillas'),
  planilla: id => api.get(`/api/planillas/${id}`),
  crearPlanilla: data => api.post('/api/planillas', data),
  enviarPlanilla: id => api.post(`/api/planillas/${id}/enviar`),
  pagarPlanilla: (id, data) => api.post(`/api/planillas/${id}/pagar`, data)
}
