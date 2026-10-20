import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginRequest } from '@/services/api.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const usuario = ref(JSON.parse(localStorage.getItem('usuario') || 'null'))
  const cargando = ref(false)
  const error = ref('')

  const estaAutenticado = computed(() => !!token.value && !!usuario.value)
  const esAdmin = computed(
    () => usuario.value?.rol_codigos?.includes('admin') ?? false
  )
  const tienePermiso = (_modulo, _accion) => {
    if (!usuario.value) return false
    if (esAdmin.value) return true
    return usuario.value.rol_codigos?.length > 0
  }

  async function login(username, password) {
    cargando.value = true
    error.value = ''
    try {
      const res = await loginRequest(username, password)
      token.value = res.access_token
      usuario.value = res.usuario
      localStorage.setItem('token', token.value)
      localStorage.setItem('usuario', JSON.stringify(usuario.value))
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
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
  }

  function init() {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('usuario')
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
    tienePermiso,
    login,
    logout,
    init
  }
})
