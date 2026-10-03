<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Balance Inicial"
      description="Asiento de apertura (tipo APERTURA) del 01/01 del periodo. Es una transacción normal pero marcada como inicial."
      :endpoints="[
        'POST /api/asientos (tipo=APERTURA)',
        'GET /api/asientos?tipo=APERTURA'
      ]"
      :pendientes="[
        'Botón destacado que abre el formulario ya con tipo APERTURA',
        'Validar que solo exista una apertura por periodo'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
