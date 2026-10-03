<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Catálogo de Cuentas</div>
      <q-badge color="primary" class="q-ml-sm">{{ total }} cuentas</q-badge>
      <q-space />
      <q-btn
        color="primary"
        icon="add"
        label="Agregar cuenta"
        @click="abrirDialogo"
      />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>
    <q-banner v-if="ok" class="bg-green-1 text-green-9 q-mb-md" rounded>
      {{ ok }}
    </q-banner>

    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12">
        <q-input
          v-model="busqueda"
          label="Buscar por código o nombre"
          outlined
          dense
          clearable
          debounce="400"
        >
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
    </div>

    <q-card flat bordered>
      <q-card-section v-if="cargando" class="text-center q-pa-md">
        <q-spinner color="primary" size="24px" />
        <span class="q-ml-sm">Cargando catálogo…</span>
      </q-card-section>
      <q-tree
        v-else
        :nodes="arbol"
        node-key="codigo"
        v-model:selected="seleccionado"
        selected-color="primary"
        :filter="busqueda"
        :filter-method="filtrarNodo"
        no-results-label="Sin coincidencias"
      >
        <template #default-header="prop">
          <div class="row items-center q-gutter-x-sm">
            <span class="text-weight-medium">{{ prop.node.codigo }}</span>
            <span>{{ prop.node.nombre }}</span>
            <q-badge outline color="grey-7">{{ prop.node.naturaleza }}</q-badge>
          </div>
        </template>
      </q-tree>
    </q-card>

    <q-card v-if="seleccionada" class="opti-card q-mt-md">
      <q-card-section>
        <div class="text-subtitle1">
          {{ seleccionada.cuenta.codigo }} — {{ seleccionada.cuenta.nombre }}
        </div>
        <div class="text-caption text-grey-7">
          Naturaleza {{ seleccionada.cuenta.naturaleza }} · Nivel
          {{ seleccionada.cuenta.nivel }}
        </div>
      </q-card-section>
      <q-card-section>
        <div class="text-subtitle2 q-mb-sm"
          >Subcuentas ({{ seleccionada.hijos.length }})</div
        >
        <q-chip
          v-for="h in seleccionada.hijos"
          :key="h.codigo"
          icon="subdirectory_arrow_right"
        >
          {{ h.codigo }} · {{ h.nombre }}
        </q-chip>
        <div v-if="!seleccionada.hijos.length" class="text-caption text-grey-7">
          Es cuenta hoja: permite movimientos en asientos.
        </div>
      </q-card-section>
    </q-card>

    <q-dialog v-model="dialogo">
      <q-card style="min-width: 380px">
        <q-card-section>
          <div class="text-h6">Agregar cuenta</div>
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input
            v-model="form.codigo"
            label="Código (ej: 1.1.1.04)"
            outlined
            dense
          />
          <q-input v-model="form.nombre" label="Nombre" outlined dense />
          <q-select
            v-model="form.naturaleza"
            :options="['Deudora', 'Acreedora', 'Deudora o Acreedora']"
            label="Naturaleza"
            outlined
            dense
          />
          <q-select
            v-model="form.padre"
            :options="opcionesPadre"
            label="Cuenta padre (vacío = nivel 1)"
            outlined
            dense
            clearable
            use-input
            fill-input
            hide-selected
            emit-value
            map-options
            input-debounce="200"
            @filter="filtrarPadre"
          />
          <div class="text-caption text-grey-7"
            >Nivel calculado: {{ nivelCalculado }}</div
          >
          <q-banner v-if="errorForm" class="bg-red-1 text-red" rounded dense>
            {{ errorForm }}
          </q-banner>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn
            color="primary"
            label="Guardar"
            :loading="guardando"
            @click="guardar"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { cuentasService } from '@/services/cuentasService.js'

const total = ref(0)
const cargando = ref(false)
const error = ref('')
const ok = ref('')
const busqueda = ref('')
const seleccionada = ref(null)
const seleccionado = ref(null)
const dialogo = ref(false)
const guardando = ref(false)
const errorForm = ref('')
const todas = ref([])

const form = ref({ codigo: '', nombre: '', naturaleza: 'Deudora', padre: null })

/** Árbol anidado desde la lista plana (padre -> hijos). Solo raíces al inicio. */
const arbol = computed(() => {
  const porPadre = {}
  todas.value.forEach(c => {
    const p = c.codigo_padre || '__root__'
    ;(porPadre[p] = porPadre[p] || []).push(c)
  })
  const armar = padre =>
    (porPadre[padre] || []).map(c => ({
      label: `${c.codigo} · ${c.nombre}`,
      codigo: c.codigo,
      nombre: c.nombre,
      naturaleza: c.naturaleza,
      nivel: c.nivel,
      children: armar(c.codigo)
    }))
  return armar('__root__')
})

/** Filtro del árbol: coincide por código o por nombre. */
function filtrarNodo(nodo, filtro) {
  const f = filtro.toLowerCase()
  return (
    nodo.codigo.toLowerCase().includes(f) ||
    nodo.nombre.toLowerCase().includes(f)
  )
}

/** Al elegir un nodo del árbol se muestra su detalle debajo. */
watch(seleccionado, codigo => {
  if (codigo) verDetalle(codigo)
})
const nivelPadre = computed(() => {
  if (!form.value.padre) return 0
  const p = todas.value.find(c => c.codigo === form.value.padre)
  return p ? p.nivel : 0
})
const nivelCalculado = computed(() =>
  form.value.padre ? nivelPadre.value + 1 : 1
)

const opcionesPadre = ref([])

function filtrarPadre(val, update) {
  update(() => {
    const lista = todas.value.map(c => ({
      label: `${c.codigo} · ${c.nombre}`,
      value: c.codigo
    }))
    opcionesPadre.value = val
      ? lista
          .filter(o => o.label.toLowerCase().includes(val.toLowerCase()))
          .slice(0, 50)
      : lista.slice(0, 50)
  })
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    // Se trae todo el catálogo una vez; el árbol y el buscador filtran en cliente.
    const res = await cuentasService.listar()
    todas.value = res.cuentas
    total.value = res.total
  } catch (e) {
    error.value = `No se pudo cargar el catálogo. ¿Está el backend disponible? (${e.message})`
  } finally {
    cargando.value = false
  }
}

async function verDetalle(codigo) {
  try {
    seleccionada.value = await cuentasService.detalle(codigo)
  } catch (e) {
    error.value = e.message
  }
}

function abrirDialogo() {
  form.value = { codigo: '', nombre: '', naturaleza: 'Deudora', padre: null }
  errorForm.value = ''
  dialogo.value = true
}

async function guardar() {
  errorForm.value = ''
  ok.value = ''
  if (!form.value.codigo.trim() || !form.value.nombre.trim()) {
    errorForm.value = 'Código y nombre son obligatorios.'
    return
  }
  guardando.value = true
  try {
    const res = await cuentasService.crear({
      codigo: form.value.codigo.trim(),
      nombre: form.value.nombre.trim(),
      naturaleza: form.value.naturaleza,
      nivel: nivelCalculado.value,
      codigo_padre: form.value.padre || null
    })
    dialogo.value = false
    ok.value = `Cuenta ${res.cuenta.codigo} creada.`
    todas.value = []
    await cargar()
  } catch (e) {
    errorForm.value = e.message
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
</script>
