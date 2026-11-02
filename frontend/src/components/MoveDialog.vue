<script setup lang="ts">
import { ref, computed } from 'vue'
import FolderTreeItem from './FolderTreeItem.vue'

interface Props {
  item: any
  folders: any[]
}

interface Emits {
  close: []
  move: [id: number, newParentId: number | null]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const selectedFolderId = ref<number | null>(null)
const expandedFolders = ref<Set<number>>(new Set())

function toggleExpand(folderId: number) {
  if (expandedFolders.value.has(folderId)) {
    expandedFolders.value.delete(folderId)
  } else {
    expandedFolders.value.add(folderId)
  }
}

function isExpanded(folderId: number) {
  return expandedFolders.value.has(folderId)
}

function isDescendant(folderId: number, targetId: number): boolean {
  if (folderId === targetId) return true
  const folder = findFolder(folderId, props.folders)
  if (!folder) return false
  if (folder.children) {
    return folder.children.some((child: any) => isDescendant(child.id, targetId))
  }
  return false
}

function findFolder(id: number, folders: any[]): any | null {
  for (const folder of folders) {
    if (folder.id === id) return folder
    if (folder.children) {
      const found = findFolder(id, folder.children)
      if (found) return found
    }
  }
  return null
}

const canMove = computed(() => {
  if (!selectedFolderId.value) return true // root
  return !isDescendant(selectedFolderId.value, props.item.id)
})

function handleSubmit() {
  if (canMove.value) {
    emit('move', props.item.id, selectedFolderId.value)
  }
}
</script>

<template>
  <div class="dialog-overlay" @click="emit('close')">
    <div class="dialog" @click.stop style="max-width: 500px; max-height: 70vh;">
      <header class="dialog-header">
        <h2>Move {{ props.item.is_folder ? 'Folder' : 'File' }}</h2>
        <button class="dialog-close" @click="emit('close')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </header>

      <div class="dialog-body" style="padding: 0; max-height: 50vh; overflow: auto;">
        <div class="move-target" :class="{ 'current-location': selectedFolderId.value === null }" @click="selectedFolderId = null">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <span>My Drive (Root)</span>
          <span v-if="selectedFolderId.value === null" class="selected-indicator">✓</span>
        </div>

        <div class="folder-tree" style="padding: 0 16px;">
          <FolderTreeItem
            v-for="folder in props.folders"
            :key="folder.id"
            :folder="folder"
            :current-folder-id="selectedFolderId.value"
            @navigate="selectedFolderId = $event"
          />
        </div>

        <div v-if="props.folders.length === 0" class="no-folders">
          No folders available
        </div>
      </div>

      <footer class="dialog-footer">
        <button class="btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn-primary" @click="handleSubmit" :disabled="!canMove">Move Here</button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.dialog {
  width: 100%;
  max-width: 500px;
  background: var(--bg);
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.dialog-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
}

.dialog-close {
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

.dialog-close:hover {
  background: var(--code-bg);
  color: var(--text-h);
}

.dialog-body {
  padding: 16px 20px;
  max-height: 50vh;
  overflow: auto;
}

.move-target {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 8px;
}

.move-target:hover {
  background: var(--accent-bg);
}

.move-target.current-location {
  background: var(--accent-bg);
  color: var(--accent);
}

.move-target svg {
  flex-shrink: 0;
  color: var(--accent);
}

.selected-indicator {
  margin-left: auto;
  color: var(--accent);
  font-weight: bold;
}

.folder-tree {
  margin-top: 8px;
}

.no-folders {
  padding: 20px;
  text-align: center;
  color: var(--text);
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
}

.btn-secondary {
  padding: 10px 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-h);
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.btn-secondary:hover {
  background: var(--code-bg);
  border-color: var(--accent-border);
}

.btn-primary {
  padding: 10px 20px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>