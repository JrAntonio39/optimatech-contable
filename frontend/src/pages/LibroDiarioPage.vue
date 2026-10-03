<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Libro Diario</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} asiento(s)</q-badge>
      <q-space />
      <q-btn
        color="primary"
        icon="add"
        label="Nuevo asiento"
        @click="router.push('/transacciones')"
      />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>

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
          @update:model-value="cargar"
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
          @update:model-value="cargar"
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
          @update:model-value="cargar"
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
          <q-td v-for="col in props.cols.filter(c => c.name !== 'expand')" :key="col.name" :props="props">
            <q-badge v-if="col.name === 'tipo'" color="blue-8">{{ col.value }}</q-badge>
            <q-badge v-else-if="col.name === 'estado_partida'" :color="props.row.estado_partida === 'CUADRADO' ? 'positive' : 'negative'">
              {{ col.value }}
            </q-badge>
            <span v-else>{{ col.value }}</span>
          </q-td>
        </q-tr>
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <div v-if="detalles[props.row.id]">
              <q-list dense bordered separator>
                <q-item v-for="l in detalles[props.row.id].detalles" :key="l.id">
                  <q-item-section>
                    <q-item-label>{{ l.cuenta_codigo }} · {{ l.cuenta_nombre }}</q-item-label>
                    <q-item-label v-if="l.descripcion" caption>{{ l.descripcion }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <span v-if="l.debe > 0">Debe {{ Number(l.debe).toFixed(2) }}</span>
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
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { asientosService } from '@/services/asientosService.js'

const router = useRouter()
const asientos = ref([])
const detalles = ref({})
const total = ref(0)
const cargando = ref(false)
const error = ref('')
const filtroTipo = ref(null)
const filtroPeriodo = ref(null)
const filtroSucursal = ref(null)
const periodos = ref([])
const sucursales = ref([])

const tipos = [
  { label: 'Todos', value: null },
  { label: 'Apertura', value: 'APERTURA' },
  { label: 'Normal', value: 'DIARIO' },
  { label: 'Ajuste', value: 'AJUSTE' },
  { label: 'Cierre', value: 'CIERRE' }
]

const columnas = [
  { name: 'expand', label: '', field: 'expand', align: 'center' },
  { name: 'codigo', label: 'Folio', field: 'codigo', align: 'left', sortable: true },
  { name: 'fecha', label: 'Fecha', field: 'fecha', align: 'left', sortable: true },
  { name: 'concepto', label: 'Concepto', field: 'concepto', align: 'left' },
  { name: 'tipo', label: 'Tipo', field: 'tipo', align: 'center' },
  {
    name: 'total_debe', label: 'Debe', field: 'total_debe',
    align: 'right', format: v => Number(v).toFixed(2)
  },
  {
    name: 'total_haber', label: 'Haber', field: 'total_haber',
    align: 'right', format: v => Number(v).toFixed(2)
  },
  { name: 'estado_partida', label: 'Estado', field: 'estado_partida', align: 'center' }
]

const sumaDebe = computed(() =>
  asientos.value.reduce((s, a) => s + (parseFloat(a.total_debe) || 0), 0)
)
const sumaHaber = computed(() =>
  asientos.value.reduce((s, a) => s + (parseFloat(a.total_haber) || 0), 0)
)

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
    const res = await asientosService.listar(params)
    asientos.value = res.asientos
    total.value = res.total
  } catch (e) {
    error.value = `No se pudo cargar el diario. (${e.message})`
  } finally {
    cargando.value = false
  }
}

onMounted(async () => {
  try {
    const [perRes, sucRes] = await Promise.all([
      asientosService.periodos(),
      asientosService.sucursales()
    ])
    periodos.value = perRes.periodos.map(p => ({ ...p, anio: String(p.anio) }))
    sucursales.value = sucRes.sucursales
  } catch (e) {
    error.value = e.message
  }
  await cargar()
})
</script>
