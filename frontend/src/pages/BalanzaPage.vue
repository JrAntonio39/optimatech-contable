<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Balanza de Comprobación</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} cuenta(s)</q-badge>
      <q-badge :color="cuadrada ? 'positive' : 'negative'" class="q-ml-sm">
        {{ cuadrada ? 'CUADRADA' : 'DESCUADRADA' }}
      </q-badge>
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
          @update:model-value="cargar"
        />
      </div>
      <div class="col-12 col-md-8 row items-center q-gutter-md">
        <q-chip color="blue-1"
          >Sumas debe: {{ fmt(totales.sumas_debe) }}</q-chip
        >
        <q-chip color="orange-1"
          >Sumas haber: {{ fmt(totales.sumas_haber) }}</q-chip
        >
        <q-chip color="green-3"
          >Saldos deudores: {{ fmt(totales.saldo_deudor) }}</q-chip
        >
        <q-chip color="purple-3"
          >Saldos acreedores: {{ fmt(totales.saldo_acreedor) }}</q-chip
        >
      </div>
    </div>

    <q-card v-if="cargando" flat bordered class="text-center q-pa-md">
      <q-spinner color="primary" size="24px" />
      <span class="q-ml-sm">Cargando balanza…</span>
    </q-card>

    <q-table
      v-else
      :rows="lineas"
      :columns="columnas"
      row-key="codigo"
      :pagination="{ rowsPerPage: 15 }"
      :rows-per-page-options="[10, 15, 30, 0]"
      no-data-label="Sin movimientos en el periodo"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reportesService } from '@/services/reportesService.js'
import { asientosService } from '@/services/asientosService.js'

const lineas = ref([])
const totales = ref({
  sumas_debe: 0,
  sumas_haber: 0,
  saldo_deudor: 0,
  saldo_acreedor: 0
})
const cuadrada = ref(true)
const total = ref(0)
const cargando = ref(false)
const error = ref('')
const filtroPeriodo = ref(null)
const periodos = ref([])

const columnas = [
  {
    name: 'codigo',
    label: 'Código',
    field: 'codigo',
    align: 'left',
    sortable: true
  },
  { name: 'nombre', label: 'Nombre', field: 'nombre', align: 'left' },
  {
    name: 'sumas_debe',
    label: 'Sumas Debe',
    field: 'sumas_debe',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  {
    name: 'sumas_haber',
    label: 'Sumas Haber',
    field: 'sumas_haber',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  {
    name: 'saldo_deudor',
    label: 'Saldo Deudor',
    field: 'saldo_deudor',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  {
    name: 'saldo_acreedor',
    label: 'Saldo Acreedor',
    field: 'saldo_acreedor',
    align: 'right',
    format: v => Number(v).toFixed(2)
  }
]

function fmt(v) {
  return Number(v || 0).toFixed(2)
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const res = await reportesService.balanza(filtroPeriodo.value || undefined)
    lineas.value = res.lineas
    totales.value = res.totales
    cuadrada.value = res.cuadrada
    total.value = res.total
  } catch (e) {
    error.value = `No se pudo cargar la balanza. (${e.message})`
  } finally {
    cargando.value = false
  }
}

onMounted(async () => {
  try {
    const perRes = await asientosService.periodos()
    periodos.value = perRes.periodos.map(p => ({ ...p, anio: String(p.anio) }))
  } catch (e) {
    error.value = e.message
  }
  await cargar()
})
</script>
