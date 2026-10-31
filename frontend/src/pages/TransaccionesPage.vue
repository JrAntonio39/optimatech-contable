<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">Registrar Transacción</div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>
    <q-banner v-if="ok" class="bg-green-1 text-green-9 q-mb-md" rounded>
      {{ ok }}
    </q-banner>
    <q-card class="opti-card q-mb-md">
      <q-card-section>
        <div class="text-subtitle1 q-mb-md">Datos del asiento</div>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-md-2">
            <q-input
              v-model="cab.fecha"
              type="date"
              label="Fecha"
              outlined
              dense
              :error="!!errorFecha"
              :error-message="errorFecha"
            />
            <div v-if="periodoSeleccionado" class="text-caption text-grey-7 q-mt-xs">
              Fechas permitidas: {{ mostrarFecha(periodoSeleccionado.fecha_inicio) }} a
              {{ mostrarFecha(periodoSeleccionado.fecha_fin) }}.
              Si cambias de período, la fecha se ajustará dentro de ese rango.
            </div>
          </div>
          <div class="col-12 col-md-4">
            <q-input v-model="cab.concepto" label="Concepto" outlined dense />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="cab.tipo"
              :options="tipos"
              label="Tipo"
              outlined
              dense
              emit-value
              map-options
            />
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="cab.periodo_id"
              :options="periodosAbiertos"
              option-value="id"
              option-label="anio"
              label="Periodo"
              outlined
              dense
              emit-value
              map-options
            />
            <div v-if="!periodosAbiertos.length" class="text-caption text-negative q-mt-xs">
              No hay períodos abiertos. Abre un período desde Control y auditoría para registrar asientos.
            </div>
          </div>
          <div class="col-12 col-md-2">
            <q-select
              v-model="cab.sucursal_id"
              :options="sucursales"
              option-value="id"
              option-label="nombre"
              label="Sucursal"
              outlined
              dense
              emit-value
              map-options
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-card class="opti-card q-mb-md">
      <q-card-section>
        <div class="row items-center q-mb-md">
          <div class="text-subtitle1">Líneas (partida doble)</div>
          <q-space />
          <q-btn
            color="primary"
            outline
            icon="add"
            label="Agregar línea"
            dense
            @click="agregarLinea"
          />
        </div>

        <div
          v-for="(lin, i) in lineas"
          :key="i"
          class="row q-col-gutter-md q-mb-sm items-center"
        >
          <div class="col-12 col-md-5">
            <q-select
              v-model="lin.cuenta_codigo"
              :options="opcionesCuentas"
              label="Cuenta (solo hojas)"
              outlined
              dense
              use-input
              fill-input
              hide-selected
              emit-value
              map-options
              input-debounce="200"
              @filter="filtrarCuentas"
            />
          </div>
          <div class="col-6 col-md-2">
            <q-input
              v-model.number="lin.debe"
              type="number"
              min="0"
              step="0.01"
              label="Debe"
              outlined
              dense
              @update:model-value="
                () => {
                  if (lin.debe > 0) lin.haber = 0
                }
              "
            />
          </div>
          <div class="col-6 col-md-2">
            <q-input
              v-model.number="lin.haber"
              type="number"
              min="0"
              step="0.01"
              label="Haber"
              outlined
              dense
              @update:model-value="
                () => {
                  if (lin.haber > 0) lin.debe = 0
                }
              "
            />
          </div>
          <div class="col-10 col-md-2">
            <q-input v-model="lin.descripcion" label="Detalle" outlined dense />
          </div>
          <div class="col-2 col-md-1">
            <q-btn
              flat
              round
              color="negative"
              icon="delete"
              :disable="lineas.length <= 2"
              @click="lineas.splice(i, 1)"
            />
          </div>
        </div>
      </q-card-section>

      <q-card-section class="row items-center q-gutter-md">
        <q-chip color="blue-1">Debe: {{ totalDebe.toFixed(2) }}</q-chip>
        <q-chip color="orange-1">Haber: {{ totalHaber.toFixed(2) }}</q-chip>
        <q-chip :color="cuadrado ? 'green-3' : 'red-3'">
          {{
            cuadrado && totalDebe > 0
              ? 'CUADRADO'
              : `DESCUADRADO (dif. ${Math.abs(totalDebe - totalHaber).toFixed(2)})`
          }}
        </q-chip>
        <q-space />
        <q-btn
          color="primary"
          icon="save"
          label="Guardar asiento"
          :loading="guardando"
          :disable="!puedeGuardar"
          @click="guardar"
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { asientosService, TIPOS_ASIENTO } from '@/services/asientosService.js'
import { cuentasService } from '@/services/cuentasService.js'

const route = useRoute()

const tipos = TIPOS_ASIENTO.map(t => ({
  label:
    t === 'DIARIO' ? 'Normal (DIARIO)' : t.charAt(0) + t.slice(1).toLowerCase(),
  value: t
}))

function fechaLocalHoy() {
  const hoy = new Date()
  hoy.setMinutes(hoy.getMinutes() - hoy.getTimezoneOffset())
  return hoy.toISOString().slice(0, 10)
}

const cab = ref({
  fecha: fechaLocalHoy(),
  concepto: '',
  tipo: 'DIARIO',
  periodo_id: null,
  sucursal_id: null
})
const lineas = ref([
  { cuenta_codigo: null, debe: 0, haber: 0, descripcion: '' },
  { cuenta_codigo: null, debe: 0, haber: 0, descripcion: '' }
])
const periodos = ref([])
const periodosAbiertos = computed(() => periodos.value.filter(p => p.estado === 'ABIERTO'))
const periodoSeleccionado = computed(() =>
  periodos.value.find(p => p.id === cab.value.periodo_id) || null
)
const errorFecha = computed(() => {
  const periodo = periodoSeleccionado.value
  if (!periodo || !cab.value.fecha) return ''
  if (cab.value.fecha < periodo.fecha_inicio || cab.value.fecha > periodo.fecha_fin) {
    return `La fecha no corresponde al período ${periodo.anio}. Elige una entre ${mostrarFecha(periodo.fecha_inicio)} y ${mostrarFecha(periodo.fecha_fin)}.`
  }
  return ''
})
const sucursales = ref([])
const hojas = ref([])
const opcionesCuentas = ref([])
const guardando = ref(false)
const error = ref('')
const ok = ref('')

const totalDebe = computed(() =>
  lineas.value.reduce((s, l) => s + (parseFloat(l.debe) || 0), 0)
)
const totalHaber = computed(() =>
  lineas.value.reduce((s, l) => s + (parseFloat(l.haber) || 0), 0)
)
const cuadrado = computed(
  () => totalDebe.value.toFixed(2) === totalHaber.value.toFixed(2)
)
const lineasValidas = computed(() =>
  lineas.value.every(l => {
    const d = parseFloat(l.debe) || 0
    const h = parseFloat(l.haber) || 0
    return l.cuenta_codigo && ((d > 0 && h === 0) || (h > 0 && d === 0))
  })
)
const puedeGuardar = computed(
  () =>
    !guardando.value &&
    cab.value.concepto.trim().length >= 3 &&
    cab.value.periodo_id &&
    lineas.value.length >= 2 &&
    lineasValidas.value &&
    !errorFecha.value &&
    periodoSeleccionado.value?.estado === 'ABIERTO' &&
    cuadrado.value &&
    totalDebe.value > 0
)

function mostrarFecha(fecha) {
  if (!fecha) return ''
  const [anio, mes, dia] = String(fecha).slice(0, 10).split('-')
  return `${dia}/${mes}/${anio}`
}

watch(
  () => cab.value.periodo_id,
  id => {
    const periodo = periodos.value.find(p => p.id === id)
    if (!periodo) return
    if (cab.value.fecha < periodo.fecha_inicio || cab.value.fecha > periodo.fecha_fin) {
      cab.value.fecha = periodo.fecha_inicio
    }
    error.value = ''
  }
)

function agregarLinea() {
  lineas.value.push({ cuenta_codigo: null, debe: 0, haber: 0, descripcion: '' })
}

function filtrarCuentas(val, update) {
  update(() => {
    const lista = hojas.value.map(c => ({
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

async function cargarBase() {
  try {
    const [cuentasRes, perRes, sucRes] = await Promise.all([
      cuentasService.listar(),
      asientosService.periodos(),
      asientosService.sucursales()
    ])
    const todas = cuentasRes.cuentas
    const padres = new Set(todas.map(c => c.codigo_padre).filter(Boolean))
    hojas.value = todas.filter(c => !padres.has(c.codigo))
    periodos.value = perRes.periodos.map(p => ({ ...p, anio: String(p.anio) }))
    sucursales.value = sucRes.sucursales
    const hoy = fechaLocalHoy()
    const periodoInicial = periodosAbiertos.value.find(p => p.fecha_inicio <= hoy && hoy <= p.fecha_fin)
      || periodosAbiertos.value[0]
    if (periodoInicial) cab.value.periodo_id = periodoInicial.id
    if (sucursales.value.length && !cab.value.sucursal_id)
      cab.value.sucursal_id = sucursales.value[0].id
  } catch (e) {
    error.value = `No se pudo cargar datos base. ¿Está el backend en http://localhost:8000? (${e.message})`
  }
}

async function guardar() {
  error.value = ''
  ok.value = ''
  if (errorFecha.value) {
    error.value = errorFecha.value
    return
  }
  if (!periodoSeleccionado.value || periodoSeleccionado.value.estado !== 'ABIERTO') {
    error.value = 'Selecciona un período contable abierto para registrar el asiento.'
    return
  }
  guardando.value = true
  try {
    const res = await asientosService.crear({
      fecha: cab.value.fecha,
      concepto: cab.value.concepto.trim(),
      tipo: cab.value.tipo,
      periodo_id: cab.value.periodo_id,
      sucursal_id: cab.value.sucursal_id,
      detalles: lineas.value.map(l => ({
        cuenta_codigo: l.cuenta_codigo,
        debe: parseFloat(l.debe) || 0,
        haber: parseFloat(l.haber) || 0,
        descripcion: l.descripcion || undefined
      }))
    })
    ok.value = `Asiento ${res.asiento.codigo} guardado (${res.estado_partida}, debe ${res.total_debe}).`
    lineas.value = [
      { cuenta_codigo: null, debe: 0, haber: 0, descripcion: '' },
      { cuenta_codigo: null, debe: 0, haber: 0, descripcion: '' }
    ]
    cab.value.concepto = ''
  } catch (e) {
    error.value = e.message
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  const t = String(route.query.tipo || '').toUpperCase()
  if (['APERTURA', 'DIARIO', 'AJUSTE', 'CIERRE'].includes(t)) cab.value.tipo = t
  await cargarBase()
})
</script>
