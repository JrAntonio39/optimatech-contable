/**
 * Servicio de Pago de Salarios / Planilla (plus).
 * Al cerrar una planilla el backend genera un asiento automático:
 *   Debe:  4.1.1.09 Costos Personal
 *   Haber: 2.1.4 Sueldos por Pagar + 2.1.5 ISSS/AFP + retenciones
 * PENDIENTE: implementar endpoints en el backend FastAPI.
 */
import { api } from './api.js'

export const planillaService = {
  listarEmpleados: () => api.get('/api/empleados'),
  crearEmpleado: data => api.post('/api/empleados', data),

  listarPlanillas: () => api.get('/api/planillas'),
  crearPlanilla: data => api.post('/api/planillas', data),
  // data = { codigo, periodo: 'YYYY-MM', fecha_pago, sucursal_id, tipo, periodo_id,
  //          detalles: [{ empleado_id, dias_trabajados, salario_base, horas_extra,
  //                       bonificaciones, deduccion_isss, deduccion_afp, deduccion_renta }] }

  totalesPlanilla: id => api.get(`/api/planillas/${id}/totales`),
  contabilizar: id => api.post(`/api/planillas/${id}/contabilizar`, {})
}
