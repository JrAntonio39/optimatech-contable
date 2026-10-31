const routes = [
  {
    path: '/login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', component: () => import('@/pages/IndexPage.vue') },
      { path: 'catalogo', component: () => import('@/pages/CatalogoPage.vue'), meta: { permiso: 'cuentas.ver' } },
      {
        path: 'transacciones',
        component: () => import('@/pages/TransaccionesPage.vue'), meta: { permiso: 'asientos.crear' }
      },
      {
        path: 'balance-inicial',
        component: () => import('@/pages/BalanceInicialPage.vue'), meta: { permiso: 'asientos.ver' }
      },
      {
        path: 'libro-diario',
        component: () => import('@/pages/LibroDiarioPage.vue'), meta: { permiso: 'asientos.ver' }
      },
      {
        path: 'libro-mayor',
        component: () => import('@/pages/LibroMayorPage.vue'), meta: { permiso: 'reportes.ver' }
      },
      { path: 'balanza', component: () => import('@/pages/BalanzaPage.vue'), meta: { permiso: 'reportes.ver' } },
      {
        path: 'resultados',
        component: () => import('@/pages/ResultadosPage.vue'), meta: { permiso: 'reportes.ver' }
      },
      {
        path: 'balance-general',
        component: () => import('@/pages/BalanceGeneralPage.vue'), meta: { permiso: 'reportes.ver' }
      },
      {
        path: 'facturacion',
        component: () => import('@/pages/FacturacionPage.vue'), meta: { permiso: 'facturas.ver' }
      },
      { path: 'clientes', component: () => import('@/pages/ClientesPage.vue'), meta: { permiso: 'facturas.ver' } },
      { path: 'proveedores', component: () => import('@/pages/ProveedoresPage.vue'), meta: { permiso: 'compras.ver' } },
      { path: 'compras', component: () => import('@/pages/ComprasPage.vue'), meta: { permiso: 'compras.ver' } },
      { path: 'empleados', component: () => import('@/pages/EmpleadosPage.vue'), meta: { permiso: 'planilla.ver' } },
      { path: 'planilla', component: () => import('@/pages/PlanillaPage.vue'), meta: { permiso: 'planilla.ver' } },
      {
        path: 'control',
        component: () => import('@/pages/ControlPage.vue'), meta: { permisos: ['asientos.ver', 'asientos.aprobar', 'periodos.ver', 'periodos.crear', 'periodos.cerrar', 'sucursales.ver', 'auditoria.ver'] }
      },
      {
        path: 'usuarios',
        component: () => import('@/pages/UsuariosPage.vue'), meta: { permiso: 'usuarios.ver' }
      }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue')
  }
]

export default routes
