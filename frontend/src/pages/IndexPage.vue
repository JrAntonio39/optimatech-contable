<template>
  <q-page padding class="opti-dashboard">
    <div class="opti-hero q-pa-md q-mb-md">
      <div class="text-h5">OptimaTech Empresarial</div>
      <div class="text-subtitle1"
        >Sistema Contable — Catálogo, Diario, Mayor, Balanza y Resultados</div
      >
      <div class="q-mt-sm">
        <q-badge color="white" text-color="primary" class="q-mr-xs"
          >217 cuentas</q-badge
        >
        <q-badge color="white" text-color="primary" class="q-mr-xs"
          >PostgreSQL :5434</q-badge
        >
        <q-badge color="white" text-color="primary">FastAPI :8000</q-badge>
      </div>
    </div>

    <div v-for="section in menuSections" :key="section.title" class="q-mb-lg">
      <template v-if="itemsVisibles(section).length">
        <div class="text-h6 q-mb-sm">{{ section.title }}</div>
        <div class="row q-col-gutter-md">
          <div
            v-for="item in itemsVisibles(section)"
            :key="item.to"
            class="col-12 col-sm-6 col-md-4"
          >
            <q-card class="opti-card opti-modulo-btn">
              <q-card-section>
                <div class="row items-center no-wrap">
                  <q-avatar
                    color="primary"
                    text-color="white"
                    :icon="item.icon"
                  />
                  <div class="q-ml-md">
                    <div class="text-subtitle1">{{ item.label }}</div>
                    <div class="text-caption text-grey-7">{{
                      item.caption
                    }}</div>
                  </div>
                </div>
              </q-card-section>
              <q-card-actions align="right">
                <q-btn color="primary" :to="item.to" label="Abrir" no-caps />
              </q-card-actions>
            </q-card>
          </div>
        </div>
      </template>
    </div>
  </q-page>
</template>

<script setup>
import { MENU_SECTIONS } from '@/constants/menu.js'
import { useAuthStore } from '@/stores/auth.js'

const menuSections = MENU_SECTIONS
const auth = useAuthStore()

/** Solo muestra los módulos que el usuario tiene permitidos. */
function itemsVisibles(section) {
  return section.items.filter(item => {
    if (!item.permiso) return true
    return Array.isArray(item.permiso)
      ? item.permiso.some(permiso => auth.tienePermiso(permiso))
      : auth.tienePermiso(item.permiso)
  })
}
</script>
