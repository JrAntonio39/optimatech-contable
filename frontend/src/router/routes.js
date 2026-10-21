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
      { path: 'catalogo', component: () => import('@/pages/CatalogoPage.vue') },
      {
        path: 'transacciones',
        component: () => import('@/pages/TransaccionesPage.vue')
      },
      {
        path: 'balance-inicial',
        component: () => import('@/pages/BalanceInicialPage.vue')
      },
      {
        path: 'libro-diario',
        component: () => import('@/pages/LibroDiarioPage.vue')
      },
      {
        path: 'libro-mayor',
        component: () => import('@/pages/LibroMayorPage.vue')
      },
      { path: 'balanza', component: () => import('@/pages/BalanzaPage.vue') },
      {
        path: 'resultados',
        component: () => import('@/pages/ResultadosPage.vue')
      },
      {
        path: 'balance-general',
        component: () => import('@/pages/BalanceGeneralPage.vue')
      },
      {
        path: 'facturacion',
        component: () => import('@/pages/FacturacionPage.vue')
      },
      { path: 'compras', component: () => import('@/pages/ComprasPage.vue') },
      { path: 'planilla', component: () => import('@/pages/PlanillaPage.vue') },
      {
        path: 'control',
        component: () => import('@/pages/ControlPage.vue')
      },
      {
        path: 'usuarios',
        component: () => import('@/pages/UsuariosPage.vue')
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
