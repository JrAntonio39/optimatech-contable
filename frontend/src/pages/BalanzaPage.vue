<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Balanza de Comprobación</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} cuenta(s)</q-badge>
      <q-badge :color="cuadrada ? 'positive' : 'negative'" class="q-ml-sm">
        {{ cuadrada ? 'CUADRADA' : 'DESCUADRADA' }}
      </q-badge>
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
          @update:model-value="cargar"
        />
      </div>
    </div>

    <q-card v-if="cargando" flat bordered class="text-center q-pa-md">
      <q-spinner color="primary" size="24px" />
      <span class="q-ml-sm">Cargando balanza…</span>
    </q-card>

    <q-card v-else flat bordered>
      <q-markup-table flat bordered separator="cell" dense>
        <thead>
          <tr class="bg-primary text-white">
            <th rowspan="2" class="text-right">N°</th>
            <th rowspan="2" class="text-left">Cuentas</th>
            <th colspan="2" class="text-center">Saldos</th>
          </tr>
          <tr class="bg-primary text-white">
            <th class="text-right">Deudor</th>
            <th class="text-right">Acreedor</th>
          </tr>
        </thead>
        <tbody v-if="lineas.length">
          <tr v-for="(linea, indice) in lineas" :key="linea.codigo">
            <td class="text-right">{{ indice + 1 }}</td>
            <td>{{ linea.codigo }} · {{ linea.nombre }}</td>
            <td class="text-right">
              {{ linea.saldo_deudor > 0 ? `$ ${fmt(linea.saldo_deudor)}` : '' }}
            </td>
            <td class="text-right">
              {{ linea.saldo_acreedor > 0 ? `$ ${fmt(linea.saldo_acreedor)}` : '' }}
            </td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr>
            <td colspan="4" class="text-center text-grey-7 q-pa-lg">
              Sin movimientos en el período seleccionado.
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="text-weight-bold">
            <td colspan="2">Total</td>
            <td class="text-right">$ {{ fmt(totales.saldo_deudor) }}</td>
            <td class="text-right">$ {{ fmt(totales.saldo_acreedor) }}</td>
          </tr>
        </tfoot>
      </q-markup-table>
    </q-card>
  </q-page>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { ref, onMounted } from 'vue'
import { reportesService } from '@/services/reportesService.js'
import { asientosService } from '@/services/asientosService.js'
import { descargarCsv, imprimirPdf } from '@/utils/exportacion.js'

const auth = useAuthStore()
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

const columnasCsv = [
  { label: 'N°', value: fila => lineas.value.indexOf(fila) + 1 },
  { label: 'Cuenta', value: fila => `${fila.codigo} · ${fila.nombre}` },
  { label: 'Saldo Deudor', field: 'saldo_deudor' },
  { label: 'Saldo Acreedor', field: 'saldo_acreedor' }
]

function exportar() {
  descargarCsv('balanza-comprobacion', columnasCsv, lineas.value)
}

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
