<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Control y auditoría</div>
      <q-space />
      <q-btn-toggle
        v-model="tab"
        toggle-color="primary"
        color="grey-2"
        text-color="grey-8"
        unelevated
        no-caps
        :options="tabsControl"
      />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>
    <q-banner v-if="ok" class="bg-green-1 text-green-9 q-mb-md" rounded>
      {{ ok }}
    </q-banner>

    <!-- ================= APROBACIONES ================= -->
    <template v-if="tab === 'aprobaciones'">
      <div class="row items-center q-gutter-md q-mb-md">
        <q-chip color="orange-2"> Pendientes: {{ pendientes.length }} </q-chip>
        <q-space />
        <q-btn
          flat
          dense
          icon="refresh"
          label="Actualizar"
          @click="cargarPendientes"
        />
      </div>

      <q-card v-if="cargando" flat bordered class="text-center q-pa-md">
        <q-spinner color="primary" size="24px" />
      </q-card>

      <q-table
        v-else
        :rows="pendientes"
        :columns="columnasPendientes"
        row-key="id"
        :pagination="{ rowsPerPage: 10 }"
        :rows-per-page-options="[10, 20, 50]"
        no-data-label="No hay asientos pendientes de aprobación"
      >
        <template #body="props">
          <q-tr :props="props">
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              <q-badge
                v-if="col.name === 'estado'"
                color="orange-3"
                text-color="dark"
              >
                {{ col.value }}
              </q-badge>
              <q-badge
                v-else-if="col.name === 'estado_partida'"
                :color="
                  props.row.estado_partida === 'CUADRADO'
                    ? 'positive'
                    : 'negative'
                "
              >
                {{ col.value }}
              </q-badge>
              <span v-else>{{ col.value }}</span>
            </q-td>
            <q-td auto-width>
              <q-btn
                v-if="auth.tienePermiso('asientos.aprobar')"
                dense
                color="positive"
                icon="check"
                label="Aprobar"
                @click="aprobar(props.row)"
              />
              <q-btn
                v-if="auth.tienePermiso('asientos.aprobar')"
                dense
                flat
                color="negative"
                icon="thumb_down"
                label="Rechazar"
                @click="abrirDialogoRechazar(props.row)"
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </template>

    <!-- ================= PERÍODOS ================= -->
    <template v-else-if="tab === 'periodos'">
      <div class="row items-center q-gutter-md q-mb-md">
        <q-btn
          v-if="auth.tienePermiso('periodos.crear')"
          color="primary"
          icon="add"
          label="Abrir período"
          @click="abrirDialogoPeriodo"
        />
        <q-space />
      </div>

      <q-table
        v-if="auth.tienePermiso('periodos.ver')"
        :rows="periodos"
        :columns="columnasPeriodos"
        row-key="id"
        :loading="cargando"
        no-data-label="No hay períodos contables"
      >
        <template #body="props">
          <q-tr :props="props">
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              <q-badge
                v-if="col.name === 'estado'"
                :color="
                  props.row.estado === 'CERRADO' ? 'negative' : 'positive'
                "
              >
                {{ col.value }}
              </q-badge>
              <span v-else>{{ col.value }}</span>
            </q-td>
            <q-td auto-width>
              <q-btn
                v-if="
                  props.row.estado === 'ABIERTO' &&
                  auth.tienePermiso('periodos.cerrar')
                "
                dense
                color="negative"
                outline
                icon="lock"
                label="Cerrar"
                @click="cerrarPeriodo(props.row)"
              />
              <q-btn
                v-else-if="
                  props.row.estado === 'CERRADO' &&
                  auth.tienePermiso('periodos.cerrar')
                "
                dense
                color="primary"
                outline
                icon="lock_open"
                label="Reabrir"
                @click="abrirPeriodo(props.row)"
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>

      <div v-if="auth.tienePermiso('sucursales.ver')" class="text-subtitle1 q-mt-lg q-mb-sm">Sucursales</div>
      <q-table
        v-if="auth.tienePermiso('sucursales.ver')"
        :rows="sucursales"
        :columns="columnasSucursales"
        row-key="id"
        no-data-label="No hay sucursales"
      />
    </template>

    <!-- ================= HISTORIAL ================= -->
    <template v-else>
      <div class="row q-col-gutter-md q-mb-md">
        <div class="col-12 col-md-3">
          <q-select
            v-model="filtroModulo"
            :options="modulos"
            label="Módulo"
            outlined
            dense
            emit-value
            map-options
            clearable
            @update:model-value="cargarAuditoria"
          />
        </div>
        <div class="col-12 col-md-3">
          <q-select
            v-model="filtroAccion"
            :options="acciones"
            label="Acción"
            outlined
            dense
            emit-value
            map-options
            clearable
            @update:model-value="cargarAuditoria"
          />
        </div>
        <div class="col-6 col-md-3">
          <q-input
            v-model="filtroDesde"
            type="date"
            label="Desde"
            outlined
            dense
            @update:model-value="cargarAuditoria"
          />
        </div>
        <div class="col-6 col-md-3">
          <q-input
            v-model="filtroHasta"
            type="date"
            label="Hasta"
            outlined
            dense
            @update:model-value="cargarAuditoria"
          />
        </div>
      </div>

      <q-table
        :rows="auditoria"
        :columns="columnasAuditoria"
        row-key="id"
        :loading="cargando"
        :pagination="{ rowsPerPage: 15 }"
        :rows-per-page-options="[15, 30, 50]"
        no-data-label="Sin registros en la bitácora"
      >
        <template #body="props">
          <q-tr :props="props">
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              <q-badge
                v-if="col.name === 'accion'"
                :color="colorAccion(props.row.accion)"
              >
                {{ col.value }}
              </q-badge>
              <q-badge v-else-if="col.name === 'modulo'" outline color="grey-7">
                {{ col.value }}
              </q-badge>
              <span v-else>{{ col.value }}</span>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </template>

    <!-- ============ DIÁLOGO RECHAZAR PENDIENTE ============ -->
    <q-dialog v-model="dialogoRechazar">
      <q-card style="min-width: 420px">
        <q-card-section>
          <div class="text-h6">Rechazar asiento pendiente</div>
          <div class="text-caption text-grey-7">
            {{ asientoRechazar?.codigo }} — {{ asientoRechazar?.concepto }}
          </div>
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input
            v-model="motivoRechazo"
            label="Motivo del rechazo"
            type="textarea"
            outlined
            autogrow
            :rules="[v => (v || '').length >= 5 || 'Mínimo 5 caracteres']"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn
            color="negative"
            label="Rechazar asiento"
            :loading="guardando"
            :disable="motivoRechazo.trim().length < 5"
            @click="rechazar"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ============ DIÁLOGO PERÍODO ============ -->
    <q-dialog v-model="dialogoPeriodo">
      <q-card style="min-width: 420px">
        <q-card-section>
          <div class="text-h6">Abrir período contable</div>
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input
            v-model="formPeriodo.anio"
            type="number"
            label="Año"
            outlined
            dense
          />
          <q-input
            v-model="formPeriodo.fecha_inicio"
            type="date"
            label="Fecha de inicio"
            outlined
            dense
          />
          <q-input
            v-model="formPeriodo.fecha_fin"
            type="date"
            label="Fecha de fin"
            outlined
            dense
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn
            color="primary"
            label="Abrir período"
            :loading="guardando"
            @click="crearPeriodo"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { controlService } from '@/services/controlService.js'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()

const tabsControl = computed(() => [
  ...(auth.tienePermiso('asientos.ver') ? [{ label: 'Aprobaciones', value: 'aprobaciones' }] : []),
  ...(auth.tienePermiso('periodos.ver') || auth.tienePermiso('sucursales.ver') ? [{ label: 'Períodos', value: 'periodos' }] : []),
  ...(auth.tienePermiso('auditoria.ver') ? [{ label: 'Historial', value: 'historial' }] : [])
])
const tabInicial = auth.tienePermiso('asientos.ver')
  ? 'aprobaciones'
  : auth.tienePermiso('periodos.ver') || auth.tienePermiso('sucursales.ver')
    ? 'periodos'
    : 'historial'
const tab = ref(tabInicial)
const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const ok = ref('')

const pendientes = ref([])
const periodos = ref([])
const sucursales = ref([])
const auditoria = ref([])

const dialogoRechazar = ref(false)
const asientoRechazar = ref(null)
const motivoRechazo = ref('')
const dialogoPeriodo = ref(false)
const formPeriodo = ref({
  anio: new Date().getFullYear() + 1,
  fecha_inicio: '',
  fecha_fin: ''
})

const periodosAbiertos = computed(() =>
  periodos.value.filter(p => p.estado === 'ABIERTO')
)

const filtroModulo = ref(null)
const filtroAccion = ref(null)
const filtroDesde = ref('')
const filtroHasta = ref('')

const modulos = [
  { label: 'Todos', value: null },
  { label: 'Asientos', value: 'asientos' },
  { label: 'Períodos', value: 'periodos' },
  { label: 'Sucursales', value: 'sucursales' },
  { label: 'Cuentas', value: 'cuentas' },
  { label: 'Usuarios', value: 'usuarios' }
]

const acciones = [
  { label: 'Todas', value: null },
  { label: 'Crear', value: 'crear' },
  { label: 'Editar', value: 'editar' },
  { label: 'Aprobar', value: 'aprobar' },
  { label: 'Rechazar', value: 'rechazar' },
  { label: 'Anular', value: 'anular' },
  { label: 'Cerrar', value: 'cerrar' },
  { label: 'Eliminar', value: 'eliminar' }
]

const columnasPendientes = [
  {
    name: 'codigo',
    label: 'Folio',
    field: 'codigo',
    align: 'left',
    sortable: true
  },
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'fecha',
    align: 'left',
    sortable: true
  },
  { name: 'concepto', label: 'Concepto', field: 'concepto', align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'tipo', align: 'center' },
  {
    name: 'total_debe',
    label: 'Debe',
    field: 'total_debe',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  {
    name: 'total_haber',
    label: 'Haber',
    field: 'total_haber',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  { name: 'estado', label: 'Estado', field: 'estado', align: 'center' },
  {
    name: 'estado_partida',
    label: 'Partida',
    field: 'estado_partida',
    align: 'center'
  }
]

const columnasPeriodos = [
  { name: 'anio', label: 'Año', field: 'anio', align: 'left', sortable: true },
  {
    name: 'fecha_inicio',
    label: 'Inicio',
    field: 'fecha_inicio',
    align: 'left'
  },
  { name: 'fecha_fin', label: 'Fin', field: 'fecha_fin', align: 'left' },
  {
    name: 'num_asientos',
    label: 'Asientos',
    field: 'num_asientos',
    align: 'center'
  },
  {
    name: 'total_debe',
    label: 'Total debitado',
    field: 'total_debe',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  { name: 'estado', label: 'Estado', field: 'estado', align: 'center' }
]

const columnasSucursales = [
  { name: 'codigo', label: 'Código', field: 'codigo', align: 'left' },
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  { name: 'direccion', label: 'Dirección', field: 'direccion', align: 'left' },
  {
    name: 'num_asientos',
    label: 'Asientos',
    field: 'num_asientos',
    align: 'center'
  }
]

const columnasAuditoria = [
  {
    name: 'fecha',
    label: 'Fecha',
    field: 'fecha',
    align: 'left',
    format: v => (v ? new Date(v).toLocaleString('es-SV') : ''),
    sortable: true
  },
  {
    name: 'usuario_nombre',
    label: 'Usuario',
    field: 'usuario_nombre',
    align: 'left'
  },
  { name: 'modulo', label: 'Módulo', field: 'modulo', align: 'center' },
  { name: 'accion', label: 'Acción', field: 'accion', align: 'center' },
  {
    name: 'registro_codigo',
    label: 'Registro',
    field: 'registro_codigo',
    align: 'left'
  },
  {
    name: 'descripcion',
    label: 'Descripción',
    field: 'descripcion',
    align: 'left'
  }
]

function colorAccion(accion) {
  return (
    {
      crear: 'positive',
      editar: 'warning',
      aprobar: 'positive',
      anular: 'negative',
      cerrar: 'negative',
      eliminar: 'negative'
    }[accion] || 'grey-7'
  )
}

async function cargarPendientes() {
  cargando.value = true
  try {
    const res = await controlService.pendientes()
    pendientes.value = res.asientos
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}

async function cargarPeriodos() {
  cargando.value = true
  try {
    const tareas = []
    if (auth.tienePermiso('periodos.ver')) tareas.push(controlService.listarPeriodos().then(r => { periodos.value = r.periodos }))
    if (auth.tienePermiso('sucursales.ver')) tareas.push(controlService.listarSucursales().then(r => { sucursales.value = r.sucursales }))
    await Promise.all(tareas)
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}

async function cargarAuditoria() {
  cargando.value = true
  try {
    const res = await controlService.auditoria({
      modulo: filtroModulo.value,
      accion: filtroAccion.value,
      desde: filtroDesde.value,
      hasta: filtroHasta.value
    })
    auditoria.value = res.registros
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}

async function aprobar(asiento) {
  ok.value = ''
  error.value = ''
  try {
    await controlService.aprobar(asiento.id)
    ok.value = `Asiento ${asiento.codigo} aprobado y contabilizado.`
    await cargarPendientes()
  } catch (e) {
    error.value = e.message
  }
}

function abrirDialogoRechazar(asiento) {
  asientoRechazar.value = asiento
  motivoRechazo.value = ''
  dialogoRechazar.value = true
}

async function rechazar() {
  guardando.value = true
  ok.value = ''
  error.value = ''
  try {
    await controlService.rechazar(asientoRechazar.value.id, motivoRechazo.value.trim())
    ok.value = `Asiento ${asientoRechazar.value.codigo} rechazado. No se contabilizó ni se generó reversión.`
    dialogoRechazar.value = false
    await cargarPendientes()
  } catch (e) {
    error.value = e.message
  } finally {
    guardando.value = false
  }
}

async function cerrarPeriodo(periodo) {
  ok.value = ''
  error.value = ''
  try {
    await controlService.cerrarPeriodo(periodo.id)
    ok.value = `Período ${periodo.anio} cerrado. Ya no admite movimientos.`
    await cargarPeriodos()
  } catch (e) {
    error.value = e.message
  }
}

async function abrirPeriodo(periodo) {
  ok.value = ''
  error.value = ''
  try {
    await controlService.abrirPeriodo(periodo.id)
    ok.value = `Período ${periodo.anio} reabierto.`
    await cargarPeriodos()
  } catch (e) {
    error.value = e.message
  }
}

function abrirDialogoPeriodo() {
  const anio = new Date().getFullYear() + 1
  formPeriodo.value = {
    anio,
    fecha_inicio: `${anio}-01-01`,
    fecha_fin: `${anio}-12-31`
  }
  dialogoPeriodo.value = true
}

async function crearPeriodo() {
  guardando.value = true
  ok.value = ''
  error.value = ''
  try {
    await controlService.crearPeriodo({
      anio: Number(formPeriodo.value.anio),
      fecha_inicio: formPeriodo.value.fecha_inicio,
      fecha_fin: formPeriodo.value.fecha_fin,
      estado: 'ABIERTO'
    })
    ok.value = `Período ${formPeriodo.value.anio} abierto.`
    dialogoPeriodo.value = false
    await cargarPeriodos()
  } catch (e) {
    error.value = e.message
  } finally {
    guardando.value = false
  }
}

async function cargarTabActual() {
  if (tab.value === 'aprobaciones' && auth.tienePermiso('asientos.ver')) await cargarPendientes()
  if (tab.value === 'periodos') await cargarPeriodos()
  if (tab.value === 'historial' && auth.tienePermiso('auditoria.ver')) await cargarAuditoria()
}

watch(tab, () => cargarTabActual())
onMounted(() => cargarTabActual())
</script>
