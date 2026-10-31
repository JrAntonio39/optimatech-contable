import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, loginRequest } from '@/services/api.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(sessionStorage.getItem('token') || '')
  const usuario = ref(JSON.parse(sessionStorage.getItem('usuario') || 'null'))
  const cargando = ref(false)
  const error = ref('')

  const estaAutenticado = computed(() => !!token.value && !!usuario.value)
  const esAdmin = computed(
    () => usuario.value?.rol_codigos?.includes('admin') ?? false
  )
  const permisos = computed(() => usuario.value?.permiso_codigos ?? [])

  /** ¿El usuario tiene el permiso "modulo.accion"? */
  const tienePermiso = codigo => {
    if (!usuario.value) return false
    if (esAdmin.value) return true
    return permisos.value.includes(codigo)
  }

  /** ¿Tiene alguno de los permisos indicados? */
  const tieneAlguno = (...codigos) => codigos.some(c => tienePermiso(c))

  async function login(username, password) {
    cargando.value = true
    error.value = ''
    try {
      const res = await loginRequest(username, password)
      token.value = res.access_token
      usuario.value = res.usuario
      sessionStorage.setItem('token', token.value)
      sessionStorage.setItem('usuario', JSON.stringify(usuario.value))
      return true
    } catch (e) {
      error.value = e.message || 'Error al iniciar sesión'
      return false
    } finally {
      cargando.value = false
    }
  }

  function logout() {
    token.value = ''
    usuario.value = null
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('usuario')
  }

  async function actualizarPerfil() {
    const actual = await api.get('/api/auth/me')
    usuario.value = actual
    sessionStorage.setItem('usuario', JSON.stringify(actual))
    return actual
  }

  function init() {
    const storedToken = sessionStorage.getItem('token')
    const storedUser = sessionStorage.getItem('usuario')
    if (storedToken && storedUser) {
      token.value = storedToken
      try {
        usuario.value = JSON.parse(storedUser)
      } catch {
        logout()
      }
    }
  }

  return {
    token,
    usuario,
    cargando,
    error,
    estaAutenticado,
    esAdmin,
    permisos,
    tienePermiso,
    tieneAlguno,
    login,
    actualizarPerfil,
    logout,
    init
  }
})
