<template>
  <q-page padding>
    <ModuloPlaceholder
      title="Compras y Proveedores"
      description="Registrar compras (CCF de proveedor) para el Libro de Compras. Al contabilizar: Debe Inventario/Activo + IVA Crédito / Haber Proveedores."
      :endpoints="[
        'GET /api/proveedores',
        'POST /api/compras',
        'POST /api/compras/{id}/contabilizar'
      ]"
      :pendientes="[
        'Endpoints de proveedores y compras en FastAPI',
        'Formulario con cuenta de activo 1.1.5/1.2.3 por línea'
      ]"
    />
  </q-page>
</template>

<script setup>
import ModuloPlaceholder from '@/components/ModuloPlaceholder.vue'
</script>
