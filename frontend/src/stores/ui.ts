import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // State
  const sidebarOpen = ref(true)
  const viewMode = ref<'grid' | 'list'>('grid')
  const sortBy = ref<'name' | 'size' | 'modified' | 'type'>('name')
  const sortAsc = ref(true)
  const previewModalOpen = ref(false)
  const previewItem = ref<any>(null)
  const contextMenu = ref<{ x: number; y: number; item: any } | null>(null)
  const newFolderDialogOpen = ref(false)
  const renameDialogOpen = ref(false)
  const renameItem = ref<any>(null)
  const moveDialogOpen = ref(false)
  const moveItem = ref<any>(null)
  const uploadQueue = ref<Array<{ file: File; progress: number; status: string }>>([])
  const toast = ref<{ message: string; type: 'success' | 'error' | 'info' } | null>(null)

  // Computed
  const sortedItems = computed(() => {
    // This would be used with files store items
    return []
  })

  // Actions
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function setSidebarOpen(open: boolean) {
    sidebarOpen.value = open
  }

  function setViewMode(mode: 'grid' | 'list') {
    viewMode.value = mode
    localStorage.setItem('drive_view_mode', mode)
  }

  function setSortBy(field: 'name' | 'size' | 'modified' | 'type') {
    if (sortBy.value === field) {
      sortAsc.value = !sortAsc.value
    } else {
      sortBy.value = field
      sortAsc.value = true
    }
  }

  function openPreview(item: any) {
    previewItem.value = item
    previewModalOpen.value = true
  }

  function closePreview() {
    previewModalOpen.value = false
    previewItem.value = null
  }

  function showContextMenu(event: MouseEvent, item: any) {
    event.preventDefault()
    contextMenu.value = { x: event.clientX, y: event.clientY, item }
  }

  function hideContextMenu() {
    contextMenu.value = null
  }

  function openNewFolderDialog(parentId?: number) {
    newFolderDialogOpen.value = true
  }

  function closeNewFolderDialog() {
    newFolderDialogOpen.value = false
  }

  function openRenameDialog(item: any) {
    renameItem.value = item
    renameDialogOpen.value = true
  }

  function closeRenameDialog() {
    renameDialogOpen.value = false
    renameItem.value = null
  }

  function openMoveDialog(item: any) {
    moveItem.value = item
    moveDialogOpen.value = true
  }

  function closeMoveDialog() {
    moveDialogOpen.value = false
    moveItem.value = null
  }

  function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    toast.value = { message, type }
    setTimeout(() => {
      toast.value = null
    }, 3000)
  }

  // Initialize from localStorage
  function init() {
    const savedViewMode = localStorage.getItem('drive_view_mode') as 'grid' | 'list' | null
    if (savedViewMode) viewMode.value = savedViewMode

    const savedSidebar = localStorage.getItem('drive_sidebar_open')
    if (savedSidebar !== null) sidebarOpen.value = savedSidebar === 'true'
  }

  return {
    // State
    sidebarOpen,
    viewMode,
    sortBy,
    sortAsc,
    previewModalOpen,
    previewItem,
    contextMenu,
    newFolderDialogOpen,
    renameDialogOpen,
    renameItem,
    moveDialogOpen,
    moveItem,
    uploadQueue,
    toast,

    // Computed
    sortedItems,

    // Actions
    toggleSidebar,
    setSidebarOpen,
    setViewMode,
    setSortBy,
    openPreview,
    closePreview,
    showContextMenu,
    hideContextMenu,
    openNewFolderDialog,
    closeNewFolderDialog,
    openRenameDialog,
    closeRenameDialog,
    openMoveDialog,
    closeMoveDialog,
    showToast,
    init,
  }
})