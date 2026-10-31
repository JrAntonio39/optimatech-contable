/**
 * Mapa único del menú de OptimaTech.
 * Lo usan MainLayout (drawer lateral) e IndexPage (dashboard con botones).
 * icon: nombre de Material Icons. to: ruta del router.
 * permiso: código "modulo.accion" que el usuario necesita para ver el módulo.
 */
export const MENU_SECTIONS = [
  {
    title: 'Catálogo y registro',
    items: [
      {
        label: 'Catálogo de Cuentas',
        caption: 'Agregar y ver cuentas',
        icon: 'account_tree',
        to: '/catalogo',
        permiso: 'cuentas.ver'
      },
      {
        label: 'Transacciones',
        caption: 'Normal, Ajuste y Cierre',
        icon: 'edit_note',
        to: '/transacciones',
        permiso: 'asientos.crear'
      },
      {
        label: 'Balance Inicial',
        caption: 'Asiento de apertura',
        icon: 'play_for_work',
        to: '/balance-inicial',
        permiso: 'asientos.ver'
      }
    ]
  },
  {
    title: 'Libros y reportes',
    items: [
      {
        label: 'Libro Diario',
        caption: 'Todas las partidas',
        icon: 'book',
        to: '/libro-diario',
        permiso: 'asientos.ver'
      },
      {
        label: 'Libro Mayor',
        caption: 'Mayorización por cuenta',
        icon: 'library_books',
        to: '/libro-mayor',
        permiso: 'reportes.ver'
      },
      {
        label: 'Balanza de Comprobación',
        caption: 'Sumas y saldos',
        icon: 'balance',
        to: '/balanza',
        permiso: 'reportes.ver'
      },
      {
        label: 'Estado de resultados',
        caption: 'Estado de resultados',
        icon: 'trending_up',
        to: '/resultados',
        permiso: 'reportes.ver'
      },
      {
        label: 'Balance General',
        caption: 'Situación financiera',
        icon: 'account_balance_wallet',
        to: '/balance-general',
        permiso: 'reportes.ver'
      }
    ]
  },
  {
    title: 'Plus',
    items: [
      {
        label: 'Facturación',
        caption: 'Emitir y consultar facturas',
        icon: 'receipt_long',
        to: '/facturacion',
        permiso: 'facturas.ver'
      },
      {
        label: 'Clientes',
        caption: 'Datos fiscales y contactos',
        icon: 'groups',
        to: '/clientes',
        permiso: 'facturas.ver'
      },
      {
        label: 'Compras',
        caption: 'Registro de compras',
        icon: 'shopping_cart',
        to: '/compras',
        permiso: 'compras.ver'
      },
      {
        label: 'Proveedores',
        caption: 'Datos fiscales y contactos',
        icon: 'local_shipping',
        to: '/proveedores',
        permiso: 'compras.ver'
      },
      {
        label: 'Empleados',
        caption: 'Personal, cargos y sucursales',
        icon: 'badge',
        to: '/empleados',
        permiso: 'planilla.ver'
      },
      {
        label: 'Pago de Salarios',
        caption: 'Planilla mensual',
        icon: 'payments',
        to: '/planilla',
        permiso: 'planilla.ver'
      }
    ]
  },
  {
    title: 'Control del sistema',
    items: [
      {
        label: 'Control y auditoría',
        caption: 'Aprobaciones, periodos e historial',
        icon: 'manage_accounts',
        to: '/control',
        permiso: ['asientos.ver', 'asientos.aprobar', 'periodos.ver', 'periodos.crear', 'periodos.cerrar', 'sucursales.ver', 'auditoria.ver']
      },
      {
        label: 'Usuarios y roles',
        caption: 'Permisos y accesos',
        icon: 'group',
        to: '/usuarios',
        permiso: 'usuarios.ver'
      }
    ]
  }
]
