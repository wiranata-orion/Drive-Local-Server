<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/drive')
}
</script>

<template>
  <div class="not-found">
    <svg width="96" height="96" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
    <h1>404</h1>
    <p>Page not found</p>
    <button class="btn-primary" @click="goHome">Go to Drive</button>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  text-align: center;
  padding: 24px;
  gap: 16px;
}

.not-found svg {
  opacity: 0.3;
}

.not-found h1 {
  margin: 0;
  font-size: 72px;
  font-weight: 700;
  color: var(--text-h);
}

.not-found p {
  margin: 0;
  font-size: 18px;
  color: var(--text);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>