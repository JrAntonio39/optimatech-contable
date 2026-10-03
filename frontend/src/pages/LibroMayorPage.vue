<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Libro Mayor"
      description="Mayorización: saldos acumulados por cuenta. Se calcula solo desde el detalle de asientos."
      :endpoints="['GET /api/libro-mayor (vista v_libro_mayor)']"
      :pendientes="[
        'Endpoint /api/libro-mayor en FastAPI',
        'Selector de cuenta + tabla debe/haber/saldo'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
