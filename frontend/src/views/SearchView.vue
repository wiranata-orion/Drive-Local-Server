<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useAuthStore, useFilesStore, useUIStore } from '@/stores'
import { useRouter, useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'

const authStore = useAuthStore()
const filesStore = useFilesStore()
const uiStore = useUIStore()
const router = useRouter()
const route = useRoute()

const searchQuery = ref(route.query.q as string || '')

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.checkStatus()
    if (!authStore.isAuthenticated) {
      router.push('/login')
      return
    }
  }
  uiStore.init()

  if (searchQuery.value) {
    filesStore.search(searchQuery.value)
  }
})

watch(searchQuery, (newQuery) => {
  router.replace({ query: { q: newQuery || undefined } })
  filesStore.search(newQuery)
}, { immediate: true })

const highlightMatch = (text: string, query: string) => {
  if (!query) return text
  const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'))
  return parts.map((part, i) =>
    part.toLowerCase() === query.toLowerCase()
      ? `<mark key="${i}">${part}</mark>`
      : part
  ).join('')
}

const openItem = (item: any) => {
  if (item.is_folder) {
    router.push({ path: '/drive', query: { folder: item.parent || undefined } })
  } else {
    uiStore.openPreview(item)
  }
}

const downloadItem = (item: any) => {
  filesStore.downloadFile(item.id, item.name)
}
</script>

<template>
  <Layout v-if="authStore.isAuthenticated">
    <template #default>
      <div class="search-view">
        <header class="view-header">
          <h1>Search Results</h1>
        </header>

        <div class="search-info" v-if="searchQuery">
          <p>Results for "<strong>{{ searchQuery }}</strong>" — {{ filesStore.searchResults.length }} found</p>
        </div>

        <div v-if="!searchQuery" class="search-empty">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <p>Enter a search query to find files</p>
        </div>

        <div v-else-if="filesStore.searchResults.length === 0" class="search-empty">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            <line x1="12" y1="8" x2="12" y2="16"/>
            <line x1="8" y1="12" x2="16" y2="12"/>
          </svg>
          <p>No results found for "{{ searchQuery }}"</p>
        </div>

        <div v-else class="search-results">
          <table class="search-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Size</th>
                <th>Location</th>
                <th>Modified</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filesStore.searchResults" :key="item.id" @click="openItem(item)">
                <td class="col-name">
                  <div class="file-name-cell">
                    <svg v-if="item.is_folder" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                    <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    </svg>
                    <span class="highlighted-name" v-html="highlightMatch(item.name, searchQuery)"></span>
                  </div>
                </td>
                <td class="col-type">
                  <span v-if="item.is_folder">Folder</span>
                  <span v-else>{{ item.mime_type || 'File' }}</span>
                </td>
                <td class="col-size">{{ item.size_formatted }}</td>
                <td class="col-path" v-html="highlightMatch(item.path, searchQuery)"></td>
                <td class="col-date">{{ new Date(item.updated_at).toLocaleString() }}</td>
                <td class="col-actions">
                  <button v-if="!item.is_folder" class="action-btn" @click.stop="downloadItem(item)" title="Download">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </Layout>

  <div v-else class="loading-screen">
    <div class="spinner"></div>
  </div>
</template>

<style scoped>
.search-view {
  flex: 1;
  overflow: auto;
  padding: 24px;
}

.view-header {
  margin-bottom: 24px;
}

.view-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--text-h);
}

.search-info {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--code-bg);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text);
}

.search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: var(--text);
  gap: 16px;
  text-align: center;
}

.search-empty svg {
  opacity: 0.4;
}

.search-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.search-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 500;
  color: var(--text);
  border-bottom: 2px solid var(--border);
  background: var(--code-bg);
}

.search-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.search-table tr:hover td {
  background: var(--accent-bg);
  cursor: pointer;
}

.col-name { width: 25%; min-width: 200px; }
.col-type { width: 15%; }
.col-size { width: 10%; text-align: right; white-space: nowrap; }
.col-path { width: 25%; }
.col-date { width: 15%; white-space: nowrap; }
.col-actions { width: 10%; text-align: right; }

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-name-cell svg {
  flex-shrink: 0;
  color: var(--accent);
}

.highlighted-name mark {
  background: var(--accent-bg);
  color: var(--accent);
  padding: 0 2px;
  border-radius: 2px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: var(--text);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.action-btn:hover {
  background: var(--accent-bg);
  color: var(--accent);
}

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