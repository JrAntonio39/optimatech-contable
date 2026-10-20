<template>
  <q-page class="flex flex-center q-pa-md">
    <q-card class="q-mt-xl" style="width: 100%; max-width: 400px">
      <q-card-section class="text-center">
        <q-icon name="business" color="primary" size="64px" class="q-mb-md" />
        <div class="text-h5">OptimaTech</div>
        <div class="text-caption text-grey-7 q-mt-sm">Sistema Contable</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="login" class="q-gutter-md">
          <q-input
            v-model="form.username"
            label="Usuario"
            type="text"
            outlined
            dense
            :rules="[val => !!val || 'Requerido']"
            autofocus
            @keyup.enter="login"
          >
            <template #append>
              <q-icon name="person" />
            </template>
          </q-input>

          <q-input
            v-model="form.password"
            label="Contraseña"
            type="password"
            outlined
            dense
            :rules="[val => !!val || 'Requerido']"
            @keyup.enter="login"
          >
            <template #append>
              <q-icon name="lock" />
            </template>
          </q-input>

          <q-btn
            type="submit"
            label="Iniciar sesión"
            color="primary"
            class="q-mt-md"
            :loading="cargando"
            :disable="cargando"
          />
        </q-form>

        <q-banner v-if="error" class="bg-red-1 text-red q-mt-md" rounded dense>
          {{ error }}
        </q-banner>
      </q-card-section>

      <q-card-section class="text-center text-caption text-grey-7">
        Usuario demo: <strong>admin</strong> / <strong>admin123</strong>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ username: '', password: '' })
const cargando = ref(false)
const error = ref('')

async function login() {
  error.value = ''
  const ok = await auth.login(form.value.username, form.value.password)
  if (ok) {
    router.push('/catalogo')
  } else {
    error.value = auth.error || 'Error al iniciar sesión'
  }
}
</script>
