<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="opti-header">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title class="opti-title">
          OptimaTech
          <span class="opti-subtitle">Sistema Contable</span>
        </q-toolbar-title>

        <q-badge color="green-3" text-color="dark" class="q-mr-sm">
          {{ apiStatus }}
        </q-badge>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="opti-drawer"
    >
      <q-list>
        <q-item clickable to="/" exact class="opti-home">
          <q-item-section avatar>
            <q-icon name="home" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Inicio</q-item-label>
            <q-item-label caption>Dashboard</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator spaced />

        <template v-for="section in menuSections" :key="section.title">
          <q-item-label header class="opti-menu-section">
            {{ section.title }}
          </q-item-label>

          <q-item
            v-for="item in section.items"
            :key="item.to"
            clickable
            :to="item.to"
            exact
            active-class="menu-active"
          >
            <q-item-section avatar>
              <q-icon :name="item.icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ item.label }}</q-item-label>
              <q-item-label caption>{{ item.caption }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MENU_SECTIONS } from '@/constants/menu.js'
import { API_BASE_URL } from '@/services/api.js'

const menuSections = MENU_SECTIONS
const leftDrawerOpen = ref(false)
const apiStatus = ref('API: verificando…')

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/health`)
    apiStatus.value = res.ok ? 'API: en línea' : 'API: sin respuesta'
  } catch {
    apiStatus.value = 'API: sin conexión'
  }
})
</script>
