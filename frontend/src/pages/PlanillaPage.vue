<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Pago de Salarios"
      description="Planilla mensual por empleado (ISSS, AFP, Renta). Al cerrar: Debe Costos Personal 4.1.1.09 / Haber Sueldos por Pagar 2.1.4 + 2.1.5."
      :endpoints="[
        'GET /api/empleados',
        'POST /api/planillas',
        'POST /api/planillas/{id}/contabilizar'
      ]"
      :pendientes="[
        'Endpoints de empleados y planillas en FastAPI',
        'Cálculo automático del líquido a pagar en Vue'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
