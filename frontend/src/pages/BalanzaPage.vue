<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Balanza de Comprobación"
      description="Sumas y saldos deudores/acreedores de las cuentas de mayor (nivel 3). Se calcula sola."
      :endpoints="['GET /api/balanza (vista v_balanza_comprobacion)']"
      :pendientes="[
        'Endpoint /api/balanza en FastAPI',
        'Tabla con sumas debe/haber y saldos deudor/acreedor'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
