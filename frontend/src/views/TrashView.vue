<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore, useFilesStore, useUIStore } from '@/stores'
import { useRouter } from 'vue-router'
import Layout from '@/components/Layout.vue'

const authStore = useAuthStore()
const filesStore = useFilesStore()
const uiStore = useUIStore()
const router = useRouter()

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    await authStore.checkStatus()
    if (!authStore.isAuthenticated) {
      router.push('/login')
      return
    }
  }
  await filesStore.loadTrash()
  uiStore.init()
})

const restoreItem = async (item: any) => {
  try {
    await filesStore.restoreFromTrash(item.id)
    uiStore.showToast('Restored', 'success')
  } catch (err) {
    uiStore.showToast('Failed to restore', 'error')
  }
}

const permanentDelete = async (item: any) => {
  if (confirm(`Permanently delete "${item.name}"? This cannot be undone.`)) {
    try {
      await filesStore.permanentDelete(item.id)
      uiStore.showToast('Permanently deleted', 'success')
    } catch (err) {
      uiStore.showToast('Failed to delete', 'error')
    }
  }
}

const emptyTrash = async () => {
  if (confirm('Empty trash permanently? This cannot be undone.')) {
    try {
      await filesStore.emptyTrash()
      uiStore.showToast('Trash emptied', 'success')
    } catch (err) {
      uiStore.showToast('Failed to empty trash', 'error')
    }
  }
}
</script>

<template>
  <Layout v-if="authStore.isAuthenticated">
    <template #default>
      <div class="trash-view">
        <header class="view-header">
          <h1>Trash</h1>
          <button v-if="filesStore.trashItems.length > 0" class="btn-danger" @click="emptyTrash">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
            Empty Trash
          </button>
        </header>

        <div v-if="filesStore.trashItems.length === 0" class="empty-trash">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <p>Trash is empty</p>
        </div>

        <div v-else class="trash-list">
          <table class="trash-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Original Location</th>
                <th>Size</th>
                <th>Deleted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filesStore.trashItems" :key="item.id">
                <td class="col-name">
                  <div class="file-name-cell">
                    <svg v-if="item.is_folder" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                    <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    </svg>
                    <span>{{ item.name }}</span>
                  </div>
                </td>
                <td class="col-path">{{ item.path || 'Unknown' }}</td>
                <td class="col-size">{{ item.size_formatted }}</td>
                <td class="col-date">{{ new Date(item.trashed_at).toLocaleString() }}</td>
                <td class="col-actions">
                  <div class="action-buttons">
                    <button class="action-btn" @click="restoreItem(item)" title="Restore">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M19 12H5"/><polyline points="12 5 19 12 12 19"/>
                      </svg>
                    </button>
                    <button class="action-btn danger" @click="permanentDelete(item)" title="Delete permanently">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                      </svg>
                    </button>
                  </div>
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
.trash-view {
  flex: 1;
  overflow: auto;
  padding: 24px;
}

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.view-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--text-h);
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  background: #ef4444;
  color: white;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-danger:hover {
  opacity: 0.9;
}

.empty-trash {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: var(--text);
  gap: 16px;
  text-align: center.
}

.trash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.trash-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 500;
  color: var(--text);
  border-bottom: 2px solid var(--border);
  background: var(--code-bg);
}

.trash-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.trash-table tr:hover td {
  background: var(--accent-bg);
}

.col-name { width: 30%; min-width: 200px; }
.col-path { width: 30%; }
.col-size { width: 15%; text-align: right; white-space: nowrap; }
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

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
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

.action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
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