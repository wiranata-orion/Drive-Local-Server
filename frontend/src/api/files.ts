import api from './axios'
import type { DriveNode, FolderTreeNode, SearchResult, Stats, PaginatedResponse } from '@/types'

// Type definitions
export interface FileListParams {
  parent_id?: number | null
  search?: string
  page?: number
  page_size?: number
  ordering?: string
}

export interface FileUploadData {
  file: File
  parent_id?: number | null
  name?: string
}

export interface FolderCreateData {
  name: string
  parent_id?: number | null
}

export interface NodeUpdateData {
  name?: string
  parent_id?: number | null
}

// Auth API
export const authApi = {
  login(password: string) {
    return api.post<{ success: boolean; message: string; token: string }>('/auth/login/', { password })
  },

  status() {
    return api.get<{ authenticated: boolean; message: string }>('/auth/status/')
  },
}

// Files/Folders API
export const filesApi = {
  // List files/folders
  list(params: FileListParams = {}) {
    return api.get<PaginatedResponse<DriveNode>>('/files/', { params })
  },

  // Get single file/folder
  get(id: number) {
    return api.get<DriveNode>(`/files/${id}/`)
  },

  // Create folder
  createFolder(data: FolderCreateData) {
    return api.post<DriveNode>('/files/', { ...data, is_folder: true })
  },

  // Upload file
  upload(data: FileUploadData, onProgress?: (progress: number) => void) {
    const formData = new FormData()
    formData.append('file', data.file)
    if (data.parent_id) formData.append('parent_id', data.parent_id.toString())
    if (data.name) formData.append('name', data.name)

    return api.post<DriveNode>('/files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress ? (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1))
        onProgress(progress)
      } : undefined,
    })
  },

  // Update (rename/move)
  update(id: number, data: NodeUpdateData) {
    return api.patch<DriveNode>(`/files/${id}/`, data)
  },

  // Delete (move to trash)
  delete(id: number) {
    return api.delete(`/files/${id}/`)
  },

  // Download file
  download(id: number) {
    return api.get(`/files/${id}/download/`, { responseType: 'blob' })
  },

  // Preview file
  preview(id: number) {
    return api.get(`/files/${id}/preview/`, { responseType: 'blob' })
  },

  // Get folder tree
  getTree() {
    return api.get<FolderTreeNode[]>('/files/tree/')
  },

  // Search
  search(query: string) {
    return api.get<SearchResult[]>(`/files/search/`, { params: { q: query } })
  },

  // Get stats
  getStats() {
    return api.get<Stats>('/files/stats/')
  },
}

// Trash API
export const trashApi = {
  list() {
    return api.get<DriveNode[]>('/trash/')
  },

  restore(id: number) {
    return api.post<DriveNode>(`/trash/${id}/restore/`)
  },

  permanentDelete(id: number) {
    return api.delete(`/trash/${id}/`)
  },

  empty() {
    return api.post('/trash/empty/')
  },
}