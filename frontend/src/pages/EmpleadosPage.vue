<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div>
        <div class="text-h5">Empleados</div>
        <div class="text-caption text-grey-7">Personal, cargos y datos laborales de OptimaTech</div>
      </div>
      <q-space />
      <q-btn v-if="auth.tienePermiso('planilla.crear')" color="primary" icon="person_add" label="Nuevo empleado" @click="abrirNuevo" />
    </div>

    <q-banner v-if="error&&!dialog" class="bg-red-1 text-red q-mb-md" rounded>{{ error }}</q-banner>
    <q-banner v-if="mensaje" class="bg-blue-1 text-blue-10 q-mb-md" rounded>{{ mensaje }}</q-banner>
    <q-card class="opti-card">
      <q-table :rows="empleadosVisibles" :columns="columns" row-key="id" :loading="cargando" :filter="filtro" no-data-label="No hay empleados en esta vista">
        <template #top-right>
          <div class="row q-col-gutter-sm">
            <div class="col-auto"><q-select v-model="filtroEstado" :options="opcionesEstado" dense outlined emit-value map-options label="Estado" style="min-width: 140px" /></div>
            <div class="col-auto"><q-input v-model="filtro" dense outlined debounce="250" placeholder="Buscar empleado" clearable>
              <template #prepend><q-icon name="search" /></template>
            </q-input></div>
          </div>
        </template>
        <template #body-cell-salario_base="p"><q-td :props="p">{{ dinero(p.value) }}</q-td></template>
        <template #body-cell-estado="p"><q-td :props="p"><q-badge :color="p.value==='ACTIVO'?'positive':'grey'">{{ p.value==='ACTIVO'?'Activo':'Inactivo' }}</q-badge></q-td></template>
        <template #body-cell-acciones="p">
          <q-td :props="p" class="text-right">
            <q-btn v-if="p.row.estado==='ACTIVO'&&auth.tienePermiso('planilla.editar')" flat dense color="primary" icon="edit" label="Editar" @click="abrirEdicion(p.row)" />
            <q-btn v-if="p.row.estado==='ACTIVO'&&auth.tienePermiso('planilla.editar')" flat dense color="negative" icon="person_off" label="Dar de baja" :loading="estadoProcesando===p.row.id" :disable="estadoProcesando!==null" @click="cambiarEstado(p.row,false)" />
            <q-btn v-if="p.row.estado!=='ACTIVO'&&auth.tienePermiso('planilla.editar')" flat dense color="positive" icon="person_add_alt" label="Reactivar" :loading="estadoProcesando===p.row.id" :disable="estadoProcesando!==null" @click="cambiarEstado(p.row,true)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialog">
      <q-card style="width:760px;max-width:96vw">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editando ? 'Editar empleado' : 'Nuevo empleado' }}</div>
          <q-space /><q-btn v-close-popup flat round icon="close" />
        </q-card-section>
        <q-card-section v-if="error" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ error }}</q-banner></q-card-section>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12 col-sm-4">
            <q-input v-model="form.codigo" label="Código del empleado" :placeholder="editando ? '' : 'Ej.: EMP-003'" :hint="editando ? 'El código existente se conserva.' : 'Opcional: déjalo vacío y se asignará el siguiente código.'" :disable="editando" maxlength="10" outlined dense @update:model-value="limpiarError" />
          </div>
          <div class="col-12 col-sm-4"><q-input v-model="form.nombres" label="Nombres" placeholder="Ej.: Ana María" maxlength="100" outlined dense @update:model-value="limpiarError" /></div>
          <div class="col-12 col-sm-4"><q-input v-model="form.apellidos" label="Apellidos" placeholder="Ej.: López García" maxlength="100" outlined dense @update:model-value="limpiarError" /></div>
          <div class="col-12 col-sm-6"><q-input v-model="form.dui" label="DUI (obligatorio)" placeholder="Ej.: 01234567-8" hint="Identificación personal, no licencia de conducir." mask="########-#" fill-mask="" inputmode="numeric" outlined dense @update:model-value="limpiarError" /></div>
          <div class="col-12 col-sm-6"><q-input v-model="form.nit" label="NIT (opcional)" placeholder="Ej.: 0614-010199-001-1" hint="Escribe los números; los guiones se agregan automáticamente." mask="####-######-###-#" fill-mask="" inputmode="numeric" outlined dense @update:model-value="limpiarError" /></div>
          <div class="col-12 col-sm-6"><q-select v-model="form.cargo" :options="cargosOpciones" option-value="value" option-label="label" emit-value map-options label="Cargo o puesto" outlined dense @update:model-value="limpiarError" /></div>
          <div v-if="form.cargo==='OTRO'" class="col-12 col-sm-6"><q-input v-model="cargoOtro" label="Especifica el cargo" placeholder="Ej.: Especialista en ciberseguridad" maxlength="100" outlined dense @update:model-value="limpiarError" /></div>
          <div class="col-12 col-sm-6"><q-input v-model="form.salario_base" type="number" min="0.01" step="0.01" label="Salario base mensual ($)" placeholder="Ej.: 850.00" hint="Monto positivo, hasta 2 decimales." outlined dense @update:model-value="limpiarError" /></div>
          <div class="col-12 col-sm-6"><q-input v-model="form.fecha_ingreso" type="date" label="Fecha de ingreso" outlined dense @update:model-value="limpiarError" /></div>
          <div class="col-12 col-sm-6"><q-select v-model="form.sucursal_id" :options="sucursales" option-value="id" option-label="nombre" emit-value map-options label="Sucursal (obligatoria)" outlined dense @update:model-value="limpiarError" /></div>
        </q-card-section>
        <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup /><q-btn color="primary" :label="editando ? 'Guardar cambios' : 'Guardar empleado'" :loading="guardando" @click="guardar" /></q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth.js'
import { api } from '@/services/api.js'

const $q = useQuasar()
const auth = useAuthStore()
const empleados = ref([])
const sucursales = ref([])
const cargos = ref([])
const filtro = ref('')
const filtroEstado = ref('ACTIVO')
const cargando = ref(false)
const guardando = ref(false)
const estadoProcesando = ref(null)
const error = ref('')
const mensaje = ref('')
const dialog = ref(false)
const editando = ref(false)
const employeeId = ref(null)
const cargoOtro = ref('')
const hoy = () => new Date().toLocaleDateString('sv-SE')
const blank = () => ({ codigo: '', nombres: '', apellidos: '', dui: '', nit: '', cargo: '', salario_base: '', fecha_ingreso: hoy(), sucursal_id: null })
const form = ref(blank())
const cargosOpciones = computed(() => [...cargos.value.map(c => ({ label: c.nombre, value: c.nombre })), { label: 'Otro (especificar)', value: 'OTRO' }])
const opcionesEstado = [
  { label: 'Activos', value: 'ACTIVO' },
  { label: 'Inactivos', value: 'INACTIVO' },
  { label: 'Todos', value: 'TODOS' }
]
const empleadosVisibles = computed(() => filtroEstado.value === 'TODOS' ? empleados.value : empleados.value.filter(employee => employee.estado === filtroEstado.value))
const columns = [
  { name: 'codigo', label: 'Código', field: 'codigo', align: 'left' },
  { name: 'nombre', label: 'Empleado', field: r => `${r.nombres} ${r.apellidos}` },
  { name: 'dui', label: 'DUI', field: r => r.dui || '—' },
  { name: 'cargo', label: 'Cargo', field: 'cargo' },
  { name: 'salario_base', label: 'Salario mensual', field: 'salario_base', align: 'right' },
  { name: 'sucursal', label: 'Sucursal', field: r => sucursales.value.find(s => s.id === r.sucursal_id)?.nombre || '—' },
  { name: 'estado', label: 'Estado', field: 'estado' },
  { name: 'acciones', label: 'Acciones', field: 'id', align: 'right' }
]
const dinero = value => new Intl.NumberFormat('es-SV', { style: 'currency', currency: 'USD' }).format(Number(value) || 0)

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const [e, s, c] = await Promise.all([api.get('/api/empleados'), api.get('/api/sucursales'), api.get('/api/cargos-empleado')])
    empleados.value = e.empleados
    sucursales.value = s.sucursales
    cargos.value = c.cargos
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

function abrirNuevo() {
  error.value = ''
  mensaje.value = ''
  form.value = blank()
  cargoOtro.value = ''
  editando.value = false
  employeeId.value = null
  dialog.value = true
}

function abrirEdicion(row) {
  error.value = ''
  mensaje.value = ''
  editando.value = true
  employeeId.value = row.id
  const cargoExiste = cargos.value.some(c => c.nombre === row.cargo)
  cargoOtro.value = cargoExiste ? '' : row.cargo
  form.value = { codigo: row.codigo, nombres: row.nombres, apellidos: row.apellidos, dui: row.dui || '', nit: row.nit || '', cargo: cargoExiste ? row.cargo : 'OTRO', salario_base: String(row.salario_base), fecha_ingreso: String(row.fecha_ingreso).slice(0, 10), sucursal_id: row.sucursal_id }
  dialog.value = true
}

function limpiarError() {
  error.value = ''
}

async function guardar() {
  error.value = ''
  const code = String(form.value.codigo || '').trim().toUpperCase()
  const cargo = form.value.cargo === 'OTRO' ? cargoOtro.value.trim() : String(form.value.cargo || '').trim()
  if (!editando.value && code && !/^EMP-\d{3,6}$/.test(code)) { error.value = 'Usa el formato EMP-003 para el código, o déjalo vacío para que se genere.'; return }
  if (!form.value.nombres.trim() || !form.value.apellidos.trim() || cargo.length < 2) { error.value = 'Completa nombres, apellidos y selecciona o especifica el cargo.'; return }
  const duiDigits = String(form.value.dui || '').replace(/\D/g, '')
  if (duiDigits.length !== 9) { error.value = 'El DUI es obligatorio y debe tener 9 dígitos. Ejemplo: 01234567-8.'; return }
  const dui = `${duiDigits.slice(0, 8)}-${duiDigits[8]}`
  if (!form.value.sucursal_id) { error.value = 'Selecciona la sucursal asignada al empleado.'; return }
  const nit = String(form.value.nit || '').trim()
  if (nit && !/^(?:\d{9}|\d{14}|\d{8}-\d|\d{4}-\d{6}-\d{3}-\d)$/.test(nit)) { error.value = 'El NIT debe tener 9 o 14 dígitos. Ejemplo: 0614-010199-001-1.'; return }
  if (!(Number(form.value.salario_base) > 0) || !/^\d+(?:\.\d{1,2})?$/.test(String(form.value.salario_base))) { error.value = 'El salario debe ser mayor que cero y tener máximo 2 decimales.'; return }
  guardando.value = true
  try {
    const payload = { ...form.value, codigo: editando.value ? undefined : (code || null), cargo, salario_base: Number(form.value.salario_base), dui: dui || null, nit: nit || null }
    const result = editando.value ? await api.put(`/api/empleados/${employeeId.value}`, payload) : await api.post('/api/empleados', payload)
    dialog.value = false
    mensaje.value = editando.value ? 'Cambios del empleado guardados.' : `Empleado ${result.codigo} creado.`
    await cargar()
  } catch (err) {
    error.value = err.message
  } finally {
    guardando.value = false
  }
}

function cambiarEstado(row, activar) {
  const accion = activar ? 'reactivar' : 'dar de baja'
  $q.dialog({ title: `${activar ? 'Reactivar' : 'Dar de baja'} empleado`, message: `¿Deseas ${accion} a ${row.nombres} ${row.apellidos}? ${activar ? 'Volverá a estar disponible en futuras planillas.' : 'No aparecerá en futuras planillas; su historial se conservará.'}`, cancel: true, persistent: true })
    .onOk(() => { void ejecutarCambioEstado(row, activar) })
}

async function ejecutarCambioEstado(row, activar) {
  error.value = ''
  mensaje.value = ''
  estadoProcesando.value = row.id
  try {
    if (activar) await api.post(`/api/empleados/${row.id}/activar`, {})
    else await api.del(`/api/empleados/${row.id}`)
    await cargar()
    mensaje.value = activar ? `${row.nombres} ${row.apellidos} fue reactivado.` : `${row.nombres} ${row.apellidos} fue dado de baja. Su historial de planillas se conserva.`
  } catch (err) {
    error.value = err.message || `No se pudo ${activar ? 'reactivar' : 'desactivar'} al empleado. Inténtalo de nuevo.`
  } finally {
    estadoProcesando.value = null
  }
}

onMounted(cargar)
</script>
