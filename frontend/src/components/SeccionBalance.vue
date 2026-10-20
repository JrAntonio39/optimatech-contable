<template>
  <q-card flat bordered>
    <q-card-section class="row items-center">
      <div class="text-subtitle1">{{ titulo }}</div>
      <q-space />
      <q-chip :color="color" text-color="white">Total: {{ fmt(total) }}</q-chip>
    </q-card-section>
    <q-card-section v-for="r in rubros" :key="r.codigo" class="q-pt-none">
      <div class="row items-center q-mb-xs">
        <div class="text-subtitle2">{{ r.codigo }} · {{ r.nombre }}</div>
        <q-space />
        <span class="text-weight-medium">{{ fmt(r.saldo) }}</span>
      </div>
      <q-list dense bordered separator class="q-mb-sm">
        <q-item v-for="l in r.lineas" :key="l.codigo">
          <q-item-section>{{ l.codigo }} · {{ l.nombre }}</q-item-section>
          <q-item-section side>{{ fmt(l.saldo) }}</q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
  </q-card>
</template>

<script setup>
defineProps({
  titulo: { type: String, required: true },
  rubros: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  color: { type: String, default: 'primary' }
})

function fmt(v) {
  return Number(v || 0).toFixed(2)
}
</script>
