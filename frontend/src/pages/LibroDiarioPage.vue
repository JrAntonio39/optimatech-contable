<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Libro Diario"
      description="Lista de todos los asientos con sus líneas (partida doble). Solo vista: los datos vienen de Transacciones."
      :endpoints="['GET /api/asientos', 'GET /api/asientos/{id}']"
      :pendientes="[
        'Tabla con folio, fecha, concepto y totales',
        'Filtro por tipo y por periodo/sucursal'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
