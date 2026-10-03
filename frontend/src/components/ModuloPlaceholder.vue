<template>
  <q-card class="opti-card q-mb-md">
    <q-card-section>
      <div class="text-h6">{{ title }}</div>
      <div class="text-body2 text-grey-7">{{ description }}</div>
    </q-card-section>

    <q-card-section v-if="endpoints && endpoints.length">
      <div class="text-subtitle2 q-mb-sm">API que usará este módulo</div>
      <q-chip
        v-for="ep in endpoints"
        :key="ep"
        color="blue-grey-1"
        text-color="dark"
        icon="link"
        class="q-mr-xs q-mb-xs"
      >
        {{ ep }}
      </q-chip>
    </q-card-section>

    <q-card-section v-if="pendientes && pendientes.length">
      <div class="text-subtitle2 q-mb-sm">Pendiente de implementar</div>
      <q-list dense bordered class="rounded-borders">
        <q-item v-for="p in pendientes" :key="p">
          <q-item-section avatar>
            <q-icon name="hourglass_empty" color="orange" />
          </q-item-section>
          <q-item-section>{{ p }}</q-item-section>
        </q-item>
      </q-list>
    </q-card-section>

    <q-card-actions align="left">
      <q-btn flat color="primary" icon="home" label="Volver al inicio" to="/" />
    </q-card-actions>
  </q-card>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  endpoints: { type: Array, default: () => [] },
  pendientes: { type: Array, default: () => [] }
})
</script>
