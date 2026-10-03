/**
 * Mapa único del menú de OptimaTech.
 * Lo usan MainLayout (drawer lateral) e IndexPage (dashboard con botones).
 * icon: nombre de Material Icons. to: ruta del router.
 */
export const MENU_SECTIONS = [
  {
    title: 'Catálogo y registro',
    items: [
      {
        label: 'Catálogo de Cuentas',
        caption: 'Agregar y ver cuentas',
        icon: 'account_tree',
        to: '/catalogo'
      },
      {
        label: 'Transacciones',
        caption: 'Normal, Ajuste y Cierre',
        icon: 'edit_note',
        to: '/transacciones'
      },
      {
        label: 'Balance Inicial',
        caption: 'Asiento de apertura',
        icon: 'play_for_work',
        to: '/balance-inicial'
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
        to: '/libro-diario'
      },
      {
        label: 'Libro Mayor',
        caption: 'Mayorización por cuenta',
        icon: 'library_books',
        to: '/libro-mayor'
      },
      {
        label: 'Balanza de Comprobación',
        caption: 'Sumas y saldos',
        icon: 'balance',
        to: '/balanza'
      },
      {
        label: 'Pérdidas y Ganancias',
        caption: 'Estado de resultados',
        icon: 'trending_up',
        to: '/resultados'
      },
      {
        label: 'Balance General',
        caption: 'Situación financiera',
        icon: 'account_balance_wallet',
        to: '/balance-general'
      }
    ]
  },
  {
    title: 'Plus',
    items: [
      {
        label: 'Facturación Electrónica',
        caption: 'Facturas y clientes',
        icon: 'receipt_long',
        to: '/facturacion'
      },
      {
        label: 'Compras y Proveedores',
        caption: 'Libro de compras',
        icon: 'shopping_cart',
        to: '/compras'
      },
      {
        label: 'Pago de Salarios',
        caption: 'Planilla mensual',
        icon: 'payments',
        to: '/planilla'
      }
    ]
  }
]
