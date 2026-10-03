<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Balance General"
      description="Situación financiera: Activo = Pasivo + Patrimonio (clases 1, 2 y 3). Se calcula solo."
      :endpoints="['GET /api/balance-general?periodo_id=1']"
      :pendientes="[
        'Endpoint /api/balance-general en FastAPI',
        'Secciones Activo / Pasivo / Patrimonio'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
