<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div>
        <div class="text-h5">Proyectos y rentabilidad</div>
        <div class="text-caption text-grey-7">Relaciona ventas, compras y planilla con cada trabajo de OptimaTech.</div>
      </div>
      <q-space />
      <q-btn flat color="secondary" icon="refresh" label="Actualizar" :loading="cargando" @click="cargarProyectos" />
      <q-btn v-if="auth.tienePermiso('proyectos.crear')" class="q-ml-sm" color="primary" icon="add" label="Nuevo proyecto" @click="abrirNuevo" />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>{{ error }}</q-banner>
    <q-banner v-if="mensaje" class="bg-blue-1 text-blue-10 q-mb-md" rounded>{{ mensaje }}</q-banner>
    <q-banner class="bg-blue-1 text-blue-10 q-mb-md" rounded>
      Las asignaciones son analíticas: solo enlazan líneas contabilizadas y vigentes; no crean ni modifican asientos. Los costos de compras se consideran por su importe de línea antes del IVA.
    </q-banner>

    <q-card class="opti-card">
      <q-table :rows="proyectos" :columns="columnas" row-key="id" :loading="cargando" :filter="filtro" :pagination="{ rowsPerPage: 10 }" no-data-label="No hay proyectos registrados">
        <template #top-right>
          <q-input v-model="filtro" dense outlined debounce="250" placeholder="Buscar proyecto" clearable>
            <template #prepend><q-icon name="search" /></template>
          </q-input>
        </template>
        <template #body-cell-proyecto="p">
          <q-td :props="p">
            <div class="text-weight-medium">{{ p.row.nombre }}</div>
            <div class="text-caption text-grey-7">{{ p.row.codigo }} · {{ tipoLabel(p.row.tipo) }}</div>
          </q-td>
        </template>
        <template #body-cell-cliente="p"><q-td :props="p">{{ p.value || '—' }}</q-td></template>
        <template #body-cell-estado="p">
          <q-td :props="p"><q-badge :color="colorEstado(p.value)">{{ estadoLabel(p.value) }}</q-badge></q-td>
        </template>
        <template #body-cell-acciones="p">
          <q-td :props="p" class="text-right">
            <q-btn flat dense color="secondary" icon="analytics" label="Ver proyecto" @click="abrirDetalle(p.row)" />
            <q-btn v-if="auth.tienePermiso('proyectos.editar')" flat dense color="primary" icon="edit" label="Editar" @click="abrirEdicion(p.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogProyecto" @hide="errorDialog = ''">
      <q-card style="width: 760px; max-width: 96vw">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ editando ? 'Editar proyecto' : 'Nuevo proyecto' }}</div>
          <q-space /><q-btn v-close-popup flat round icon="close" />
        </q-card-section>
        <q-card-section v-if="errorDialog" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ errorDialog }}</q-banner></q-card-section>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12 col-sm-4">
            <q-input v-model="form.codigo" label="Código (opcional)" placeholder="Ej.: PRY-0001" hint="Déjalo vacío para asignarlo automáticamente." maxlength="20" outlined dense />
          </div>
          <div class="col-12 col-sm-8"><q-input v-model="form.nombre" label="Nombre del proyecto *" placeholder="Ej.: Instalación CCTV – Cliente X" maxlength="160" outlined dense /></div>
          <div class="col-12 col-sm-6">
            <q-select v-model="form.tipo" :options="tiposProyecto" option-value="value" option-label="label" emit-value map-options label="Tipo de trabajo" outlined dense />
          </div>
          <div v-if="puedeVerClientes" class="col-12 col-sm-6">
            <q-select v-model="form.cliente_id" :options="clientes" option-value="id" option-label="nombre" emit-value map-options clearable label="Cliente (opcional)" outlined dense />
          </div>
          <div class="col-12"><q-input v-model="form.descripcion" type="textarea" autogrow label="Descripción (opcional)" placeholder="Alcance, entregables o notas del trabajo" maxlength="2000" outlined dense /></div>
          <div class="col-12 col-sm-4"><q-input v-model="form.fecha_inicio" type="date" label="Fecha de inicio" outlined dense /></div>
          <div class="col-12 col-sm-4"><q-input v-model="form.fecha_fin" type="date" label="Fecha de cierre" outlined dense /></div>
          <div v-if="editando" class="col-12 col-sm-4">
            <q-select v-model="form.estado" :options="estadosPermitidos" option-value="value" option-label="label" emit-value map-options label="Estado" outlined dense />
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn color="primary" :label="editando ? 'Guardar cambios' : 'Crear proyecto'" :loading="guardandoProyecto" @click="guardarProyecto" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogDetalle" maximized>
      <q-card class="bg-page text-primary">
        <q-card-section class="row items-center q-px-lg">
          <div>
            <div class="text-h5">{{ proyectoActual?.nombre }}</div>
            <div class="text-caption text-grey-7">{{ proyectoActual?.codigo }} · {{ tipoLabel(proyectoActual?.tipo) }}</div>
          </div>
          <q-space />
          <q-badge :color="colorEstado(proyectoActual?.estado)" class="q-mr-md">{{ estadoLabel(proyectoActual?.estado) }}</q-badge>
          <q-btn v-close-popup flat round icon="close" />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-pa-lg">
          <q-banner v-if="errorDetalle" class="bg-red-1 text-red q-mb-md" rounded>{{ errorDetalle }}</q-banner>
          <q-inner-loading :showing="cargandoDetalle"><q-spinner size="42px" color="primary" /></q-inner-loading>
          <template v-if="!cargandoDetalle && proyectoActual">
            <div v-if="rentabilidad" class="row q-col-gutter-md q-mb-lg">
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Ingresos asignados</div><div class="text-h5 text-positive">{{ dinero(rentabilidad.ingresos) }}</div></q-card></div>
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Costos directos y mano de obra</div><div class="text-h5">{{ dinero(Number(rentabilidad.costos_directos) + Number(rentabilidad.mano_obra)) }}</div></q-card></div>
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Costos indirectos</div><div class="text-h5">{{ dinero(rentabilidad.costos_indirectos) }}</div></q-card></div>
              <div class="col-12 col-sm-6 col-lg-3"><q-card class="opti-card q-pa-md"><div class="text-caption text-grey-7">Margen del proyecto</div><div class="text-h5" :class="Number(rentabilidad.margen) >= 0 ? 'text-positive' : 'text-negative'">{{ dinero(rentabilidad.margen) }}</div><div class="text-caption">{{ Number(rentabilidad.margen_porcentaje).toFixed(2) }}% de los ingresos</div></q-card></div>
            </div>
            <q-banner v-if="!rentabilidad" class="bg-blue-1 text-blue-10 q-mb-md" rounded>
              Tu rol puede asignar solo las categorías que tiene autorizadas. El reporte consolidado de margen requiere el permiso de rentabilidad.
            </q-banner>
            <q-banner v-if="asignacionesNoVigentes.length" class="bg-amber-1 text-amber-10 q-mb-md" rounded>
              Hay {{ asignacionesNoVigentes.length }} asignación(es) cuyo documento fuente ya no está vigente. Se conservan como historial, pero se excluyen de los saldos y del margen.
            </q-banner>
            <div class="row items-center q-mb-sm">
              <div class="text-h6">Movimientos asignados</div><q-space />
              <q-btn v-if="puedeAsignarAlguna && proyectoActual.estado === 'ABIERTO'" color="primary" icon="add" label="Asignar ingreso o costo" @click="abrirAsignacion" />
            </div>
            <q-table :rows="asignacionesVisibles" :columns="columnasAsignaciones" row-key="id" :pagination="{ rowsPerPage: 10 }" no-data-label="Aún no hay ingresos o costos asignados">
              <template #body-cell-documento="p">
                <q-td :props="p">
                  <div>{{ p.row.documento || 'Documento no disponible' }}</div>
                  <q-badge v-if="p.row.fuente_vigente === false" color="warning" text-color="dark" class="q-mt-xs">Fuente no vigente</q-badge>
                </q-td>
              </template>
              <template #body-cell-categoria="p"><q-td :props="p">{{ categoriaLabel(p.value) }}</q-td></template>
              <template #body-cell-monto="p"><q-td :props="p" class="text-right">{{ dinero(p.value) }}</q-td></template>
              <template #body-cell-acciones="p">
                <q-td :props="p" class="text-right">
                  <q-btn v-if="puedeQuitar(p.row) && proyectoActual.estado === 'ABIERTO'" flat dense color="negative" icon="delete_outline" label="Quitar" @click="confirmarQuitar(p.row)" />
                </q-td>
              </template>
            </q-table>
          </template>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogAsignacion">
      <q-card style="width: 820px; max-width: 96vw">
        <q-card-section class="row items-center"><div class="text-h6">Asignar ingreso o costo</div><q-space /><q-btn v-close-popup flat round icon="close" /></q-card-section>
        <q-card-section v-if="errorAsignacion" class="q-pt-none"><q-banner class="bg-red-1 text-red" rounded>{{ errorAsignacion }}</q-banner></q-card-section>
        <q-card-section class="row q-col-gutter-sm">
          <div class="col-12 col-sm-5">
            <q-select v-model="asignacion.fuente_tipo" :options="tiposFuentePermitidos" option-value="value" option-label="label" emit-value map-options label="Origen del movimiento" outlined dense @update:model-value="cargarFuentes" />
          </div>
          <div v-if="asignacion.fuente_tipo === 'COMPRA'" class="col-12 col-sm-7">
            <q-select v-model="asignacion.categoria" :options="categoriasCompra" option-value="value" option-label="label" emit-value map-options label="Clasificación del costo" outlined dense />
          </div>
          <div class="col-12">
            <q-select v-model="asignacion.fuente_detalle_id" :options="fuentes" :option-value="'fuente_detalle_id'" :option-label="fuenteLabel" emit-value map-options label="Línea contabilizada *" :loading="cargandoFuentes" :disable="cargandoFuentes || !asignacion.fuente_tipo" outlined dense @update:model-value="actualizarMontoSugerido">
              <template #option="scope"><q-item v-bind="scope.itemProps"><q-item-section><q-item-label>{{ fuenteLabel(scope.opt) }}</q-item-label><q-item-label caption>{{ scope.opt.descripcion }} · Disponible {{ dinero(scope.opt.monto_disponible) }}</q-item-label></q-item-section></q-item></template>
            </q-select>
          </div>
          <div class="col-12 col-sm-5"><q-input v-model.number="asignacion.monto" type="number" min="0.01" step="0.01" label="Importe que se asigna *" outlined dense /></div>
          <div class="col-12 col-sm-7 self-center text-caption text-grey-7">Disponible en la fuente: <strong>{{ dinero(fuenteSeleccionada?.monto_disponible || 0) }}</strong></div>
          <div class="col-12"><q-banner class="bg-blue-1 text-blue-10" rounded>Solo aparecen documentos aprobados y vigentes. Una línea puede distribuirse entre proyectos; la suma asignada no puede superar su importe disponible. Esta operación no crea un asiento contable.</q-banner></div>
        </q-card-section>
        <q-card-actions align="right"><q-btn flat label="Cancelar" v-close-popup /><q-btn color="primary" label="Guardar asignación" :loading="guardandoAsignacion" :disable="!asignacion.fuente_detalle_id || !asignacion.monto" @click="guardarAsignacion" /></q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth.js'
import { api } from '@/services/api.js'
import { proyectosService } from '@/services/operacionesService.js'

const $q = useQuasar()
const auth = useAuthStore()
const proyectos = ref([])
const clientes = ref([])
const filtro = ref('')
const cargando = ref(false)
const guardandoProyecto = ref(false)
const dialogProyecto = ref(false)
const dialogDetalle = ref(false)
const dialogAsignacion = ref(false)
const editando = ref(false)
const proyectoId = ref(null)
const proyectoActual = ref(null)
const rentabilidad = ref(null)
const asignaciones = ref([])
const fuentes = ref([])
const cargandoDetalle = ref(false)
const cargandoFuentes = ref(false)
const guardandoAsignacion = ref(false)
const error = ref('')
const errorDialog = ref('')
const errorDetalle = ref('')
const errorAsignacion = ref('')
const mensaje = ref('')
const formVacio = () => ({ codigo: '', nombre: '', descripcion: '', tipo: 'OTRO', cliente_id: null, fecha_inicio: '', fecha_fin: '', estado: 'ABIERTO' })
const form = ref(formVacio())
const asignacionVacia = () => ({ fuente_tipo: '', fuente_detalle_id: null, categoria: '', monto: null })
const asignacion = ref(asignacionVacia())
const puedeVerClientes = computed(() => auth.tienePermiso('facturas.ver'))
const puedeAsignarAlguna = computed(() => ['FACTURA', 'COMPRA', 'PLANILLA'].some(type => permisoFuente(type)))
const tiposProyecto = [
  { label: 'Instalación CCTV', value: 'CCTV' }, { label: 'Desarrollo de software', value: 'DESARROLLO' },
  { label: 'Hosting', value: 'HOSTING' }, { label: 'Soporte técnico', value: 'SOPORTE' },
  { label: 'Licencias', value: 'LICENCIAS' }, { label: 'Equipo tecnológico', value: 'EQUIPO' }, { label: 'Otro', value: 'OTRO' }
]
const categoriasCompra = [{ label: 'Costo directo del proyecto', value: 'COSTO_DIRECTO' }, { label: 'Costo indirecto asignado', value: 'COSTO_INDIRECTO' }]
const estados = [{ label: 'Abierto', value: 'ABIERTO' }, { label: 'Completado', value: 'COMPLETADO' }, { label: 'Cancelado', value: 'CANCELADO' }]
const estadosPermitidos = computed(() => form.value.estado === 'ABIERTO' ? estados : estados.filter(option => option.value !== 'ABIERTO'))
const columnas = [
  { name: 'proyecto', label: 'Proyecto', field: 'nombre', align: 'left', sortable: true },
  { name: 'cliente', label: 'Cliente', field: row => row.cliente || '', align: 'left' },
  { name: 'fechas', label: 'Período', field: row => `${fechaLabel(row.fecha_inicio)} – ${fechaLabel(row.fecha_fin)}`, align: 'left' },
  { name: 'estado', label: 'Estado', field: 'estado', align: 'center' },
  { name: 'acciones', label: 'Acciones', field: 'id', align: 'right' }
]
const columnasAsignaciones = [
  { name: 'documento', label: 'Documento', field: 'documento', align: 'left' },
  { name: 'fuente_tipo', label: 'Origen', field: 'fuente_tipo' },
  { name: 'categoria', label: 'Clasificación', field: 'categoria' },
  { name: 'descripcion', label: 'Detalle', field: row => row.descripcion || '—', align: 'left' },
  { name: 'monto', label: 'Importe asignado', field: 'monto', align: 'right' },
  { name: 'acciones', label: 'Acciones', field: 'id', align: 'right' }
]
const tiposFuentePermitidos = computed(() => [
  ...(permisoFuente('FACTURA') ? [{ label: 'Factura contabilizada · Ingreso', value: 'FACTURA' }] : []),
  ...(permisoFuente('COMPRA') ? [{ label: 'Compra contabilizada · Costo', value: 'COMPRA' }] : []),
  ...(permisoFuente('PLANILLA') ? [{ label: 'Planilla contabilizada · Mano de obra', value: 'PLANILLA' }] : [])
])
const fuenteSeleccionada = computed(() => fuentes.value.find(row => row.fuente_detalle_id === asignacion.value.fuente_detalle_id) || null)
const asignacionesVisibles = computed(() => rentabilidad.value?.asignaciones || asignaciones.value)
const asignacionesNoVigentes = computed(() => asignacionesVisibles.value.filter(row => row.fuente_vigente === false))

function permisoFuente(type) {
  const permission = { FACTURA: 'proyectos.asignar_ingresos', COMPRA: 'proyectos.asignar_compras', PLANILLA: 'proyectos.asignar_planilla' }[type]
  return auth.tienePermiso(permission)
}
function dinero(value) { return new Intl.NumberFormat('es-SV', { style: 'currency', currency: 'USD' }).format(Number(value) || 0) }
function fechaLabel(value) { return value ? new Intl.DateTimeFormat('es-SV', { dateStyle: 'medium', timeZone: 'UTC' }).format(new Date(`${String(value).slice(0, 10)}T00:00:00Z`)) : 'Sin fecha' }
function tipoLabel(value) { return tiposProyecto.find(item => item.value === value)?.label || 'Otro' }
function estadoLabel(value) { return ({ ABIERTO: 'Abierto', COMPLETADO: 'Completado', CANCELADO: 'Cancelado' })[value] || value || '—' }
function colorEstado(value) { return ({ ABIERTO: 'positive', COMPLETADO: 'blue-grey', CANCELADO: 'negative' })[value] || 'grey' }
function categoriaLabel(value) { return ({ INGRESO: 'Ingreso', COSTO_DIRECTO: 'Costo directo', MANO_OBRA: 'Mano de obra', COSTO_INDIRECTO: 'Costo indirecto' })[value] || value }
function fuenteLabel(row) { return `${row.documento} · ${row.tercero} · ${row.descripcion} · ${fechaLabel(row.fecha)}` }

async function cargarProyectos() {
  cargando.value = true
  error.value = ''
  try {
    const result = await proyectosService.listar()
    proyectos.value = result.proyectos || []
    if (puedeVerClientes.value) {
      try { const customers = await api.get('/api/clientes'); clientes.value = (customers.clientes || []).filter(customer => customer.estado === 'ACTIVO') }
      catch { clientes.value = [] }
    }
  } catch (err) { error.value = err.message }
  finally { cargando.value = false }
}

function abrirNuevo() {
  errorDialog.value = ''
  editando.value = false
  proyectoId.value = null
  form.value = formVacio()
  dialogProyecto.value = true
}
function abrirEdicion(row) {
  errorDialog.value = ''
  editando.value = true
  proyectoId.value = row.id
  form.value = { codigo: row.codigo || '', nombre: row.nombre, descripcion: row.descripcion || '', tipo: row.tipo || 'OTRO', cliente_id: row.cliente_id || null, fecha_inicio: row.fecha_inicio || '', fecha_fin: row.fecha_fin || '', estado: row.estado }
  dialogProyecto.value = true
}
async function guardarProyecto() {
  errorDialog.value = ''
  const nombre = String(form.value.nombre || '').trim()
  if (nombre.length < 3) { errorDialog.value = 'Escribe un nombre de proyecto de al menos 3 caracteres.'; return }
  if (form.value.fecha_inicio && form.value.fecha_fin && form.value.fecha_fin < form.value.fecha_inicio) { errorDialog.value = 'La fecha de cierre no puede ser anterior al inicio.'; return }
  const payload = { ...form.value, nombre, codigo: form.value.codigo.trim() || null, descripcion: form.value.descripcion.trim() || null, cliente_id: form.value.cliente_id || null, fecha_inicio: form.value.fecha_inicio || null, fecha_fin: form.value.fecha_fin || null }
  guardandoProyecto.value = true
  try {
    const result = editando.value ? await proyectosService.actualizar(proyectoId.value, payload) : await proyectosService.crear(payload)
    dialogProyecto.value = false
    mensaje.value = editando.value ? 'Proyecto actualizado.' : `Proyecto ${result.codigo} creado.`
    await cargarProyectos()
  } catch (err) { errorDialog.value = err.message }
  finally { guardandoProyecto.value = false }
}

async function abrirDetalle(row) {
  proyectoActual.value = row
  rentabilidad.value = null
  asignaciones.value = []
  errorDetalle.value = ''
  dialogDetalle.value = true
  cargandoDetalle.value = true
  try {
    if (auth.tienePermiso('proyectos.rentabilidad')) {
      rentabilidad.value = await proyectosService.rentabilidad(row.id)
    } else {
      const types = ['FACTURA', 'COMPRA', 'PLANILLA'].filter(permisoFuente)
      const parts = await Promise.all(types.map(type => proyectosService.asignaciones(row.id, type)))
      asignaciones.value = parts.flatMap(result => result.asignaciones || [])
    }
  } catch (err) { errorDetalle.value = err.message }
  finally { cargandoDetalle.value = false }
}

function abrirAsignacion() {
  errorAsignacion.value = ''
  asignacion.value = asignacionVacia()
  asignacion.value.fuente_tipo = tiposFuentePermitidos.value[0]?.value || ''
  asignacion.value.categoria = asignacion.value.fuente_tipo === 'FACTURA' ? 'INGRESO' : asignacion.value.fuente_tipo === 'PLANILLA' ? 'MANO_OBRA' : 'COSTO_DIRECTO'
  fuentes.value = []
  dialogAsignacion.value = true
  if (asignacion.value.fuente_tipo) cargarFuentes()
}
async function cargarFuentes() {
  const type = asignacion.value.fuente_tipo
  asignacion.value.fuente_detalle_id = null
  asignacion.value.monto = null
  fuentes.value = []
  if (!type || !proyectoActual.value) return
  asignacion.value.categoria = type === 'FACTURA' ? 'INGRESO' : type === 'PLANILLA' ? 'MANO_OBRA' : 'COSTO_DIRECTO'
  cargandoFuentes.value = true
  errorAsignacion.value = ''
  try {
    const result = await proyectosService.fuentes(proyectoActual.value.id, type)
    fuentes.value = result.fuentes || []
  } catch (err) { errorAsignacion.value = err.message }
  finally { cargandoFuentes.value = false }
}
function actualizarMontoSugerido() { asignacion.value.monto = fuenteSeleccionada.value ? Number(fuenteSeleccionada.value.monto_disponible) : null }
async function guardarAsignacion() {
  errorAsignacion.value = ''
  const amount = Number(asignacion.value.monto)
  const available = Number(fuenteSeleccionada.value?.monto_disponible || 0)
  if (!Number.isFinite(amount) || amount <= 0 || Math.round(amount * 100) !== amount * 100) { errorAsignacion.value = 'Ingresa un importe positivo con hasta 2 decimales.'; return }
  if (amount > available) { errorAsignacion.value = `El importe supera el saldo disponible de ${dinero(available)}.`; return }
  guardandoAsignacion.value = true
  try {
    await proyectosService.asignar(proyectoActual.value.id, { ...asignacion.value, monto: amount })
    dialogAsignacion.value = false
    mensaje.value = 'Movimiento asignado al proyecto.'
    await abrirDetalle(proyectoActual.value)
  } catch (err) { errorAsignacion.value = err.message }
  finally { guardandoAsignacion.value = false }
}
function puedeQuitar(row) {
  const type = row.fuente_tipo || ({ INGRESO: 'FACTURA', COSTO_DIRECTO: 'COMPRA', COSTO_INDIRECTO: 'COMPRA', MANO_OBRA: 'PLANILLA' })[row.categoria]
  return permisoFuente(type)
}
function confirmarQuitar(row) {
  $q.dialog({ title: 'Quitar asignación', message: 'Se quitará este vínculo analítico del proyecto. El asiento contable original no cambiará.', cancel: true, persistent: true })
    .onOk(async () => {
      errorDetalle.value = ''
      try {
        await proyectosService.quitarAsignacion(proyectoActual.value.id, row.id)
        await abrirDetalle(proyectoActual.value)
      } catch (err) { errorDetalle.value = err.message }
    })
}

onMounted(cargarProyectos)
</script>
