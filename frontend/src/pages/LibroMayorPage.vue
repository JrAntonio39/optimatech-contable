<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Libro Mayor</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} cuenta(s)</q-badge>
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>

    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-md-6">
        <q-select
          v-model="cuentaSel"
          :options="opcionesCuentas"
          label="Cuenta (solo hojas con movimiento)"
          outlined
          dense
          use-input
          fill-input
          hide-selected
          emit-value
          map-options
          clearable
          input-debounce="200"
          @filter="filtrarCuentas"
          @update:model-value="cargarMovimientos"
        />
      </div>
      <div class="col-12 col-md-3">
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
      <div class="col-12 col-md-3">
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

    <div v-if="detalle" class="q-mb-md">
      <q-card class="opti-card">
        <q-card-section>
          <div class="text-subtitle1">
            {{ detalle.cuenta.codigo }} — {{ detalle.cuenta.nombre }}
          </div>
          <div class="text-caption text-grey-7">
            Naturaleza {{ detalle.cuenta.naturaleza }}
          </div>
        </q-card-section>
        <q-table
          :rows="detalle.movimientos"
          :columns="columnasMov"
          row-key="folio"
          :pagination="{ rowsPerPage: 15 }"
          :rows-per-page-options="[10, 15, 30, 0]"
          no-data-label="Sin movimientos"
        />
        <q-card-section class="row items-center q-gutter-md">
          <q-chip color="blue-1"
            >Debe: {{ detalle.total_debe.toFixed(2) }}</q-chip
          >
          <q-chip color="orange-1"
            >Haber: {{ detalle.total_haber.toFixed(2) }}</q-chip
          >
          <q-chip color="green-3"
            >Saldo: {{ detalle.saldo_final.toFixed(2) }}</q-chip
          >
        </q-card-section>
      </q-card>
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
      @row-click="(_, row) => seleccionar(row.codigo)"
    />
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reportesService } from '@/services/reportesService.js'
import { asientosService } from '@/services/asientosService.js'

const cuentas = ref([])
const detalle = ref(null)
const cuentaSel = ref(null)
const opcionesCuentas = ref([])
const periodos = ref([])
const filtroPeriodo = ref(null)
const busqueda = ref('')
const total = ref(0)
const cargando = ref(false)
const error = ref('')

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

const columnasMov = [
  { name: 'fecha', label: 'Fecha', field: 'fecha', align: 'left' },
  { name: 'folio', label: 'Folio', field: 'folio', align: 'left' },
  { name: 'concepto', label: 'Concepto', field: 'concepto', align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'tipo', align: 'center' },
  {
    name: 'debe',
    label: 'Debe',
    field: 'debe',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  {
    name: 'haber',
    label: 'Haber',
    field: 'haber',
    align: 'right',
    format: v => Number(v).toFixed(2)
  },
  {
    name: 'saldo_acumulado',
    label: 'Saldo',
    field: 'saldo_acumulado',
    align: 'right',
    format: v => Number(v).toFixed(2)
  }
]

function filtrarCuentas(val, update) {
  update(() => {
    const lista = cuentas.value.map(c => ({
      label: `${c.codigo} · ${c.nombre}`,
      value: c.codigo
    }))
    opcionesCuentas.value = val
      ? lista
          .filter(o => o.label.toLowerCase().includes(val.toLowerCase()))
          .slice(0, 50)
      : lista.slice(0, 50)
  })
}

function seleccionar(codigo) {
  cuentaSel.value = codigo
  cargarMovimientos()
}

async function cargarMovimientos() {
  if (!cuentaSel.value) {
    detalle.value = null
    return
  }
  try {
    detalle.value = await reportesService.mayorCuenta(
      cuentaSel.value,
      filtroPeriodo.value || undefined
    )
  } catch (e) {
    error.value = e.message
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
  detalle.value = null
  await cargarResumen()
  await cargarMovimientos()
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
