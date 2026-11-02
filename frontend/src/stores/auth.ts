import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/files'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('drive_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(password: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.login(password)
      token.value = response.data.token
      localStorage.setItem('drive_token', token.value!)
      return { success: true }
    } catch (err: any) {
      error.value = err.response?.data?.password?.[0] || err.response?.data?.message || 'Login failed'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    token.value = null
    localStorage.removeItem('drive_token')
  }

  async function checkStatus() {
    if (!token.value) return false
    try {
      await authApi.status()
      return true
    } catch {
      logout()
      return false
    }
  }

  // Initialize on store creation
  if (token.value) {
    checkStatus()
  }

  return {
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    checkStatus,
  }
})