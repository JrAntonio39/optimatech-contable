<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Libro Mayor</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} cuenta(s)</q-badge>
      <q-space />
      <q-btn v-if="auth.tienePermiso('reportes.crear')" flat icon="table_view" label="CSV" @click="exportar" />
      <q-btn v-if="auth.tienePermiso('reportes.crear')" flat icon="picture_as_pdf" label="PDF" @click="imprimirPdf" />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>

    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-md-4">
        <q-select
          v-model="filtroPeriodo"
          :options="periodos"
          option-value="id"
          option-label="anio"
          label="Periodo"
          outlined
          dense
          emit-value
          map-options
          clearable
          @update:model-value="recargarTodo"
        />
      </div>
      <div class="col-12 col-md-8">
        <q-input
          v-model="busqueda"
          label="Buscar cuenta"
          outlined
          dense
          clearable
          debounce="400"
          @update:model-value="cargarResumen"
        >
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
    </div>

    <div class="text-subtitle1 q-mb-sm">Saldos por cuenta</div>
    <q-table
      :rows="cuentas"
      :columns="columnas"
      row-key="codigo"
      :loading="cargando"
      :pagination="{ rowsPerPage: 15 }"
      :rows-per-page-options="[10, 15, 30, 0]"
      no-data-label="Sin movimientos en el periodo"
    >
      <template #body="props">
        <q-tr :props="props">
          <q-td auto-width>
            <q-btn
              dense
              flat
              round
              :icon="cuentasAbiertas[props.row.codigo] ? 'expand_less' : 'expand_more'"
              :aria-label="cuentasAbiertas[props.row.codigo] ? 'Ocultar movimientos' : 'Ver movimientos'"
              @click="alternarCuenta(props.row.codigo)"
            />
          </q-td>
          <q-td
            v-for="col in props.cols.filter(c => c.name !== 'expand')"
            :key="col.name"
            :props="props"
          >
            {{ col.value }}
          </q-td>
        </q-tr>
        <q-tr v-if="cuentasAbiertas[props.row.codigo]" :props="props">
          <q-td colspan="100%">
            <div class="text-subtitle2 q-mb-sm">
              Movimientos de {{ props.row.codigo }} — {{ props.row.nombre }}
            </div>
            <div v-if="cargandoDetalles[props.row.codigo]" class="row items-center q-pa-md">
              <q-spinner color="primary" size="22px" />
              <span class="q-ml-sm">Cargando movimientos…</span>
            </div>
            <template v-else-if="detalles[props.row.codigo]">
              <div class="text-caption text-grey-7 q-mb-xs">
                Mostrando {{ detalles[props.row.codigo].movimientos.length }} de
                {{ detalles[props.row.codigo].total_movimientos }} movimientos
              </div>
              <q-markup-table flat bordered dense separator="horizontal" class="movimientos-cuenta">
                <thead>
                  <tr>
                    <th class="text-left">Fecha</th>
                    <th class="text-left">Folio</th>
                    <th class="text-left">Concepto</th>
                    <th class="text-center">Tipo</th>
                    <th class="text-right">Debe</th>
                    <th class="text-right">Haber</th>
                    <th class="text-right">Saldo</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="mov in detalles[props.row.codigo].movimientos" :key="mov.movimiento_id">
                    <td>{{ mov.fecha }}</td>
                    <td>{{ mov.folio }}</td>
                    <td>{{ mov.concepto }}</td>
                    <td class="text-center">{{ mov.tipo }}</td>
                    <td class="text-right">{{ fmt(mov.debe) }}</td>
                    <td class="text-right">{{ fmt(mov.haber) }}</td>
                    <td class="text-right">{{ fmt(mov.saldo_acumulado) }}</td>
                  </tr>
                  <tr v-if="!detalles[props.row.codigo].movimientos.length">
                    <td colspan="7" class="text-center text-grey">Sin movimientos para esta cuenta en el período</td>
                  </tr>
                </tbody>
              </q-markup-table>
              <div class="row items-center q-gutter-sm q-mt-sm">
                <q-chip color="blue-1">Debe: {{ fmt(detalles[props.row.codigo].total_debe) }}</q-chip>
                <q-chip color="orange-1">Haber: {{ fmt(detalles[props.row.codigo].total_haber) }}</q-chip>
                <q-chip color="green-3">Saldo: {{ fmt(detalles[props.row.codigo].saldo_final) }}</q-chip>
                <q-space />
                <q-btn
                  v-if="detalles[props.row.codigo].movimientos.length < detalles[props.row.codigo].total_movimientos"
                  outline
                  dense
                  color="primary"
                  label="Cargar 50 más"
                  :loading="cargandoMas[props.row.codigo]"
                  @click="cargarMas(props.row.codigo)"
                />
              </div>
            </template>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { ref, onMounted } from 'vue'
import { reportesService } from '@/services/reportesService.js'
import { asientosService } from '@/services/asientosService.js'
import { descargarCsv, imprimirPdf } from '@/utils/exportacion.js'

const auth = useAuthStore()
const cuentas = ref([])
const detalles = ref({})
const cuentasAbiertas = ref({})
const cargandoDetalles = ref({})
const cargandoMas = ref({})
const periodos = ref([])
const filtroPeriodo = ref(null)
const busqueda = ref('')
const total = ref(0)
const cargando = ref(false)
const error = ref('')

const columnas = [
  { name: 'expand', label: '', field: 'expand', align: 'center' },
  {
    name: 'codigo',
    label: 'Código',
    field: 'codigo',
    align: 'left',
    sortable: true
  },
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  {
    name: 'naturaleza',
    label: 'Naturaleza',
    field: 'naturaleza',
    align: 'left'
  },
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
    name: 'saldo',
    label: 'Saldo',
    field: 'saldo',
    align: 'right',
    format: v => Number(v).toFixed(2)
  }
]

const fmt = value => Number(value || 0).toFixed(2)

function exportar() {
  descargarCsv(
    'libro-mayor',
    columnas.filter(col => col.name !== 'expand'),
    cuentas.value
  )
}

async function alternarCuenta(codigo) {
  if (cuentasAbiertas.value[codigo]) {
    cuentasAbiertas.value = { ...cuentasAbiertas.value, [codigo]: false }
    return
  }
  cuentasAbiertas.value = { ...cuentasAbiertas.value, [codigo]: true }
  if (detalles.value[codigo]) return
  cargandoDetalles.value = { ...cargandoDetalles.value, [codigo]: true }
  try {
    const detalle = await reportesService.mayorCuenta(
      codigo,
      filtroPeriodo.value || undefined,
      50,
      0
    )
    detalles.value = { ...detalles.value, [codigo]: detalle }
  } catch (e) {
    error.value = `No se pudieron cargar los movimientos de ${codigo}. (${e.message})`
  } finally {
    cargandoDetalles.value = { ...cargandoDetalles.value, [codigo]: false }
  }
}

async function cargarMas(codigo) {
  const detalleActual = detalles.value[codigo]
  if (!detalleActual || cargandoMas.value[codigo]) return
  cargandoMas.value = { ...cargandoMas.value, [codigo]: true }
  try {
    const pagina = await reportesService.mayorCuenta(
      codigo,
      filtroPeriodo.value || undefined,
      50,
      detalleActual.movimientos.length
    )
    detalles.value = {
      ...detalles.value,
      [codigo]: {
        ...pagina,
        movimientos: [...detalleActual.movimientos, ...pagina.movimientos]
      }
    }
  } catch (e) {
    error.value = `No se pudieron cargar más movimientos de ${codigo}. (${e.message})`
  } finally {
    cargandoMas.value = { ...cargandoMas.value, [codigo]: false }
  }
}

async function cargarResumen() {
  cargando.value = true
  error.value = ''
  try {
    const params = {}
    if (filtroPeriodo.value) params.periodo_id = filtroPeriodo.value
    if (busqueda.value) params.q = busqueda.value
    const res = await reportesService.libroMayor(params)
    cuentas.value = res.cuentas
    total.value = res.total
  } catch (e) {
    error.value = `No se pudo cargar el mayor. (${e.message})`
  } finally {
    cargando.value = false
  }
}

async function recargarTodo() {
  detalles.value = {}
  cuentasAbiertas.value = {}
  cargandoDetalles.value = {}
  cargandoMas.value = {}
  await cargarResumen()
}

onMounted(async () => {
  try {
    const perRes = await asientosService.periodos()
    periodos.value = perRes.periodos.map(p => ({ ...p, anio: String(p.anio) }))
  } catch (e) {
    error.value = e.message
  }
  await cargarResumen()
})
</script>
