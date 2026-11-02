<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import Toolbar from './Toolbar.vue'
import Breadcrumbs from './Breadcrumbs.vue'
import FileGrid from './FileGrid.vue'
import ContextMenu from './ContextMenu.vue'
import PreviewModal from './PreviewModal.vue'
import NewFolderDialog from './NewFolderDialog.vue'
import RenameDialog from './RenameDialog.vue'
import MoveDialog from './MoveDialog.vue'
import Toast from './Toast.vue'
import { useFilesStore } from '@/stores/files'
import { useUIStore } from '@/stores/ui'

const router = useRouter()
const route = useRoute()
const filesStore = useFilesStore()
const uiStore = useUIStore()

onMounted(() => {
  uiStore.init()
  filesStore.loadTree()
  filesStore.loadStats()

  // Load initial folder from route query
  const folderId = route.query.folder ? parseInt(route.query.folder as string) : null
  filesStore.loadFolder(folderId)
})

// Watch for folder changes in URL
watch(() => route.query.folder, (newVal) => {
  const folderId = newVal ? parseInt(newVal as string) : null
  if (folderId !== filesStore.currentFolderId) {
    filesStore.loadFolder(folderId)
  }
})

const navigateToFolder = (folderId: number | null) => {
  router.push({ path: '/drive', query: { folder: folderId || undefined } })
}

const handleOpen = (item: any) => {
  if (item.is_folder) {
    navigateToFolder(item.id)
  } else {
    uiStore.openPreview(item)
  }
}

const createFolder = async (name: string, parentId: number | null) => {
  try {
    await filesStore.createFolder(name, parentId)
    uiStore.showToast('Folder created', 'success')
  } catch (err) {
    // Error handled in store
  }
}

const handleRename = async (id: number, newName: string) => {
  try {
    await filesStore.renameItem(id, newName)
    uiStore.showToast('Renamed', 'success')
  } catch (err) {
    // Error handled in store
  }
}

const handleMove = async (id: number, newParentId: number | null) => {
  try {
    await filesStore.moveItem(id, newParentId)
    uiStore.showToast('Moved', 'success')
  } catch (err) {
    // Error handled in store
  }
}

const confirmDelete = async (item: any) => {
  if (confirm(`Move "${item.name}" to trash?`)) {
    try {
      await filesStore.deleteItem(item.id)
      uiStore.showToast('Moved to trash', 'success')
    } catch (err) {
      // Error handled in store
    }
  }
}
</script>

<template>
  <div class="drive-layout">
    <!-- Sidebar -->
    <Sidebar
      v-if="uiStore.sidebarOpen"
      :folders="filesStore.folderTree"
      :current-folder-id="filesStore.currentFolderId"
      :loading="filesStore.isLoadingTree"
      :stats="filesStore.stats"
      @navigate="filesStore.setCurrentFolder"
    />

    <!-- Main Content -->
    <main class="main-content" :class="{ 'sidebar-collapsed': !uiStore.sidebarOpen }">
      <!-- Top Bar -->
      <header class="top-bar">
        <button
          class="sidebar-toggle"
          @click="uiStore.toggleSidebar"
          aria-label="Toggle sidebar"
        >
          <svg v-if="uiStore.sidebarOpen" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </button>

        <div class="breadcrumb-container">
          <Breadcrumbs
            :current-folder-id="filesStore.currentFolderId"
            :folders="filesStore.folderTree"
            @navigate="navigateToFolder"
          />
        </div>

        <div class="top-bar-actions">
          <button
            class="btn-icon"
            @click="uiStore.openNewFolderDialog(filesStore.currentFolderId)"
            title="New folder"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
          </button>
          <button
            class="btn-icon"
            @click="uiStore.setViewMode(uiStore.viewMode === 'grid' ? 'list' : 'grid')"
            :title="uiStore.viewMode === 'grid' ? 'List view' : 'Grid view'"
          >
            <svg v-if="uiStore.viewMode === 'grid'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7" rx="1"/>
              <rect x="14" y="3" width="7" height="7" rx="1"/>
              <rect x="3" y="14" width="7" height="7" rx="1"/>
              <rect x="14" y="14" width="7" height="7" rx="1"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
        </div>
      </header>

      <!-- Toolbar -->
      <Toolbar
        :current-folder-id="filesStore.currentFolderId"
        :loading="filesStore.isLoading"
        @create-folder="uiStore.openNewFolderDialog"
        @search="filesStore.search"
      />

      <!-- File Grid/List -->
      <div class="file-area" :class="uiStore.viewMode">
        <FileGrid
          v-if="!filesStore.isLoading || filesStore.items.length > 0"
          :items="filesStore.items"
          :view-mode="uiStore.viewMode"
          :sort-by="uiStore.sortBy"
          :sort-asc="uiStore.sortAsc"
          @open="handleOpen"
          @context-menu="uiStore.showContextMenu"
          @download="filesStore.downloadFile"
          @rename="uiStore.openRenameDialog"
          @move="uiStore.openMoveDialog"
          @delete="confirmDelete"
        />

        <!-- Empty State -->
        <div v-else-if="!filesStore.isLoading && filesStore.items.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <p>This folder is empty</p>
          <button class="btn-primary" @click="uiStore.openNewFolderDialog(filesStore.currentFolderId)">
            Create Folder
          </button>
        </div>

        <!-- Loading State -->
        <div v-else class="loading-state">
          <div class="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    </main>

    <!-- Overlays -->
    <ContextMenu v-if="uiStore.contextMenu" :position="uiStore.contextMenu" :item="uiStore.contextMenu.item" @close="uiStore.hideContextMenu" />
    <PreviewModal v-if="uiStore.previewModalOpen" :item="uiStore.previewItem" @close="uiStore.closePreview" />
    <NewFolderDialog v-if="uiStore.newFolderDialogOpen" @close="uiStore.closeNewFolderDialog" @create="createFolder" />
    <RenameDialog v-if="uiStore.renameDialogOpen" :item="uiStore.renameItem" @close="uiStore.closeRenameDialog" @rename="handleRename" />
    <MoveDialog v-if="uiStore.moveDialogOpen" :item="uiStore.moveItem" :folders="filesStore.folderTree" @close="uiStore.closeMoveDialog" @move="handleMove" />
    <Toast v-if="uiStore.toast" :toast="uiStore.toast" />
  </div>
</template>

<style scoped>
.drive-layout {
  display: flex;
  height: 100vh;
  background: var(--bg);
  color: var(--text);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-left 0.3s ease;
}

.sidebar-collapsed {
  margin-left: 0;
}

.top-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  flex-shrink: 0;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--code-bg);
  border-radius: 8px;
  color: var(--text-h);
  cursor: pointer;
  transition: background 0.2s;
}

.sidebar-toggle:hover {
  background: var(--accent-bg);
}

.breadcrumb-container {
  flex: 1;
  min-width: 0;
}

.top-bar-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--code-bg);
  border-radius: 8px;
  color: var(--text-h);
  cursor: pointer;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: var(--accent-bg);
}

.file-area {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.file-area.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.file-area.list {
  display: block;
}

.empty-state, .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text);
  gap: 16px.
}

.empty-state svg, .loading-state svg {
  opacity: 0.5;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite.
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-primary {
  padding: 10px 20px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>