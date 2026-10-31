<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div>
        <div class="text-h5">Proveedores</div>
        <div class="text-caption text-grey-7">Datos fiscales, contactos y cuenta por pagar</div>
      </div>
      <q-space />
      <q-btn v-if="auth.tienePermiso('compras.crear')" color="primary" icon="person_add" label="Nuevo proveedor" @click="abrirNuevo" />
    </div>

    <q-banner v-if="error && !dialog" class="bg-red-1 text-red q-mb-md" rounded>{{ error }}</q-banner>
    <q-banner v-if="mensaje" class="bg-blue-1 text-blue-10 q-mb-md" rounded>{{ mensaje }}</q-banner>
    <q-card class="opti-card">
      <q-table :rows="proveedoresVisibles" :columns="columns" row-key="id" :loading="cargando" :filter="filtro" no-data-label="No hay proveedores en esta vista">
        <template #top-right>
          <div class="row q-col-gutter-sm">
            <div class="col-auto"><q-select v-model="filtroEstado" :options="opcionesEstado" dense outlined emit-value map-options label="Estado" style="min-width: 140px" /></div>
            <div class="col-auto"><q-input v-model="filtro" dense outlined debounce="250" placeholder="Buscar proveedor" clearable><template #prepend><q-icon name="search" /></template></q-input></div>
          </div>
        </template>
        <template #body-cell-estado="p">
          <q-td :props="p"><q-badge :color="p.value === 'ACTIVO' ? 'positive' : 'grey'">{{ p.value === 'ACTIVO' ? 'Activo' : 'Inactivo' }}</q-badge></q-td>
        </template>
        <template #body-cell-acciones="p">
          <q-td :props="p" class="text-right">
            <q-btn v-if="p.row.estado === 'ACTIVO' && auth.tienePermiso('compras.editar')" flat dense color="primary" icon="edit" label="Editar" @click="abrirEdicion(p.row)" />
            <q-btn v-if="p.row.estado === 'ACTIVO' && auth.tienePermiso('compras.editar')" flat dense color="negative" icon="person_off" label="Dar de baja" :loading="estadoProcesando === p.row.id" :disable="estadoProcesando !== null" @click="confirmarEstado(p.row, false)" />
            <q-btn v-if="p.row.estado !== 'ACTIVO' && auth.tienePermiso('compras.editar')" flat dense color="positive" icon="person_add_alt" label="Reactivar" :loading="estadoProcesando === p.row.id" :disable="estadoProcesando !== null" @click="confirmarEstado(p.row, true)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialog" @hide="error = ''">
      <q-card style="width: 700px; max-width: 96vw">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editando ? 'Editar proveedor' : 'Nuevo proveedor' }}</div>
          <q-space /><q-btn v-close-popup flat round icon="close" />
        </q-card-section>
        <q-card-section v-if="error" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ error }}</q-banner></q-card-section>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12 col-sm-4"><q-input v-model="form.codigo" label="Código" placeholder="Ej.: PRO-001" hint="Opcional: déjalo vacío para generar el siguiente código PRO." maxlength="10" outlined dense /></div>
          <div class="col-12 col-sm-8"><q-input v-model="form.nombre" label="Nombre o razón social *" placeholder="Ej.: Distribuidora Ejemplo, S.A. de C.V." maxlength="150" outlined dense /></div>
          <div class="col-12 col-sm-6"><q-input :model-value="form.nit" label="NIT *" placeholder="Ej.: 0614-010199-001-1" maxlength="17" inputmode="numeric" hint="Obligatorio: NIT de 14 dígitos o DUI de 9; los guiones se agregan solos." outlined dense @update:model-value="actualizarNit" /></div>
          <div class="col-12 col-sm-6"><q-input :model-value="form.nrc" label="NRC *" placeholder="Ej.: 123456-7" maxlength="9" inputmode="numeric" hint="Obligatorio: de 2 a 8 dígitos; se guarda sin guiones." outlined dense @update:model-value="actualizarNrc" /></div>
          <div class="col-12"><q-input v-model="form.direccion" label="Dirección *" placeholder="Ej.: Colonia Escalón, San Salvador" maxlength="250" outlined dense /></div>
          <div class="col-12 col-sm-6"><q-input :model-value="form.telefono" type="tel" label="Teléfono" placeholder="2222-3333" maxlength="15" hint="Opcional: 8 dígitos; agrega +503 si incluyes el código de país." outlined dense @update:model-value="actualizarTelefono" /></div>
          <div class="col-12 col-sm-6"><q-input v-model="form.email" type="email" label="Correo" placeholder="compras@proveedor.com" maxlength="100" outlined dense /></div>
          <div class="col-12"><q-select v-model="form.cuenta_codigo" :options="cuentasPagar" option-value="codigo" :option-label="c => `${c.codigo} · ${c.nombre}`" emit-value map-options label="Cuenta por pagar" outlined dense /></div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn color="primary" :label="editando ? 'Guardar cambios' : 'Guardar proveedor'" :loading="guardando" @click="guardar" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth.js'
import { api } from '@/services/api.js'
import { operacionesService } from '@/services/operacionesService.js'

const $q = useQuasar()
const auth = useAuthStore()
const proveedores = ref([])
const cuentasPagar = ref([])
const filtro = ref('')
const filtroEstado = ref('ACTIVO')
const cargando = ref(false)
const guardando = ref(false)
const estadoProcesando = ref(null)
const dialog = ref(false)
const editando = ref(false)
const proveedorId = ref(null)
const error = ref('')
const mensaje = ref('')
const nuevo = () => ({ codigo: '', nombre: '', nit: '', nrc: '', direccion: '', telefono: '', email: '', cuenta_codigo: '' })
const form = ref(nuevo())
const opcionesEstado = [
  { label: 'Activos', value: 'ACTIVO' },
  { label: 'Inactivos', value: 'INACTIVO' },
  { label: 'Todos', value: 'TODOS' }
]
const proveedoresVisibles = computed(() => filtroEstado.value === 'TODOS' ? proveedores.value : proveedores.value.filter(row => row.estado === filtroEstado.value))
const columns = [
  { name: 'codigo', label: 'Código', field: 'codigo', align: 'left', sortable: true },
  { name: 'nombre', label: 'Nombre / razón social', field: 'nombre', align: 'left', sortable: true },
  { name: 'nit', label: 'NIT', field: row => formatearNit(row.nit) },
  { name: 'nrc', label: 'NRC', field: row => formatearNrc(row.nrc) },
  { name: 'telefono', label: 'Teléfono', field: row => formatearTelefono(row.telefono) },
  { name: 'estado', label: 'Estado', field: 'estado' },
  { name: 'acciones', label: 'Acciones', field: 'id', align: 'right' }
]

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const [result, accounts] = await Promise.all([operacionesService.proveedores(), api.get('/api/cuentas?q=2.1.1.')])
    proveedores.value = result.proveedores
    const parents = new Set(accounts.cuentas.map(account => account.codigo_padre))
    cuentasPagar.value = accounts.cuentas.filter(account => account.codigo.startsWith('2.1.1.') && !parents.has(account.codigo))
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

function abrirNuevo() {
  error.value = ''
  mensaje.value = ''
  form.value = nuevo()
  form.value.cuenta_codigo = cuentasPagar.value.find(account => account.codigo === '2.1.1.01')?.codigo || cuentasPagar.value[0]?.codigo || ''
  editando.value = false
  proveedorId.value = null
  dialog.value = true
}

function abrirEdicion(row) {
  error.value = ''
  mensaje.value = ''
  editando.value = true
  proveedorId.value = row.id
  form.value = { codigo: row.codigo, nombre: row.nombre, nit: row.nit || '', nrc: row.nrc || '', direccion: row.direccion || '', telefono: row.telefono || '', email: row.email || '', cuenta_codigo: row.cuenta_codigo || '' }
  actualizarNit(row.nit || '')
  actualizarNrc(row.nrc || '')
  actualizarTelefono(row.telefono || '')
  dialog.value = true
}

function actualizarNit(value) {
  const digits = String(value || '').replace(/\D/g, '').slice(0, 14)
  if (digits.length <= 8) form.value.nit = digits
  else if (digits.length === 9) form.value.nit = `${digits.slice(0, 8)}-${digits.slice(8)}`
  else form.value.nit = `${digits.slice(0, 4)}-${digits.slice(4, 10)}${digits.length > 10 ? `-${digits.slice(10, 13)}` : ''}${digits.length > 13 ? `-${digits.slice(13, 14)}` : ''}`
}

function actualizarNrc(value) {
  const digits = String(value || '').replace(/\D/g, '').slice(0, 8)
  form.value.nrc = digits.length > 6 ? `${digits.slice(0, 6)}-${digits.slice(6)}` : digits
}

function actualizarTelefono(value) {
  const raw = String(value || '').trim()
  const internacional = raw.startsWith('+')
  let digits = raw.replace(/\D/g, '')
  if (internacional && digits.startsWith('503')) digits = digits.slice(3)
  digits = digits.slice(0, 8)
  const local = digits.length > 4 ? `${digits.slice(0, 4)}-${digits.slice(4)}` : digits
  form.value.telefono = internacional ? `+503 ${local}`.trimEnd() : local
}

function formatearNit(value) {
  if (!value) return '—'
  const digits = String(value).replace(/\D/g, '')
  if (digits.length === 9) return `${digits.slice(0, 8)}-${digits.slice(8)}`
  if (digits.length === 14) return `${digits.slice(0, 4)}-${digits.slice(4, 10)}-${digits.slice(10, 13)}-${digits.slice(13)}`
  return String(value)
}

function formatearNrc(value) {
  if (!value) return '—'
  const digits = String(value).replace(/\D/g, '')
  return digits.length > 6 ? `${digits.slice(0, 6)}-${digits.slice(6)}` : digits
}

function formatearTelefono(value) {
  if (!value) return '—'
  const raw = String(value)
  const internacional = raw.startsWith('+')
  let digits = raw.replace(/\D/g, '')
  if (internacional && digits.startsWith('503')) digits = digits.slice(3)
  const local = digits.length > 4 ? `${digits.slice(0, 4)}-${digits.slice(4, 8)}` : digits
  return internacional ? `+503 ${local}` : local
}

function validar() {
  const codigo = String(form.value.codigo || '').trim().toUpperCase()
  const nombre = String(form.value.nombre || '').trim()
  const nit = String(form.value.nit || '').trim()
  const nrc = String(form.value.nrc || '').trim()
  const direccion = String(form.value.direccion || '').trim()
  const telefono = String(form.value.telefono || '').trim()
  const email = String(form.value.email || '').trim().toLowerCase()
  if (codigo && !/^PRO-\d{3,6}$/.test(codigo)) { error.value = 'El código debe tener el formato PRO-001 con 3 a 6 dígitos; también puedes dejarlo vacío para generarlo.'; return null }
  if (nombre.length < 2) { error.value = 'Escribe el nombre o razón social del proveedor.'; return null }
  if (!/^(?:\d{9}|\d{14}|\d{8}-\d|\d{4}-\d{6}-\d{3}-\d)$/.test(nit)) { error.value = 'El NIT es obligatorio: escribe 9 dígitos (formato DUI) o 14. Ejemplo: 0614-010199-001-1.'; return null }
  if (!/^(?:\d{2,8}|\d{2,7}-\d)$/.test(nrc)) { error.value = 'El NRC es obligatorio y debe tener de 2 a 8 dígitos. Ejemplo: 123456-7.'; return null }
  if (direccion.length < 5) { error.value = 'La dirección es obligatoria y debe tener al menos 5 caracteres.'; return null }
  const phoneDigits = telefono.replace(/\D/g, '')
  if (telefono && (!/^[+0-9()\-\s]+$/.test(telefono) || ![8, 11].includes(phoneDigits.length) || (phoneDigits.length === 11 && !phoneDigits.startsWith('503')))) { error.value = 'El teléfono debe tener 8 dígitos, o 11 si comienza con 503.'; return null }
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { error.value = 'El correo debe tener un formato como compras@proveedor.com.'; return null }
  return { ...form.value, codigo: codigo || null, nombre, nit: nit.replace(/[-\s]/g, ''), nrc: nrc.replace(/-/g, ''), direccion, telefono: telefono ? (phoneDigits.length === 11 ? `+${phoneDigits}` : phoneDigits) : null, email: email || null }
}

async function guardar() {
  error.value = ''
  const payload = validar()
  if (!payload) return
  guardando.value = true
  try {
    const result = editando.value
      ? await operacionesService.actualizarProveedor(proveedorId.value, payload)
      : await operacionesService.crearProveedor(payload)
    dialog.value = false
    mensaje.value = editando.value ? 'Datos del proveedor actualizados.' : `Proveedor ${result.codigo} creado.`
    await cargar()
  } catch (err) {
    error.value = err.message
  } finally {
    guardando.value = false
  }
}

function confirmarEstado(row, activar) {
  const accion = activar ? 'reactivar' : 'dar de baja'
  $q.dialog({ title: `${activar ? 'Reactivar' : 'Dar de baja'} proveedor`, message: `¿Deseas ${accion} a ${row.nombre}? ${activar ? 'Volverá a estar disponible para nuevas compras.' : 'Se ocultará de nuevas compras; el historial se conservará.'}`, cancel: true, persistent: true })
    .onOk(() => { void ejecutarCambioEstado(row, activar) })
}

async function ejecutarCambioEstado(row, activar) {
  error.value = ''
  mensaje.value = ''
  estadoProcesando.value = row.id
  try {
    if (activar) await operacionesService.activarProveedor(row.id)
    else await operacionesService.darDeBajaProveedor(row.id)
    await cargar()
    mensaje.value = activar ? `${row.nombre} fue reactivado.` : `${row.nombre} fue dado de baja. Su historial se conservó.`
  } catch (err) {
    error.value = err.message || `No se pudo ${activar ? 'reactivar' : 'dar de baja'} al proveedor.`
  } finally {
    estadoProcesando.value = null
  }
}

onMounted(cargar)
</script>
