<script setup lang="ts">
import Layout from '@/components/Layout.vue'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.checkStatus()
    if (!authStore.isAuthenticated) {
      router.push('/login')
    }
  }
})
</script>

<template>
  <Layout v-if="authStore.isAuthenticated" />
  <div v-else class="loading-screen">
    <div class="spinner"></div>
  </div>
</template>

<style scoped>
.loading-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: var(--bg);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>