<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Pérdidas y Ganancias</div>
      <q-badge :color="badgeColor" class="q-ml-sm">
        {{ datos.resultado }}: {{ fmt(datos.utilidad_neta) }}
      </q-badge>
      <q-space />
      <q-btn flat icon="table_view" label="CSV" @click="exportar" />
      <q-btn flat icon="picture_as_pdf" label="PDF" @click="imprimirPdf" />
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
    </div>

    <q-card v-if="cargando" flat bordered class="text-center q-pa-md q-mb-md">
      <q-spinner color="primary" size="24px" />
      <span class="q-ml-sm">Calculando resultados…</span>
    </q-card>

    <template v-else>
      <div class="text-subtitle1 q-mb-sm">Ingresos (clase 5)</div>
      <q-table
        :rows="datos.ingresos.lineas"
        :columns="columnas"
        row-key="codigo"
        :pagination="{ rowsPerPage: 0 }"
        hide-pagination
        no-data-label="Sin ingresos en el periodo"
        class="q-mb-md"
      />

      <div class="text-subtitle1 q-mb-sm">Costos y Gastos (clase 4)</div>
      <q-table
        :rows="datos.gastos.lineas"
        :columns="columnas"
        row-key="codigo"
        :pagination="{ rowsPerPage: 0 }"
        hide-pagination
        no-data-label="Sin costos ni gastos en el periodo"
        class="q-mb-md"
      />

      <q-card class="opti-card">
        <q-card-section class="row items-center q-gutter-md">
          <q-chip color="green-2"
            >Ingresos: {{ fmt(datos.ingresos.total) }}</q-chip
          >
          <q-chip color="red-2">Gastos: {{ fmt(datos.gastos.total) }}</q-chip>
          <q-chip :color="badgeColor" text-color="white">
            {{ datos.resultado }} neta: {{ fmt(datos.utilidad_neta) }}
          </q-chip>
        </q-card-section>
      </q-card>
    </template>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { reportesService } from '@/services/reportesService.js'
import { asientosService } from '@/services/asientosService.js'
import { descargarCsv, imprimirPdf } from '@/utils/exportacion.js'

const datos = ref({
  ingresos: { total: 0, lineas: [] },
  gastos: { total: 0, lineas: [] },
  utilidad_neta: 0,
  resultado: 'EQUILIBRIO'
})
const cargando = ref(false)
const error = ref('')
const filtroPeriodo = ref(null)
const periodos = ref([])

const columnas = [
  { name: 'codigo', label: 'Código', field: 'codigo', align: 'left' },
  { name: 'nombre', label: 'Cuenta', field: 'nombre', align: 'left' },
  {
    name: 'total',
    label: 'Total',
    field: 'total',
    align: 'right',
    format: v => Number(v).toFixed(2)
  }
]

function exportar() {
  const filas = [
    ...datos.value.ingresos.lineas.map(fila => ({ ...fila, tipo: 'Ingreso' })),
    ...datos.value.gastos.lineas.map(fila => ({ ...fila, tipo: 'Costo/Gasto' }))
  ]
  descargarCsv(
    'estado-resultados',
    [
      { label: 'Tipo', field: 'tipo' },
      ...columnas.map(col => ({ label: col.label, field: col.field }))
    ],
    filas
  )
}

const badgeColor = computed(() =>
  datos.value.resultado === 'UTILIDAD'
    ? 'positive'
    : datos.value.resultado === 'PERDIDA'
      ? 'negative'
      : 'grey-7'
)

function fmt(v) {
  return Number(v || 0).toFixed(2)
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    datos.value = await reportesService.resultados(
      filtroPeriodo.value || undefined
    )
  } catch (e) {
    error.value = `No se pudo cargar resultados. (${e.message})`
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
