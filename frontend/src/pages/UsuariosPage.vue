<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Usuarios y roles</div>
      <q-space />
      <q-btn
        v-if="auth.tienePermiso('usuarios.crear')"
        color="primary"
        icon="person_add"
        label="Nuevo usuario"
        @click="abrirDialogo"
      />
    </div>

    <q-banner v-if="error" class="bg-red-1 text-red q-mb-md" rounded>
      {{ error }}
    </q-banner>
    <q-banner v-if="ok" class="bg-green-1 text-green-9 q-mb-md" rounded>
      {{ ok }}
    </q-banner>

    <q-tabs v-model="tab" dense align="left" class="text-primary q-mb-md">
      <q-tab name="usuarios" icon="group" label="Usuarios" />
      <q-tab name="roles" icon="badge" label="Roles y permisos" />
    </q-tabs>
    <q-separator class="q-mb-md" />

    <!-- ============ USUARIOS ============ -->
    <template v-if="tab === 'usuarios'">
      <q-table
        :rows="usuarios"
        :columns="columnasUsuarios"
        row-key="id"
        :loading="cargando"
        no-data-label="No hay usuarios"
      >
        <template #body="props">
          <q-tr :props="props">
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              <q-badge
                v-if="col.name === 'activo'"
                :color="props.row.activo ? 'positive' : 'negative'"
              >
                {{ props.row.activo ? 'Activo' : 'Inactivo' }}
              </q-badge>
              <q-chip
                v-else-if="col.name === 'rol_codigos'"
                v-for="rol in props.row.rol_codigos"
                :key="rol"
                dense
                color="blue-1"
                class="q-mr-xs"
              >
                {{ rol }}
              </q-chip>
              <span v-else>{{ col.value }}</span>
            </q-td>
            <q-td auto-width>
              <q-btn
                v-if="auth.tienePermiso('usuarios.editar')"
                dense
                flat
                icon="edit"
                label="Editar"
                @click="editarUsuario(props.row)"
              />
              <q-btn
                v-if="
                  auth.tienePermiso('usuarios.eliminar') && props.row.activo
                "
                dense
                flat
                color="negative"
                icon="person_off"
                label="Desactivar"
                @click="desactivarUsuario(props.row)"
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </template>

    <!-- ============ ROLES ============ -->
    <template v-else>
      <div class="text-caption text-grey-7 q-mb-md">
        Los permisos de cada rol se ajustan en la base de datos (script
        <code>seed_permisos.py</code>), no en el código.
      </div>
      <q-table
        :rows="roles"
        :columns="columnasRoles"
        row-key="id"
        :loading="cargando"
        no-data-label="No hay roles"
      >
        <template #body="props">
          <q-tr :props="props">
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              <span v-if="col.name === 'permiso_codigos'">
                <q-chip
                  v-for="p in props.row.permiso_codigos"
                  :key="p"
                  dense
                  outline
                  color="grey-7"
                  class="q-mr-xs q-mb-xs"
                >
                  {{ p }}
                </q-chip>
              </span>
              <span v-else>{{ col.value }}</span>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </template>

    <!-- ============ DIÁLOGO USUARIO ============ -->
    <q-dialog v-model="dialogo">
      <q-card style="min-width: 460px">
        <q-card-section>
          <div class="text-h6">
            {{ editando ? 'Editar usuario' : 'Nuevo usuario' }}
          </div>
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-input
            v-model="form.username"
            label="Usuario"
            outlined
            dense
            :disable="editando"
          />
          <q-input
            v-model="form.nombre_completo"
            label="Nombre completo"
            outlined
            dense
          />
          <q-input
            v-model="form.email"
            label="Correo electrónico"
            type="email"
            outlined
            dense
          />
          <q-input
            v-if="!editando"
            v-model="form.password"
            label="Contraseña"
            type="password"
            outlined
            dense
            hint="Mínimo 8 caracteres"
          />
          <q-select
            v-model="form.rol_codigos"
            :options="opcionesRol"
            option-value="value"
            option-label="label"
            label="Rol(es)"
            outlined
            dense
            multiple
            use-chips
          />
          <q-toggle
            v-if="editando"
            v-model="form.activo"
            label="Usuario activo"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />
          <q-btn
            color="primary"
            :label="editando ? 'Guardar cambios' : 'Crear usuario'"
            :loading="guardando"
            @click="guardar"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api.js'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()

const tab = ref('usuarios')
const usuarios = ref([])
const roles = ref([])
const cargando = ref(false)
const guardando = ref(false)
const error = ref('')
const ok = ref('')
const dialogo = ref(false)
const editando = ref(false)

const form = ref({
  id: null,
  username: '',
  nombre_completo: '',
  email: '',
  password: '',
  rol_codigos: [],
  activo: true
})

const opcionesRol = computed(() =>
  roles.value.map(r => ({ label: r.nombre, value: r.codigo }))
)

const columnasUsuarios = [
  { name: 'username', label: 'Usuario', field: 'username', align: 'left' },
  {
    name: 'nombre_completo',
    label: 'Nombre',
    field: 'nombre_completo',
    align: 'left'
  },
  { name: 'email', label: 'Correo', field: 'email', align: 'left' },
  { name: 'rol_codigos', label: 'Roles', field: 'rol_codigos', align: 'left' },
  { name: 'activo', label: 'Estado', field: 'activo', align: 'center' },
  {
    name: 'ultimo_acceso',
    label: 'Último acceso',
    field: 'ultimo_acceso',
    align: 'left',
    format: v => (v ? new Date(v).toLocaleString('es-SV') : 'Nunca')
  }
]

const columnasRoles = [
  { name: 'codigo', label: 'Código', field: 'codigo', align: 'left' },
  { name: 'nombre', label: 'Rol', field: 'nombre', align: 'left' },
  {
    name: 'descripcion',
    label: 'Descripción',
    field: 'descripcion',
    align: 'left'
  },
  {
    name: 'permiso_codigos',
    label: 'Permisos',
    field: 'permiso_codigos',
    align: 'left'
  }
]

async function cargar() {
  cargando.value = true
  try {
    const [u, r] = await Promise.all([
      api.get('/api/auth/usuarios'),
      api.get('/api/auth/roles')
    ])
    usuarios.value = u
    roles.value = r
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}

function abrirDialogo() {
  editando.value = false
  form.value = {
    id: null,
    username: '',
    nombre_completo: '',
    email: '',
    password: '',
    rol_codigos: [],
    activo: true
  }
  error.value = ''
  dialogo.value = true
}

function editarUsuario(u) {
  editando.value = true
  form.value = {
    id: u.id,
    username: u.username,
    nombre_completo: u.nombre_completo,
    email: u.email,
    password: '',
    rol_codigos: [...u.rol_codigos],
    activo: u.activo
  }
  error.value = ''
  dialogo.value = true
}

async function guardar() {
  guardando.value = true
  ok.value = ''
  error.value = ''
  try {
    if (editando.value) {
      const payload = {
        nombre_completo: form.value.nombre_completo,
        email: form.value.email,
        activo: form.value.activo,
        rol_codigos: form.value.rol_codigos
      }
      await api.put(`/api/auth/usuarios/${form.value.id}`, payload)
      ok.value = `Usuario ${form.value.username} actualizado.`
    } else {
      await api.post('/api/auth/register', {
        username: form.value.username,
        nombre_completo: form.value.nombre_completo,
        email: form.value.email,
        password: form.value.password,
        rol_codigos: form.value.rol_codigos
      })
      ok.value = `Usuario ${form.value.username} creado.`
    }
    dialogo.value = false
    await cargar()
  } catch (e) {
    error.value = e.message
  } finally {
    guardando.value = false
  }
}

async function desactivarUsuario(u) {
  ok.value = ''
  error.value = ''
  try {
    await api.del(`/api/auth/usuarios/${u.id}`)
    ok.value = `Usuario ${u.username} desactivado.`
    await cargar()
  } catch (e) {
    error.value = e.message
  }
}

onMounted(cargar)
</script>
