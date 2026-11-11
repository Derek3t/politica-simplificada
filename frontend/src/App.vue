<script setup>
import { useRoute } from 'vue-router'
import SidebarMenu from './components/SidebarMenu.vue'

const route = useRoute()
</script>

<template>
  <RouterView v-if="route.meta.semMenu" />
  <div v-else class="flex min-h-screen flex-col md:flex-row">
    <SidebarMenu />
    <main class="flex-1 px-4 pb-24 pt-6 md:px-8 md:pb-8">
      <RouterView />
    </main>
  </div>
</template>
