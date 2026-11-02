<script setup lang="ts">
import { computed } from 'vue'
import FolderTreeItem from './FolderTreeItem.vue'

interface Props {
  folders: any[]
  currentFolderId: number | null
  loading: boolean
  stats: any
}

interface Emits {
  navigate: [folderId: number | null]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const rootFolders = computed(() => props.folders)

function navigateToRoot() {
  emit('navigate', null)
}

function navigateToFolder(id: number) {
  emit('navigate', id)
}

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}
</script>

<template>
  <aside class="sidebar">
    <!-- Drive Header -->
    <div class="sidebar-header">
      <div class="drive-title">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <span>Local Drive</span>
      </div>
    </div>

    <!-- Storage Stats -->
    <div v-if="props.stats" class="storage-stats">
      <div class="storage-bar">
        <div
          class="storage-used"
          :style="{ width: props.stats.storage_total > 0 ? (props.stats.storage_used / props.stats.storage_total * 100) + '%' : '0%' }"
        ></div>
      </div>
      <div class="storage-info">
        <span>{{ formatBytes(props.stats.storage_used) }} used</span>
        <span>{{ formatBytes(props.stats.storage_total) }} total</span>
      </div>
    </div>

    <!-- Folder Tree -->
    <nav class="folder-tree" aria-label="Folders">
      <ul class="folder-list">
        <li class="folder-item root">
          <button
            class="folder-button"
            :class="{ active: props.currentFolderId === null }"
            @click="navigateToRoot"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
            <span>My Drive</span>
          </button>
        </li>

        <li v-for="folder in rootFolders" :key="folder.id">
          <FolderTreeItem
            :folder="folder"
            :current-folder-id="props.currentFolderId"
            @navigate="navigateToFolder"
          />
        </li>
      </ul>

      <div v-if="props.loading" class="tree-loading">
        <div class="spinner-small"></div>
      </div>
    </nav>

    <!-- Trash Link -->
    <div class="sidebar-footer">
      <button class="trash-link" @click="$router.push('/trash')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
        <span>Trash</span>
        <span class="trash-count" v-if="props.stats && props.stats.trashed_files > 0">
          {{ props.stats.trashed_files }}
        </span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  height: 100%;
  border-right: 1px solid var(--border);
  background: var(--bg);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}

.drive-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-h);
}

.storage-stats {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}

.storage-bar {
  height: 6px;
  background: var(--code-bg);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.storage-used {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.storage-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text);
}

.folder-tree {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.folder-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.folder-item.root {
  padding: 0 12px;
}

.folder-button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.folder-button:hover {
  background: var(--accent-bg);
  color: var(--text-h);
}

.folder-button.active {
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 500;
}

.folder-button svg {
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
}

.trash-link {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: var(--text);
  font-size: 14px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.trash-link:hover {
  background: var(--accent-bg);
  color: var(--text-h);
}

.trash-count {
  margin-left: auto;
  padding: 2px 6px;
  background: var(--accent-bg);
  color: var(--accent);
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.tree-loading {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>