<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Libro Diario</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} asiento(s)</q-badge>
      <q-space />
      <q-btn v-if="auth.tienePermiso('reportes.crear')" flat icon="table_view" label="CSV" @click="exportar" />
      <q-btn v-if="auth.tienePermiso('reportes.crear')" flat icon="picture_as_pdf" label="PDF" @click="imprimirPdf" />
      <q-btn
        v-if="auth.tienePermiso('asientos.crear')"
        color="primary"
        icon="add"
        label="Nuevo asiento"
        @click="router.push('/transacciones')"
      />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>
    <q-banner v-if="ok" class="bg-green-1 text-green-9 q-mb-md" rounded>
      {{ ok }}
    </q-banner>

    <div class="q-mb-md">
      <div class="text-subtitle2 q-mb-xs">Período contable</div>
      <q-tabs
        v-model="periodoPestana"
        dense
        align="left"
        active-color="primary"
        indicator-color="primary"
        @update:model-value="cambiarPeriodo"
      >
        <q-tab name="todos" label="Todos" />
        <q-tab
          v-for="p in periodos"
          :key="p.id"
          :name="String(p.id)"
          :label="`${p.anio} · ${p.estado}`"
        />
      </q-tabs>
      <div v-if="periodoActual" class="text-caption text-grey-7 q-mt-xs">
        Período {{ periodoActual.anio }}: {{ periodoActual.estado }}
        <span v-if="periodoActual.estado === 'CERRADO'">· Solo consulta; no admite nuevos asientos.</span>
      </div>
    </div>

    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-md-3">
        <q-select
          v-model="filtroTipo"
          :options="tipos"
          label="Tipo"
          outlined
          dense
          emit-value
          map-options
          clearable
          @update:model-value="cambiarFiltro"
        />
      </div>
      <div class="col-12 col-md-3">
        <q-select
          v-model="filtroEstado"
          :options="estados"
          label="Estado del asiento"
          outlined
          dense
          emit-value
          map-options
          clearable
          @update:model-value="cambiarFiltro"
        />
      </div>
      <div class="col-12 col-md-3">
        <q-input
          v-model="filtroDesde"
          type="date"
          label="Desde"
          outlined
          dense
          clearable
          @update:model-value="cambiarFiltro"
        />
      </div>
      <div class="col-12 col-md-3">
        <q-input
          v-model="filtroHasta"
          type="date"
          label="Hasta"
          outlined
          dense
          clearable
          @update:model-value="cambiarFiltro"
        />
      </div>
      <div class="col-12 col-md-3">
        <q-select
          v-model="filtroSucursal"
          :options="sucursales"
          option-value="id"
          option-label="nombre"
          label="Sucursal"
          outlined
          dense
          emit-value
          map-options
          clearable
          @update:model-value="cambiarFiltro"
        />
      </div>
      <div class="col-12 col-md-3 row items-center q-gutter-md">
        <q-chip color="blue-1">Debe: {{ sumaDebe.toFixed(2) }}</q-chip>
        <q-chip color="orange-1">Haber: {{ sumaHaber.toFixed(2) }}</q-chip>
      </div>
    </div>

    <q-card v-if="cargando" flat bordered class="text-center q-pa-md">
      <q-spinner color="primary" size="24px" />
      <span class="q-ml-sm">Cargando diario…</span>
    </q-card>

    <q-table
      v-else
      :rows="asientos"
      :columns="columnas"
      row-key="id"
      :pagination="{ rowsPerPage: 15 }"
      :rows-per-page-options="[10, 15, 30, 0]"
      no-data-label="No hay asientos con esos filtros"
    >
      <template #body="props">
        <q-tr :props="props">
          <q-td auto-width>
            <q-btn
              size="sm"
              dense
              flat
              round
              :icon="props.expand ? 'expand_less' : 'expand_more'"
              @click="alternar(props)"
            />
          </q-td>
          <q-td
            v-for="col in props.cols.filter(c => c.name !== 'expand')"
            :key="col.name"
            :props="props"
          >
            <q-badge v-if="col.name === 'tipo'" color="blue-8">{{
              col.value
            }}</q-badge>
            <q-badge v-else-if="col.name === 'periodo_anio'" :color="props.row.periodo_estado === 'CERRADO' ? 'grey-7' : 'teal'">
              {{ col.value }} · {{ props.row.periodo_estado }}
            </q-badge>
            <q-badge
              v-else-if="col.name === 'estado'"
              :color="estadoColor(props.row.estado)"
            >
              {{ col.value }}
            </q-badge>
            <q-badge
              v-else-if="col.name === 'estado_partida'"
              :color="props.row.estado_partida === 'CUADRADO' ? 'positive' : 'negative'"
            >
              {{ col.value }}
            </q-badge>
            <q-btn
              v-else-if="col.name === 'acciones' && props.row.estado === 'PENDIENTE' && auth.tienePermiso('asientos.eliminar')"
              dense
              flat
              round
              color="negative"
              icon="delete"
              :loading="eliminando === props.row.id"
              aria-label="Eliminar asiento pendiente"
              @click="abrirEliminar(props.row)"
            >
              <q-tooltip>Eliminar asiento pendiente</q-tooltip>
            </q-btn>
            <q-btn
              v-else-if="col.name === 'acciones' && props.row.estado === 'VIGENTE' && auth.tienePermiso('asientos.anular')"
              dense
              flat
              color="negative"
              icon="block"
              label="Anular"
              @click="abrirAnulacion(props.row)"
            />
            <span v-else-if="col.name === 'acciones'">—</span>
            <span v-else>{{ col.value }}</span>
          </q-td>
        </q-tr>
        <q-tr v-show="props.expand || String(props.row.id) === asientoEnfocado" :props="props">
          <q-td colspan="100%">
            <div v-if="detalles[props.row.id]">
              <q-list dense bordered separator>
                <q-item
                  v-for="l in detalles[props.row.id].detalles"
                  :key="l.id"
                >
                  <q-item-section>
                    <q-item-label
                      >{{ l.cuenta_codigo }} ·
                      {{ l.cuenta_nombre }}</q-item-label
                    >
                    <q-item-label v-if="l.descripcion" caption>{{
                      l.descripcion
                    }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <span v-if="l.debe > 0"
                      >Debe {{ Number(l.debe).toFixed(2) }}</span
                    >
                    <span v-else>Haber {{ Number(l.haber).toFixed(2) }}</span>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            <div v-else class="text-grey-7">Cargando líneas…</div>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="dialogoEliminar" persistent>
      <q-card style="min-width: 360px; max-width: 480px">
        <q-card-section>
          <div class="text-h6">Eliminar transacción</div>
        </q-card-section>
        <q-card-section>
          ¿Confirmas eliminar el asiento pendiente
          <strong>{{ asientoEliminar?.codigo }} — {{ asientoEliminar?.concepto }}</strong>?
          Esta acción quedará registrada en auditoría. Los asientos de facturas, compras y planillas se administran desde sus módulos.
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn
            color="negative"
            icon="delete"
            label="Eliminar asiento"
            :loading="!!eliminando"
            @click="eliminarAsiento"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogoAnular" persistent>
      <q-card style="width: 560px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">Anular asiento vigente</div>
          <div class="text-caption text-grey-7">
            {{ asientoAnular?.codigo }} — {{ asientoAnular?.concepto }}
          </div>
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input v-model="motivoAnulacion" label="Motivo de la anulación" type="textarea" outlined autogrow />
          <q-select v-model="formAnular.periodo_id" :options="periodosAbiertos" option-value="id" :option-label="p => String(p.anio)" emit-value map-options label="Período abierto para la reversión" outlined dense />
          <q-input v-model="formAnular.fecha_reversion" type="date" label="Fecha de la reversión" outlined dense />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn color="negative" label="Crear reversión y anular" :loading="anulando" :disable="motivoAnulacion.trim().length < 5 || !formAnular.periodo_id || !formAnular.fecha_reversion" @click="anularAsiento" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { asientosService } from '@/services/asientosService.js'
import { controlService } from '@/services/controlService.js'
import { descargarCsv, imprimirPdf } from '@/utils/exportacion.js'

const router = useRouter()
const route = useRoute()
const asientoEnfocado = ref(route.query.asiento_id ? String(route.query.asiento_id) : '')
const auth = useAuthStore()
const asientos = ref([])
const detalles = ref({})
const total = ref(0)
const cargando = ref(false)
const error = ref('')
const ok = ref('')
const dialogoEliminar = ref(false)
const asientoEliminar = ref(null)
const eliminando = ref(null)
const dialogoAnular = ref(false)
const asientoAnular = ref(null)
const motivoAnulacion = ref('')
const anulando = ref(false)
const formAnular = ref({ periodo_id: null, fecha_reversion: '' })
const filtroTipo = ref(null)
const filtroPeriodo = ref(null)
const periodoPestana = ref('todos')
const filtroSucursal = ref(null)
const filtroEstado = ref(null)
const filtroDesde = ref('')
const filtroHasta = ref('')
const periodos = ref([])
const sucursales = ref([])
const periodoActual = computed(() => periodos.value.find(p => String(p.id) === periodoPestana.value) || null)
const periodosAbiertos = computed(() => periodos.value.filter(p => p.estado === 'ABIERTO'))

const tipos = [
  { label: 'Todos', value: null },
  { label: 'Apertura', value: 'APERTURA' },
  { label: 'Normal', value: 'DIARIO' },
  { label: 'Ajuste', value: 'AJUSTE' },
  { label: 'Cierre', value: 'CIERRE' }
]
const estados = [
  { label: 'Pendiente', value: 'PENDIENTE' },
  { label: 'Vigente', value: 'VIGENTE' },
  { label: 'Anulado', value: 'ANULADO' },
  { label: 'Rechazado', value: 'RECHAZADO' }
]

const columnas = [
  { name: 'expand', label: '', field: 'expand', align: 'center' },
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
  {
    name: 'periodo_anio',
    label: 'Período',
    field: 'periodo_anio',
    align: 'center'
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
  {
    name: 'estado',
    label: 'Estado del asiento',
    field: 'estado',
    align: 'center'
  },
  {
    name: 'estado_partida',
    label: 'Cuadre',
    field: 'estado_partida',
    align: 'center'
  },
  { name: 'acciones', label: 'Acciones', field: 'id', align: 'center' }
]

const sumaDebe = computed(() =>
  asientos.value.reduce((s, a) => s + (parseFloat(a.total_debe) || 0), 0)
)
const sumaHaber = computed(() =>
  asientos.value.reduce((s, a) => s + (parseFloat(a.total_haber) || 0), 0)
)

function estadoColor(estado) {
  return ({ PENDIENTE: 'warning', VIGENTE: 'positive', ANULADO: 'grey-7', RECHAZADO: 'negative' })[estado] || 'grey'
}

async function alternar(props) {
  props.expand = !props.expand
  const id = props.row.id
  if (props.expand && !detalles.value[id]) {
    try {
      detalles.value[id] = await asientosService.detalle(id)
    } catch (e) {
      error.value = e.message
    }
  }
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const params = {}
    if (filtroTipo.value) params.tipo = filtroTipo.value
    if (filtroPeriodo.value) params.periodo_id = filtroPeriodo.value
    if (filtroSucursal.value) params.sucursal_id = filtroSucursal.value
    if (filtroEstado.value) params.estado = filtroEstado.value
    if (filtroDesde.value) params.desde = filtroDesde.value
    if (filtroHasta.value) params.hasta = filtroHasta.value
    if (asientoEnfocado.value) params.asiento_id = Number(asientoEnfocado.value)
    const res = await asientosService.listar(params)
    asientos.value = res.asientos
    total.value = res.total
    const enfocado = asientos.value.find(a => String(a.id) === asientoEnfocado.value)
    if (enfocado && !detalles.value[enfocado.id]) detalles.value[enfocado.id] = await asientosService.detalle(enfocado.id)
  } catch (e) {
    error.value = `No se pudo cargar el diario. (${e.message})`
  } finally {
    cargando.value = false
  }
}

function cambiarPeriodo(valor) {
  asientoEnfocado.value = ''
  filtroPeriodo.value = valor === 'todos' ? null : Number(valor)
  cargar()
}

function cambiarFiltro() {
  asientoEnfocado.value = ''
  cargar()
}

function abrirEliminar(asiento) {
  asientoEliminar.value = asiento
  dialogoEliminar.value = true
}

function abrirAnulacion(asiento) {
  asientoAnular.value = asiento
  motivoAnulacion.value = ''
  const hoy = new Date().toLocaleDateString('sv-SE')
  const periodo = periodosAbiertos.value.find(p => hoy >= p.fecha_inicio && hoy <= p.fecha_fin)
    || periodosAbiertos.value[0]
  formAnular.value = {
    periodo_id: periodo?.id || null,
    fecha_reversion: periodo && (hoy < periodo.fecha_inicio || hoy > periodo.fecha_fin) ? periodo.fecha_inicio : hoy
  }
  dialogoAnular.value = true
}

async function anularAsiento() {
  if (!asientoAnular.value) return
  anulando.value = true
  error.value = ''
  ok.value = ''
  try {
    const result = await controlService.anular(asientoAnular.value.id, {
      motivo: motivoAnulacion.value.trim(),
      periodo_id: formAnular.value.periodo_id,
      fecha_reversion: formAnular.value.fecha_reversion
    })
    ok.value = `Asiento ${asientoAnular.value.codigo} anulado. Se creó la reversión ${result?.reversion?.asiento?.codigo || ''}.`
    dialogoAnular.value = false
    asientoAnular.value = null
    await cargar()
  } catch (e) {
    error.value = e.message
  } finally {
    anulando.value = false
  }
}

async function eliminarAsiento() {
  if (!asientoEliminar.value) return
  const asiento = asientoEliminar.value
  eliminando.value = asiento.id
  error.value = ''
  ok.value = ''
  try {
    await asientosService.eliminar(asiento.id)
    dialogoEliminar.value = false
    asientoEliminar.value = null
    ok.value = `Asiento ${asiento.codigo} eliminado.`
    await cargar()
  } catch (e) {
    error.value = e.message
    dialogoEliminar.value = false
  } finally {
    eliminando.value = null
  }
}

function exportar() {
  descargarCsv(
    'libro-diario',
    columnas.filter(c => !['expand', 'acciones'].includes(c.name)),
    asientos.value
  )
}

onMounted(async () => {
  try {
    const [perRes, sucRes] = await Promise.all([
      asientosService.periodos(),
      asientosService.sucursales()
    ])
    periodos.value = perRes.periodos.map(p => ({ ...p, anio: String(p.anio) }))
    sucursales.value = sucRes.sucursales
    const anioActual = new Date().getFullYear()
    const periodoInicial = asientoEnfocado.value ? null : (periodos.value.find(p => p.estado === 'ABIERTO' && Number(p.anio) === anioActual)
      || periodos.value.find(p => p.estado === 'ABIERTO')
      || periodos.value[0])
    if (periodoInicial) {
      periodoPestana.value = String(periodoInicial.id)
      filtroPeriodo.value = periodoInicial.id
    }
  } catch (e) {
    error.value = e.message
  }
  await cargar()
})
</script>
