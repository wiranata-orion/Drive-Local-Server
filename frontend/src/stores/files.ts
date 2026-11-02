import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { filesApi, trashApi } from '@/api/files'
import type { DriveNode, FolderTreeNode, SearchResult, Stats, PaginatedResponse } from '@/types'

export const useFilesStore = defineStore('files', () => {
  // State
  const items = ref<DriveNode[]>([])
  const currentFolderId = ref<number | null>(null)
  const folderTree = ref<FolderTreeNode[]>([])
  const searchResults = ref<SearchResult[]>([])
  const trashItems = ref<DriveNode[]>([])
  const stats = ref<Stats | null>(null)

  const isLoading = ref(false)
  const isLoadingTree = ref(false)
  const isLoadingStats = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const currentPage = ref(1)
  const totalPages = ref(1)
  const totalCount = ref(0)

  // Computed
  const folders = computed(() => items.value.filter(item => item.is_folder))
  const files = computed(() => items.value.filter(item => !item.is_folder))
  const breadcrumbs = computed(() => {
    // This would need the full path - for now return empty
    return []
  })

  // Actions
  async function loadFolder(folderId: number | null = null, page = 1) {
    isLoading.value = true
    error.value = null
    try {
      const params: any = { page, page_size: 50 }
      if (folderId !== null) {
        params.parent_id = folderId
      }
      const response = await filesApi.list(params)
      items.value = response.data.results
      currentFolderId.value = folderId
      currentPage.value = response.data.page || 1
      totalCount.value = response.data.count
      totalPages.value = Math.ceil(totalCount.value / 50)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load folder'
      items.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function loadTree() {
    isLoadingTree.value = true
    try {
      const response = await filesApi.getTree()
      folderTree.value = response.data
    } catch (err: any) {
      console.error('Failed to load folder tree:', err)
    } finally {
      isLoadingTree.value = false
    }
  }

  async function loadStats() {
    isLoadingStats.value = true
    try {
      const response = await filesApi.getStats()
      stats.value = response.data
    } catch (err: any) {
      console.error('Failed to load stats:', err)
    } finally {
      isLoadingStats.value = false
    }
  }

  async function createFolder(name: string, parentId: number | null = null) {
    try {
      const response = await filesApi.createFolder({ name, parent_id: parentId })
      // Add to current list if in same folder
      if (parentId === currentFolderId.value || (parentId === null && currentFolderId.value === null)) {
        items.value.unshift(response.data)
        items.value.sort((a, b) => {
          if (a.is_folder !== b.is_folder) return a.is_folder ? -1 : 1
          return a.name.localeCompare(b.name)
        })
      }
      // Refresh tree
      await loadTree()
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.name?.[0] || 'Failed to create folder'
      throw err
    }
  }

  async function uploadFile(file: File, parentId: number | null = null, onProgress?: (progress: number) => void) {
    try {
      const response = await filesApi.upload({ file, parent_id: parentId }, onProgress)
      // Add to current list if in same folder
      if (parentId === currentFolderId.value || (parentId === null && currentFolderId.value === null)) {
        items.value.unshift(response.data)
        items.value.sort((a, b) => {
          if (a.is_folder !== b.is_folder) return a.is_folder ? -1 : 1
          return a.name.localeCompare(b.name)
        })
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.file?.[0] || 'Failed to upload file'
      throw err
    }
  }

  async function renameItem(id: number, newName: string) {
    try {
      const response = await filesApi.update(id, { name: newName })
      const index = items.value.findIndex(item => item.id === id)
      if (index !== -1) {
        items.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.name?.[0] || 'Failed to rename'
      throw err
    }
  }

  async function moveItem(id: number, newParentId: number | null) {
    try {
      const response = await filesApi.update(id, { parent_id: newParentId })
      // Remove from current list if moved out
      const index = items.value.findIndex(item => item.id === id)
      if (index !== -1) {
        items.value.splice(index, 1)
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.parent_id?.[0] || 'Failed to move'
      throw err
    }
  }

  async function deleteItem(id: number) {
    try {
      await filesApi.delete(id)
      const index = items.value.findIndex(item => item.id === id)
      if (index !== -1) {
        items.value.splice(index, 1)
      }
      await loadTrash() // Refresh trash
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete'
      throw err
    }
  }

  async function downloadFile(id: number, name: string) {
    try {
      const response = await filesApi.download(id)
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      error.value = 'Failed to download file'
      throw err
    }
  }

  async function search(query: string) {
    if (!query.trim()) {
      searchResults.value = []
      return
    }
    try {
      const response = await filesApi.search(query)
      searchResults.value = response.data
    } catch (err: any) {
      searchResults.value = []
      console.error('Search failed:', err)
    }
  }

  async function loadTrash() {
    try {
      const response = await trashApi.list()
      trashItems.value = response.data
    } catch (err: any) {
      console.error('Failed to load trash:', err)
    }
  }

  async function restoreFromTrash(id: number) {
    try {
      const response = await trashApi.restore(id)
      // Remove from trash list
      const index = trashItems.value.findIndex(item => item.id === id)
      if (index !== -1) {
        trashItems.value.splice(index, 1)
      }
      // Reload current folder to show restored item
      await loadFolder(currentFolderId.value)
      return response.data
    } catch (err: any) {
      error.value = 'Failed to restore'
      throw err
    }
  }

  async function permanentDelete(id: number) {
    try {
      await trashApi.permanentDelete(id)
      const index = trashItems.value.findIndex(item => item.id === id)
      if (index !== -1) {
        trashItems.value.splice(index, 1)
      }
    } catch (err: any) {
      error.value = 'Failed to permanently delete'
      throw err
    }
  }

  async function emptyTrash() {
    try {
      await trashApi.empty()
      trashItems.value = []
    } catch (err: any) {
      error.value = 'Failed to empty trash'
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  function setCurrentFolder(folderId: number | null) {
    currentFolderId.value = folderId
    loadFolder(folderId)
  }

  return {
    // State
    items,
    currentFolderId,
    folderTree,
    searchResults,
    trashItems,
    stats,
    isLoading,
    isLoadingTree,
    isLoadingStats,
    error,
    currentPage,
    totalPages,
    totalCount,

    // Computed
    folders,
    files,
    breadcrumbs,

    // Actions
    loadFolder,
    loadTree,
    loadStats,
    createFolder,
    uploadFile,
    renameItem,
    moveItem,
    deleteItem,
    downloadFile,
    search,
    loadTrash,
    restoreFromTrash,
    permanentDelete,
    emptyTrash,
    clearError,
    setCurrentFolder,
  }
})