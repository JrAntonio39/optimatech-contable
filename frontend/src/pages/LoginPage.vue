<template>
  <div class="flex flex-center q-pa-md" style="min-height: 100vh">
    <q-card class="q-mt-xl" style="width: 100%; max-width: 440px">
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
            :type="mostrarPassword ? 'text' : 'password'"
            outlined
            dense
            :rules="[val => !!val || 'Requerido']"
            @keyup.enter="login"
          >
            <template #append>
              <q-btn
                flat
                dense
                round
                type="button"
                :icon="mostrarPassword ? 'visibility_off' : 'visibility'"
                :aria-label="
                  mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'
                "
                @click="mostrarPassword = !mostrarPassword"
              >
                <q-tooltip>{{
                  mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'
                }}</q-tooltip>
              </q-btn>
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

      <q-card-section class="q-pt-none">
        <div class="text-subtitle2 q-mb-xs">Cuentas demo por rol</div>
        <div class="text-caption text-grey-7 q-mb-sm">
          Selecciona una cuenta para llenar el formulario.
        </div>
        <q-list bordered separator class="opti-demo-list">
          <q-item
            v-for="cuenta in cuentasDemo"
            :key="cuenta.usuario"
            clickable
            v-ripple
            @click="usarCuenta(cuenta)"
          >
            <q-item-section avatar>
              <q-icon :name="cuenta.icono" color="primary" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ cuenta.rol }}</q-item-label>
              <q-item-label caption>
                {{ cuenta.usuario }} / {{ cuenta.clave }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-icon name="login" color="grey-6" />
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ username: '', password: '' })
const mostrarPassword = ref(false)
const cargando = ref(false)
const error = ref('')
const cuentasDemo = [
  {
    rol: 'Administrador',
    usuario: 'admin',
    clave: 'admin123',
    icono: 'admin_panel_settings'
  },
  {
    rol: 'Contador',
    usuario: 'contador',
    clave: 'Demo1234',
    icono: 'calculate'
  },
  {
    rol: 'Auxiliar contable',
    usuario: 'auxiliar',
    clave: 'Demo1234',
    icono: 'edit_note'
  },
  {
    rol: 'Ventas',
    usuario: 'ventas',
    clave: 'Demo1234',
    icono: 'point_of_sale'
  },
  {
    rol: 'Compras',
    usuario: 'compras',
    clave: 'Demo1234',
    icono: 'shopping_cart'
  },
  {
    rol: 'Planilla',
    usuario: 'planilla',
    clave: 'Demo1234',
    icono: 'payments'
  },
  {
    rol: 'Auditor',
    usuario: 'auditor',
    clave: 'Demo1234',
    icono: 'fact_check'
  }
]

function usarCuenta(cuenta) {
  form.value.username = cuenta.usuario
  form.value.password = cuenta.clave
  error.value = ''
}

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
