<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Estado de Pérdidas y Ganancias"
      description="Ingresos (clase 5) menos costos y gastos (clase 4) del periodo. Se calcula solo."
      :endpoints="['GET /api/resultados?periodo_id=1']"
      :pendientes="[
        'Endpoint /api/resultados en FastAPI',
        'Desglose por 4.1 Costos, 4.1.4 Ventas, 5.1 Ingresos'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
