<script setup lang="ts">
import { createPinia } from 'pinia'
import router from '@/router'
import { useAuthStore } from '@/stores'

const pinia = createPinia()
const authStore = useAuthStore()

// Initialize auth on app mount
authStore.checkStatus()
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
/* Global styles are in style.css */
</style>