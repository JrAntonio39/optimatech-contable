/**
 * Cliente HTTP base para la API REST de OptimaTech.
 * En desarrollo usa mismo origen ('') y el proxy de Vite (quasar.config.js)
 * reenvía /api y /health a http://127.0.0.1:8000 (evita CORS y problemas
 * de resolución IPv4/IPv6 de localhost en el navegador).
 * Para producción define VITE_API_URL con la URL pública del backend.
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL ?? ''

const etiquetasCampos = {
  numero: 'número interno de la factura', codigo: 'código del cliente', nombre: 'nombre o razón social',
  fecha: 'fecha del documento', fecha_remision: 'fecha de la nota de remisión',
  numero_remision: 'número de la nota de remisión', nit: 'NIT', nrc: 'NRC',
  giro: 'giro o actividad económica', direccion: 'dirección', cantidad: 'cantidad',
  precio_unitario: 'precio unitario', cuenta_codigo: 'cuenta contable',
  telefono: 'teléfono', email: 'correo electrónico',
  dui: 'DUI del empleado', nombres: 'nombres del empleado', apellidos: 'apellidos del empleado',
  cargo: 'cargo del empleado',
  cliente_id: 'cliente', proveedor_id: 'proveedor', periodo_id: 'período contable',
  sucursal_id: 'sucursal', forma_pago: 'forma de pago', plazo_pago: 'plazo de pago'
}

function mensajeValidacion(issue) {
  const loc = Array.isArray(issue?.loc) ? issue.loc : []
  const campo = [...loc].reverse().find(part => typeof part === 'string' && part !== 'body')
  const nombre = etiquetasCampos[campo] || 'dato ingresado'
  switch (issue?.type) {
    case 'missing': return `Completa el campo ${nombre}.`
    case 'string_too_short': return `El campo ${nombre} está vacío o incompleto.`
    case 'string_pattern_mismatch': return `El campo ${nombre} no cumple el formato solicitado.`
    case 'string_too_long': return `El campo ${nombre} supera la longitud permitida.`
    case 'decimal_max_places': return `El campo ${nombre} admite como máximo ${issue?.ctx?.decimal_places ?? 2} decimales.`
    case 'greater_than': return `El campo ${nombre} debe ser mayor que cero.`
    default: return `Revisa el valor ingresado en ${nombre}.`
  }
}

function mensajeApi(status, raw, path = '') {
  let payload
  try { payload = JSON.parse(raw) } catch { payload = null }
  const detail = payload?.detail
  if (typeof detail === 'string') {
    if (detail.toLowerCase().includes('fecha de la nota de remisión')) {
      return 'Ingresaste el número de una nota de remisión. Completa también la fecha de esa nota; si no corresponde, borra el número.'
    }
    if (detail === 'Internal Server Error') return `El servidor encontró un error al procesar la solicitud${path ? ` (${path})` : ''}. Revisa la terminal del backend para ver el detalle.`
    return detail
  }
  if (Array.isArray(detail) && detail.length) return detail.map(mensajeValidacion).join(' ')
  if (status >= 500) return `El servidor encontró un error al procesar la solicitud${path ? ` (${path})` : ''}. Revisa la terminal del backend para ver el detalle.`
  if (status === 422) return 'Revisa los datos del formulario: hay un campo vacío o con formato incorrecto.'
  return 'No se pudo completar la operación. Revisa los datos e inténtalo de nuevo.'
}

function getAuthHeader() {
  const token = sessionStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      ...options,
      // Las listas operativas se consultan periódicamente desde otros equipos.
      // Evita que el navegador reutilice una respuesta GET anterior.
      cache: options.cache ?? 'no-store',
      body: options.body ? JSON.stringify(options.body) : undefined
    })
  } catch {
    throw new Error('No se pudo conectar con la API. Comprueba que el backend esté iniciado e inténtalo de nuevo.')
  }

  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new Error(mensajeApi(res.status, detail, path))
  }

  // 204 Sin contenido
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  get: path => request(path),
  post: (path, body) => request(path, { method: 'POST', body }),
  put: (path, body) => request(path, { method: 'PUT', body }),
  del: path => request(path, { method: 'DELETE' })
}

// Helper para login (usa form-data, no JSON)
export async function loginRequest(username, password) {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString()
  })
  if (!res.ok) {
    let message = `No se pudo iniciar sesión (${res.status})`
    try {
      const payload = await res.json()
      if (typeof payload.detail === 'string') message = payload.detail
    } catch {
      // Conserva el mensaje legible si el servidor no devuelve JSON.
    }
    throw new Error(message)
  }
  return res.json()
}
