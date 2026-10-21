<template>
  <router-view />
</template>

<script setup>
import { useQuasar } from 'quasar'

const $q = useQuasar()

// Mantiene la preferencia visual al navegar o recargar la aplicación.
$q.dark.set(localStorage.getItem('opti-theme') === 'dark')

// Retira tokens antiguos que se guardaban de forma persistente.
localStorage.removeItem('token')
localStorage.removeItem('usuario')
</script>
