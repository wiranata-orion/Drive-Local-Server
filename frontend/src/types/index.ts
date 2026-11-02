// Type definitions for Drive API

export interface DriveNode {
  id: number
  name: string
  parent: number | null
  parent_name: string | null
  is_folder: boolean
  file: string | null
  size: number
  size_formatted: string
  mime_type: string
  is_trashed: boolean
  trashed_at: string | null
  created_at: string
  updated_at: string
  download_url: string | null
  preview_url: string | null
  children_count: number
  path: string
}

export interface FolderTreeNode {
  id: number
  name: string
  children: FolderTreeNode[]
}

export interface SearchResult {
  id: number
  name: string
  is_folder: boolean
  size: number
  size_formatted: string
  mime_type: string
  path: string
  created_at: string
  updated_at: string
}

export interface Stats {
  total_files: number
  total_folders: number
  total_size: number
  total_size_formatted: string
  trashed_files: number
  trashed_size: number
  trashed_size_formatted: string
  storage_used: number
  storage_used_formatted: string
  storage_total: number
  storage_total_formatted: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface UploadProgress {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
  response?: DriveNode
}