<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Balance Inicial</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} apertura(s)</q-badge>
      <q-space />
      <q-btn
        v-if="auth.tienePermiso('asientos.crear')"
        color="primary"
        icon="add"
        label="Registrar balance inicial"
        @click="irARegistrar"
      />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>
    <q-card v-if="cargando" flat bordered class="text-center q-pa-md">
      <q-spinner color="primary" size="24px" />
      <span class="q-ml-sm">Cargando apertura…</span>
    </q-card>

    <q-table
      v-else
      :rows="aperturas"
      :columns="columnas"
      row-key="id"
      :pagination="{ rowsPerPage: 10 }"
      no-data-label="Aún no hay asiento de apertura registrado"
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
            <q-badge
              v-if="col.name === 'estado_partida'"
              :color="
                props.row.estado_partida === 'CUADRADO'
                  ? 'positive'
                  : 'negative'
              "
            >
              {{ col.value }}
            </q-badge>
            <span v-else>{{ col.value }}</span>
          </q-td>
        </q-tr>
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <div v-if="detalles[props.row.id]">
              <div class="q-mb-sm">
                <q-chip color="blue-1"
                  >Debe:
                  {{ detalles[props.row.id].total_debe.toFixed(2) }}</q-chip
                >
                <q-chip color="orange-1"
                  >Haber:
                  {{ detalles[props.row.id].total_haber.toFixed(2) }}</q-chip
                >
                <q-chip
                  :color="
                    detalles[props.row.id].estado_partida === 'CUADRADO'
                      ? 'green-3'
                      : 'red-3'
                  "
                >
                  {{ detalles[props.row.id].estado_partida }}
                </q-chip>
              </div>
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
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { asientosService } from '@/services/asientosService.js'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const auth = useAuthStore()
const aperturas = ref([])
const detalles = ref({})
const total = ref(0)
const cargando = ref(false)
const error = ref('')

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
  { name: 'concepto', label: 'Concepto', field: 'concepto', align: 'left' },
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
    name: 'estado_partida',
    label: 'Estado',
    field: 'estado_partida',
    align: 'center'
  }
]

function irARegistrar() {
  router.push({ path: '/transacciones', query: { tipo: 'APERTURA' } })
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
    const res = await asientosService.listar({ tipo: 'APERTURA' })
    aperturas.value = res.asientos
    total.value = res.total
  } catch (e) {
    error.value = `No se pudo cargar la apertura. (${e.message})`
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>
