<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="opti-header">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title class="opti-title">
          OptimaTech
          <span class="opti-subtitle">Sistema Contable</span>
        </q-toolbar-title>

        <q-space />

        <q-badge :color="apiStatusColor" text-color="dark" class="q-mr-sm">
          {{ apiStatus }}
        </q-badge>

        <q-btn
          v-if="auth.estaAutenticado"
          flat
          dense
          round
          icon="account_circle"
          aria-label="Ver perfil"
          @click="abrirPerfil"
        >
          <q-tooltip>Mi perfil</q-tooltip>
        </q-btn>

        <q-btn
          v-if="auth.estaAutenticado"
          flat
          dense
          round
          class="opti-theme-toggle"
          :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
          :aria-label="
            $q.dark.isActive ? 'Activar modo claro' : 'Activar modo oscuro'
          "
          @click="toggleDark"
        >
          <q-tooltip>{{
            $q.dark.isActive ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'
          }}</q-tooltip>
        </q-btn>

        <q-btn
          v-if="auth.estaAutenticado"
          flat
          dense
          round
          color="negative"
          label="Salir"
          icon="logout"
          @click="logout"
        />
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="opti-drawer"
    >
      <q-list>
        <q-item clickable to="/" exact class="opti-home">
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Inicio</q-item-label>
            <q-item-label caption>Dashboard</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator spaced />

        <template v-for="section in menuSections" :key="section.title">
          <template v-if="itemsVisibles(section).length">
            <q-item-label header class="opti-menu-section">
              {{ section.title }}
            </q-item-label>

            <q-item
              v-for="item in itemsVisibles(section)"
              :key="item.to"
              clickable
              :to="item.to"
              exact
              active-class="menu-active"
            >
              <q-item-section avatar>
                <q-icon :name="item.icon" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ item.label }}</q-item-label>
                <q-item-label caption>{{ item.caption }}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </template>

        <q-separator spaced />

        <div class="q-pa-sm" v-if="auth.estaAutenticado">
          <div class="text-caption text-grey-7">
            {{ auth.usuario?.nombre_completo }} ({{
              auth.usuario?.rol_codigos?.join(', ')
            }})
          </div>
        </div>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-dialog v-model="perfilAbierto">
      <q-card class="perfil-card">
        <q-card-section class="perfil-header row items-center no-wrap">
          <q-avatar color="primary" text-color="white" icon="person" size="56px" />
          <div class="col q-ml-md perfil-heading">
            <div class="text-h6">Mi perfil</div>
            <div class="perfil-nombre">{{ auth.usuario?.nombre_completo || auth.usuario?.username }}</div>
            <div class="text-caption perfil-usuario">@{{ auth.usuario?.username }}</div>
          </div>
          <q-badge rounded :color="auth.usuario?.activo ? 'positive' : 'negative'" class="q-px-sm">
            {{ auth.usuario?.activo ? 'Activo' : 'Inactivo' }}
          </q-badge>
        </q-card-section>

        <q-separator />

        <q-card-section class="perfil-contenido">
          <q-banner v-if="errorPerfil" class="bg-red-1 text-red q-mb-md" rounded dense>
            {{ errorPerfil }}
          </q-banner>
          <div class="perfil-seccion-titulo">Información de la cuenta</div>
          <div class="row q-col-gutter-sm q-mb-md">
            <div class="col-12 col-sm-6">
              <div class="perfil-dato">
                <q-icon name="mail_outline" color="primary" />
                <div class="perfil-dato-texto">
                  <div class="text-caption text-grey-7">Correo electrónico</div>
                  <div class="perfil-valor">{{ auth.usuario?.email || 'Sin correo registrado' }}</div>
                </div>
              </div>
            </div>
            <div class="col-12 col-sm-6" v-if="auth.usuario?.sucursal_id">
              <div class="perfil-dato">
                <q-icon name="storefront" color="primary" />
                <div class="perfil-dato-texto">
                  <div class="text-caption text-grey-7">Sucursal asignada</div>
                  <div class="perfil-valor">Sucursal {{ auth.usuario.sucursal_id }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="perfil-seccion-titulo">Roles asignados</div>
          <div class="perfil-bloque q-mb-md">
            <div v-if="rolesPerfil.length" class="row q-gutter-sm">
              <q-chip v-for="rol in rolesPerfil" :key="rol.codigo" color="primary" text-color="white" icon="badge">
                {{ rol.nombre }}
              </q-chip>
            </div>
            <div v-else class="text-caption text-grey-7">Este usuario no tiene roles asignados.</div>
          </div>

          <div class="perfil-permisos-resumen row items-center no-wrap q-mb-sm">
            <q-avatar color="teal-1" text-color="primary" icon="verified_user" size="42px" />
            <div class="col q-ml-md">
              <div class="text-subtitle2">Accesos efectivos</div>
              <div class="text-caption text-grey-7">Permisos combinados de los roles asignados</div>
            </div>
            <q-badge color="primary" rounded class="q-px-sm">
              {{ auth.permisos.length }}
            </q-badge>
          </div>

          <q-expansion-item
            v-if="gruposPermisos.length"
            dense
            expand-separator
            icon="tune"
            label="Ver permisos por módulo"
            header-class="perfil-permisos-expansion"
          >
            <q-list class="perfil-lista-permisos">
              <q-expansion-item
                v-for="grupo in gruposPermisos"
                :key="grupo.codigo"
                dense
                :label="grupo.nombre"
                :caption="`${grupo.acciones.length} permiso(s)`"
                :icon="grupo.icono"
              >
                <div class="row q-gutter-xs q-px-md q-pb-md">
                  <q-chip
                    v-for="accion in grupo.acciones"
                    :key="accion.codigo"
                    dense
                    outline
                    color="primary"
                    icon="check_circle"
                  >
                    {{ accion.nombre }}
                  </q-chip>
                </div>
              </q-expansion-item>
            </q-list>
          </q-expansion-item>
          <div v-else class="perfil-bloque text-caption text-grey-7">
            No hay permisos efectivos asignados a esta cuenta.
          </div>

          <div v-if="cargandoPerfil" class="text-caption text-grey-7 q-mt-sm">
            Actualizando perfil desde el servidor…
          </div>
        </q-card-section>

        <q-separator />
        <q-card-actions align="right" class="q-px-md q-py-sm">
          <q-btn flat color="primary" label="Cerrar" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { MENU_SECTIONS } from '@/constants/menu.js'
import { API_BASE_URL } from '@/services/api.js'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const menuSections = MENU_SECTIONS
const leftDrawerOpen = ref(false)
const perfilAbierto = ref(false)
const cargandoPerfil = ref(false)
const errorPerfil = ref('')
const apiStatus = ref('API: verificando…')
const auth = useAuthStore()
const $q = useQuasar()
const router = useRouter()

const apiStatusColor = computed(() =>
  apiStatus.value.includes('en línea') ? 'green-3' : 'red-3'
)
const nombresRoles = {
  admin: 'Administrador',
  contador: 'Contador',
  auxiliar: 'Auxiliar contable',
  ventas: 'Ventas',
  compras: 'Compras',
  planilla: 'Planilla',
  auditor: 'Auditor'
}
const rolesPerfil = computed(() =>
  (auth.usuario?.rol_codigos || []).map(codigo => ({
    codigo,
    nombre: nombresRoles[codigo] || codigo
  }))
)
const nombresModulos = {
  asientos: 'Asientos contables',
  auditoria: 'Auditoría',
  compras: 'Compras',
  cuentas: 'Catálogo de cuentas',
  facturas: 'Facturación',
  informes: 'Informes',
  periodos: 'Períodos contables',
  planilla: 'Pago de salarios',
  reportes: 'Reportes',
  sucursales: 'Sucursales',
  usuarios: 'Usuarios'
}
const iconosModulos = {
  asientos: 'receipt_long',
  auditoria: 'history',
  compras: 'shopping_cart',
  cuentas: 'account_tree',
  facturas: 'request_quote',
  informes: 'analytics',
  periodos: 'date_range',
  planilla: 'payments',
  reportes: 'assessment',
  sucursales: 'storefront',
  usuarios: 'group'
}
const nombresAcciones = {
  aprobar: 'Aprobar',
  anular: 'Anular',
  cerrar: 'Cerrar',
  crear: 'Crear',
  editar: 'Editar',
  eliminar: 'Eliminar',
  ver: 'Consultar'
}
const gruposPermisos = computed(() => {
  const grupos = new Map()
  for (const permiso of auth.permisos) {
    const [moduloCodigo, accionCodigo] = String(permiso).split('.', 2)
    const codigo = moduloCodigo || 'otros'
    if (!grupos.has(codigo)) {
      grupos.set(codigo, {
        codigo,
        nombre: nombresModulos[codigo] || codigo,
        icono: iconosModulos[codigo] || 'lock',
        acciones: []
      })
    }
    const acciones = grupos.get(codigo).acciones
    if (!acciones.some(a => a.codigo === accionCodigo)) {
      acciones.push({
        codigo: accionCodigo || permiso,
        nombre: nombresAcciones[accionCodigo] || accionCodigo || permiso
      })
    }
  }
  return [...grupos.values()].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'))
})

/** Ítems del menú visibles según los permisos del usuario autenticado. */
function itemsVisibles(section) {
  return section.items.filter(item => {
    if (!item.permiso) return true
    return Array.isArray(item.permiso)
      ? item.permiso.some(permiso => auth.tienePermiso(permiso))
      : auth.tienePermiso(item.permiso)
  })
}

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function toggleDark() {
  const nuevoModo = !$q.dark.isActive
  $q.dark.set(nuevoModo)
  localStorage.setItem('opti-theme', nuevoModo ? 'dark' : 'light')
}

async function abrirPerfil() {
  perfilAbierto.value = true
  errorPerfil.value = ''
  cargandoPerfil.value = true
  try {
    await auth.actualizarPerfil()
  } catch (e) {
    errorPerfil.value = `Mostrando los datos guardados de la sesión. No se pudo actualizar: ${e.message}`
  } finally {
    cargandoPerfil.value = false
  }
}

async function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/health`)
    apiStatus.value = res.ok ? 'API: en línea' : 'API: sin respuesta'
  } catch {
    apiStatus.value = 'API: sin conexión'
  }
})
</script>

<style scoped>
.perfil-card {
  width: 620px;
  max-width: 95vw;
  overflow: hidden;
  border-radius: 16px;
}

.perfil-header {
  min-height: 112px;
  padding: 22px 24px;
  color: #f5fbff;
  background: linear-gradient(112deg, #142a40 0%, #1b435b 72%, #167467 100%);
}

.perfil-header :deep(.text-grey-7),
.perfil-usuario {
  color: rgba(242, 249, 255, 0.72) !important;
}

.perfil-nombre {
  margin-top: 2px;
  font-size: 14px;
  font-weight: 600;
}

.perfil-contenido {
  max-height: min(68vh, 620px);
  overflow-y: auto;
  padding: 22px 24px;
}

.perfil-contenido :deep(.text-grey-7) {
  color: var(--opti-muted) !important;
}

.perfil-seccion-titulo {
  margin: 0 0 10px;
  color: var(--opti-text);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.perfil-dato,
.perfil-bloque,
.perfil-permisos-resumen {
  min-height: 62px;
  border: 1px solid var(--opti-border);
  border-radius: 11px;
  background: var(--opti-page);
}

.perfil-dato {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
}

.perfil-dato > .q-icon {
  font-size: 21px;
}

.perfil-dato-texto {
  min-width: 0;
}

.perfil-valor {
  overflow-wrap: anywhere;
  font-size: 13px;
  font-weight: 550;
}

.perfil-bloque {
  padding: 12px;
}

.perfil-permisos-resumen {
  padding: 10px 13px;
}

:deep(.perfil-permisos-expansion) {
  min-height: 46px;
  border-radius: 9px;
  background: var(--opti-page);
  font-weight: 600;
}

.perfil-lista-permisos {
  margin-top: 6px;
  border: 1px solid var(--opti-border);
  border-radius: 10px;
}

.perfil-lista-permisos :deep(.q-item) {
  min-height: 48px;
}

@media (max-width: 599px) {
  .perfil-header,
  .perfil-contenido {
    padding-right: 16px;
    padding-left: 16px;
  }
}
</style>
