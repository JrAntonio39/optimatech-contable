/**
 * Cliente HTTP base para la API REST de OptimaTech.
 * En desarrollo usa mismo origen ('') y el proxy de Vite (quasar.config.js)
 * reenvía /api y /health a http://127.0.0.1:8000 (evita CORS y problemas
 * de resolución IPv4/IPv6 de localhost en el navegador).
 * Para producción define VITE_API_URL con la URL pública del backend.
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL ?? ''

function getAuthHeader() {
  const token = sessionStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined
  })

  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new Error(`API ${res.status} en ${path}: ${detail || res.statusText}`)
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
