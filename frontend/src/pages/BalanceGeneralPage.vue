<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div>
        <div class="text-h5">Balance General</div>
        <div v-if="datos.fecha_corte" class="text-caption text-grey-7">
          Saldos acumulados al {{ fechaFmt(datos.fecha_corte) }}<span v-if="datos.fecha_apertura">
            · desde la apertura del {{ fechaFmt(datos.fecha_apertura) }}</span
          ><span v-else> · desde el inicio del historial contabilizado</span>
        </div>
      </div>
      <q-badge
        :color="datos.cuadrado ? 'positive' : 'negative'"
        class="q-ml-sm"
      >
        {{
          datos.cuadrado ? 'CUADRADO' : `DIFERENCIA ${fmt(datos.diferencia)}`
        }}
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
          @update:model-value="cargar"
        />
      </div>
      <div class="col-12 col-md-8 row items-center q-gutter-md">
        <q-chip color="blue-1">Activo: {{ fmt(datos.activo.total) }}</q-chip>
        <q-chip color="orange-1">
          Pasivo + Patrimonio: {{ fmt(datos.total_pasivo_patrimonio) }}
        </q-chip>
      </div>
    </div>

    <q-card v-if="cargando" flat bordered class="text-center q-pa-md q-mb-md">
      <q-spinner color="primary" size="24px" />
      <span class="q-ml-sm">Calculando balance…</span>
    </q-card>

    <template v-else>
      <SeccionBalance
        titulo="ACTIVO"
        :rubros="datos.activo.rubros"
        :total="datos.activo.total"
        color="primary"
      />
      <SeccionBalance
        titulo="PASIVO"
        :rubros="datos.pasivo.rubros"
        :total="datos.pasivo.total"
        color="orange-8"
        class="q-mt-md"
      />
      <q-card flat bordered class="q-mt-md">
        <q-card-section class="row items-center">
          <div class="text-subtitle1">PATRIMONIO</div>
          <q-space />
          <q-chip color="purple-3"
            >Total: {{ fmt(datos.patrimonio.total) }}</q-chip
          >
        </q-card-section>
        <q-card-section
          v-for="r in datos.patrimonio.rubros"
          :key="r.codigo"
          class="q-pt-none"
        >
          <div class="row items-center q-mb-xs">
            <div class="text-subtitle2">{{ r.codigo }} · {{ r.nombre }}</div>
            <q-space />
            <span class="text-weight-medium">{{ fmt(r.saldo) }}</span>
          </div>
          <q-list dense bordered separator class="q-mb-sm">
            <q-item v-for="l in r.lineas" :key="l.codigo">
              <q-item-section>{{ l.codigo }} · {{ l.nombre }}</q-item-section>
              <q-item-section side>{{ fmt(l.saldo) }}</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-section class="row items-center">
          <div>Resultado del ejercicio (de Pérdidas y Ganancias)</div>
          <q-space />
          <span class="text-weight-medium">{{
            fmt(datos.patrimonio.resultado_ejercicio)
          }}</span>
        </q-card-section>
      </q-card>
    </template>
  </q-page>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'
import { ref, onMounted } from 'vue'
import { reportesService } from '@/services/reportesService.js'
import { asientosService } from '@/services/asientosService.js'
import SeccionBalance from '@/components/SeccionBalance.vue'
import { descargarCsv, imprimirPdf } from '@/utils/exportacion.js'

const auth = useAuthStore()
const datos = ref({
  activo: { total: 0, rubros: [] },
  pasivo: { total: 0, rubros: [] },
  patrimonio: { total: 0, rubros: [], resultado_ejercicio: 0 },
  total_pasivo_patrimonio: 0,
  cuadrado: true,
  diferencia: 0,
  fecha_corte: null,
  fecha_apertura: null
})
const cargando = ref(false)
const error = ref('')
const filtroPeriodo = ref(null)
const periodos = ref([])

function fmt(v) {
  return Number(v || 0).toFixed(2)
}

function fechaFmt(v) {
  if (!v) return ''
  const [anio, mes, dia] = String(v).slice(0, 10).split('-')
  return `${dia}/${mes}/${anio}`
}

function exportar() {
  const filas = []
  for (const [grupo, bloque] of [
    ['Activo', datos.value.activo],
    ['Pasivo', datos.value.pasivo],
    ['Patrimonio', datos.value.patrimonio]
  ]) {
    for (const rubro of bloque.rubros || []) {
      filas.push({
        grupo,
        codigo: rubro.codigo,
        nombre: rubro.nombre,
        saldo: rubro.saldo
      })
      for (const linea of rubro.lineas || [])
        filas.push({
          grupo,
          codigo: linea.codigo,
          nombre: linea.nombre,
          saldo: linea.saldo
        })
    }
  }
  descargarCsv(
    'balance-general',
    [
      { label: 'Grupo', field: 'grupo' },
      { label: 'Código', field: 'codigo' },
      { label: 'Cuenta', field: 'nombre' },
      { label: 'Saldo', field: 'saldo' }
    ],
    filas
  )
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    datos.value = await reportesService.balanceGeneral(
      filtroPeriodo.value || undefined
    )
  } catch (e) {
    error.value = `No se pudo cargar el balance. (${e.message})`
  } finally {
    cargando.value = false
  }
}

onMounted(async () => {
  try {
    const perRes = await asientosService.periodos()
    periodos.value = perRes.periodos
      .map(p => ({ ...p, anio: String(p.anio) }))
      .sort((a, b) => String(b.fecha_fin).localeCompare(String(a.fecha_fin)))
    if (periodos.value.length) filtroPeriodo.value = periodos.value[0].id
  } catch (e) {
    error.value = e.message
  }
  await cargar()
})
</script>
