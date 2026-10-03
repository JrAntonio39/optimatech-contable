<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Facturación Electrónica"
      description="Emitir facturas (CCF/FCON) a clientes. Al contabilizar: Debe Clientes 1.1.3.01 / Haber Ingresos 5.x + IVA Débito 2.1.10."
      :endpoints="[
        'GET /api/clientes',
        'POST /api/facturas',
        'POST /api/facturas/{id}/contabilizar'
      ]"
      :pendientes="[
        'Endpoints de clientes y facturas en FastAPI',
        'Formulario con líneas y cuenta de ingreso 5.x por línea'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
