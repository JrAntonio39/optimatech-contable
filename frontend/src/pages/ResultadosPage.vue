<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Estado de resultados</div>
      <q-badge :color="badgeColor" class="q-ml-sm">
        {{ datos.resultado }}: {{ fmt(datos.utilidad_neta) }}
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

    <q-card v-if="cargando" flat bordered class="text-center q-pa-md q-mb-md">
      <q-spinner color="primary" size="24px" />
      <span class="q-ml-sm">Calculando resultados…</span>
    </q-card>

    <template v-else>
      <q-card class="opti-card estado-reporte">
        <q-card-section class="estado-encabezado text-center">
          <div class="text-overline text-primary">OptimaTech · Sistema Contable</div>
          <div class="text-h5">Estado de resultados</div>
          <div class="text-body2 text-grey-7">{{ periodoEtiqueta }}</div>
        </q-card-section>

        <q-markup-table flat separator="horizontal" class="estado-tabla">
          <thead>
            <tr>
              <th class="text-left">Concepto</th>
              <th class="text-right estado-monto">Importe</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(fila, index) in filasEstado"
              :key="`${fila.tipo}-${fila.codigo || index}`"
              :class="`estado-fila-${fila.tipo}`"
            >
              <td>{{ fila.concepto }}</td>
              <td class="text-right estado-monto">
                {{ fila.tipo === 'seccion' ? '' : fmt(fila.total) }}
              </td>
            </tr>
          </tbody>
        </q-markup-table>

        <q-card-section class="row items-center justify-between q-gutter-sm">
          <div class="text-caption text-grey-7">
            Se usan asientos vigentes y grupos del catálogo. Registra previamente los ajustes de inventario y el impuesto sobre la renta si corresponden.
          </div>
          <q-chip :color="badgeColor" text-color="white" icon="summarize">
            {{ datos.resultado }}: {{ fmt(datos.utilidad_neta) }}
          </q-chip>
        </q-card-section>
      </q-card>
    </template>
  </q-page>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { ref, computed, onMounted } from 'vue'
import { reportesService } from '@/services/reportesService.js'
import { asientosService } from '@/services/asientosService.js'
import { descargarCsv, imprimirPdf } from '@/utils/exportacion.js'

const auth = useAuthStore()
const seccionVacia = () => ({ total: 0, lineas: [] })

const datos = ref({
  ingresos: { total: 0, lineas: [] },
  gastos: { total: 0, lineas: [] },
  ingresos_operacionales: seccionVacia(),
  costos_ventas: seccionVacia(),
  utilidad_bruta: 0,
  gastos_operacionales: seccionVacia(),
  utilidad_operativa: 0,
  otros_ingresos: seccionVacia(),
  gastos_financieros: seccionVacia(),
  otros_gastos: seccionVacia(),
  utilidad_neta: 0,
  resultado: 'EQUILIBRIO'
})
const cargando = ref(false)
const error = ref('')
const filtroPeriodo = ref(null)
const periodos = ref([])

const periodoEtiqueta = computed(() => {
  if (!filtroPeriodo.value) return 'Todos los períodos'
  const periodo = periodos.value.find(p => p.id === filtroPeriodo.value)
  return periodo ? `Ejercicio ${periodo.anio}` : 'Período seleccionado'
})

const filasEstado = computed(() => {
  const filas = []
  const agregarSeccion = (titulo, seccion, subtotal = null) => {
    filas.push({ tipo: 'seccion', concepto: titulo })
    for (const linea of seccion.lineas) {
      filas.push({
        tipo: 'cuenta',
        codigo: linea.codigo,
        concepto: `${linea.codigo} · ${linea.nombre}`,
        total: linea.total
      })
    }
    if (subtotal) {
      filas.push({ tipo: 'subtotal', concepto: subtotal, total: seccion.total })
    }
  }

  agregarSeccion('Ingresos operacionales', datos.value.ingresos_operacionales, 'Total de ingresos operacionales')
  agregarSeccion('(-) Costos de ventas y servicios', datos.value.costos_ventas, 'Total de costos de ventas y servicios')
  filas.push({ tipo: 'resultado', concepto: 'Utilidad bruta', total: datos.value.utilidad_bruta })
  agregarSeccion('(-) Gastos operacionales', datos.value.gastos_operacionales, 'Total de gastos operacionales')
  filas.push({ tipo: 'resultado', concepto: 'Utilidad de operación', total: datos.value.utilidad_operativa })
  agregarSeccion('(+) Otros ingresos', datos.value.otros_ingresos, 'Total de otros ingresos')
  agregarSeccion('(-) Gastos financieros', datos.value.gastos_financieros, 'Total de gastos financieros')
  agregarSeccion('(-) Otros gastos', datos.value.otros_gastos, 'Total de otros gastos')
  filas.push({ tipo: 'final', concepto: 'Resultado del período', total: datos.value.utilidad_neta })
  return filas
})

function exportar() {
  descargarCsv('estado-resultados', [
    { label: 'Concepto', field: 'concepto' },
    { label: 'Importe', field: 'total' }
  ], filasEstado.value)
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

<style scoped>
.estado-reporte {
  width: min(100%, 960px);
  margin: 0 auto;
  overflow: hidden;
}

.estado-encabezado {
  padding: 26px 18px 20px;
  border-bottom: 1px solid var(--opti-border);
}

.estado-tabla {
  background: transparent;
}

.estado-tabla :deep(th) {
  color: var(--opti-muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.estado-monto {
  width: 190px;
  font-variant-numeric: tabular-nums;
}

.estado-tabla :deep(.estado-fila-seccion td) {
  padding-top: 16px;
  color: var(--opti-text);
  background: var(--opti-surface-raised);
  font-weight: 700;
}

.estado-tabla :deep(.estado-fila-cuenta td:first-child) {
  padding-left: 34px;
}

.estado-tabla :deep(.estado-fila-subtotal td) {
  border-top: 1px solid var(--opti-border);
  font-weight: 650;
}

.estado-tabla :deep(.estado-fila-resultado td) {
  border-top: 2px solid var(--opti-border);
  font-weight: 700;
}

.estado-tabla :deep(.estado-fila-final td) {
  border-top: 2px solid var(--primary);
  border-bottom: 3px double var(--primary);
  background: var(--opti-accent-soft);
  font-size: 15px;
  font-weight: 750;
}

@media print {
  .estado-reporte {
    width: 100%;
    border: 0;
  }
}
</style>
