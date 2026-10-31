import { defineRouter } from '#q-app'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router'

import routes from './routes.js'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter((/* { store, ssrContext } */) => {
  const createHistory = import.meta.env.QUASAR_SERVER
    ? createMemoryHistory
    : import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE)
  })

  // Guardia de navegación: proteger rutas que requieren autenticación
  Router.beforeEach(to => {
    const token = sessionStorage.getItem('token')
    if (to.matched.some(record => record.meta.requiresAuth) && !token) {
      return { path: '/login', query: { redirect: to.fullPath } }
    }

    if (to.path === '/login' && token) {
      return { path: '/' }
    }

    if ((to.meta.permiso || to.meta.permisos) && token) {
      try {
        const user = JSON.parse(sessionStorage.getItem('usuario') || 'null')
        const esAdmin = user?.rol_codigos?.includes('admin')
        const permisosNecesarios = to.meta.permisos || [to.meta.permiso]
        const allowed = esAdmin || permisosNecesarios.some(permiso =>
          user?.permiso_codigos?.includes(permiso)
        )
        if (!allowed) return { path: '/', query: { sinPermiso: '1' } }
      } catch {
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('usuario')
        return { path: '/login' }
      }
    }

    return true
  })

  return Router
})
