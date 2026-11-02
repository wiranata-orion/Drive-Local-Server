<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  item: any
  listView?: boolean
}

interface Emits {
  open: [item: any]
  contextMenu: [event: MouseEvent, item: any]
  download: [item: any]
  rename: [item: any]
  move: [item: any]
  delete: [item: any]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isImage = computed(() => props.item.mime_type?.startsWith('image/'))
const isPdf = computed(() => props.item.mime_type === 'application/pdf')
const isText = computed(() => props.item.mime_type?.startsWith('text/'))
const isVideo = computed(() => props.item.mime_type?.startsWith('video/'))
const isAudio = computed(() => props.item.mime_type?.startsWith('audio/'))

// Predefined icon data to avoid regex on every render
const ICONS = {
  folder: { path: 'M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z', points: '', hasPolyline: false },
  image: { path: 'M3 3h18v18H3z', points: '21 15 16 10 5 21', hasPolyline: true },
  pdf: { path: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z', points: '14 2 14 8 20 8', hasPolyline: true },
  video: { path: 'M1 5h15v14H1z', points: '23 7 16 12 23 17', hasPolyline: true },
  audio: { path: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z', points: '10 15 15 10 15 15', hasPolyline: true },
  text: { path: 'M4 7v-3h16v13', points: '4 7 4 4 20 4 20 17', hasPolyline: true },
  file: { path: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z', points: '14 2 14 8 20 8', hasPolyline: true },
}

function getIconKey() {
  if (props.item.is_folder) return 'folder'
  if (isImage.value) return 'image'
  if (isPdf.value) return 'pdf'
  if (isVideo.value) return 'video'
  if (isAudio.value) return 'audio'
  if (isText.value) return 'text'
  return 'file'
}

const iconData = computed(() => ICONS[getIconKey() as keyof typeof ICONS] || ICONS.file)

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleClick(event: MouseEvent) {
  if (!props.listView || (event.target as HTMLElement).closest('td:last-child')) return
  emit('open', props.item)
}

function handleDblClick(event: MouseEvent) {
  if (props.listView && (event.target as HTMLElement).closest('td:last-child')) return
  emit('open', props.item)
}

function handleContextMenu(event: MouseEvent) {
  event.preventDefault()
  emit('contextMenu', event, props.item)
}

function handleDownload(event: MouseEvent) {
  event.stopPropagation()
  emit('download', props.item)
}

function handleRename(event: MouseEvent) {
  event.stopPropagation()
  emit('rename', props.item)
}

function handleMove(event: MouseEvent) {
  event.stopPropagation()
  emit('move', props.item)
}

function handleDelete(event: MouseEvent) {
  event.stopPropagation()
  emit('delete', props.item)
}
</script>

<template>
  <!-- Grid View Item -->
  <div
    v-if="!props.listView"
    class="file-item grid-item"
    @click="handleClick"
    @dblclick="handleDblClick"
    @contextmenu="handleContextMenu"
    @keydown.enter="handleClick"
    @keydown.space.prevent
    tabindex="0"
    role="gridcell"
  >
    <div class="file-thumbnail" :class="{ folder: props.item.is_folder }">
      <!-- Folder Icon -->
      <svg v-if="props.item.is_folder" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>

      <!-- Image Thumbnail -->
      <img
        v-else-if="isImage && props.item.preview_url"
        :src="props.item.preview_url"
        :alt="props.item.name"
        class="thumb-image"
        loading="lazy"
      />

      <!-- Other File Icons -->
      <svg v-else width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="file-icon">
        <path :d="iconData.path" />
        <polyline v-if="iconData.hasPolyline" :points="iconData.points" />
      </svg>

      <div class="file-type-badge" v-if="!props.item.is_folder">{{ props.item.mime_type || 'File' }}</div>
    </div>

    <div class="file-info">
      <p class="file-name" :title="props.item.name">{{ props.item.name }}</p>
      <p class="file-meta">
        <span v-if="!props.item.is_folder">{{ props.item.size_formatted }}</span>
        <span v-else>{{ props.item.children_count }} items</span>
        · {{ formatDate(props.item.updated_at) }}
      </p>
    </div>

    <div class="file-actions">
      <button class="action-btn" @click.stop="handleDownload" :title="'Download'" :disabled="props.item.is_folder">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      </button>
      <button class="action-btn" @click.stop="handleRename" :title="'Rename'">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>
      <button class="action-btn" @click.stop="handleMove" :title="'Move'">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="5 9 2 12 5 15"/>
          <polyline points="9 5 12 2 15 5"/>
          <polyline points="15 19 12 22 9 19"/>
          <polyline points="19 9 22 12 19 15"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
        </svg>
      </button>
      <button class="action-btn danger" @click.stop="handleDelete" :title="'Delete'">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
      </button>
    </div>
  </div>

  <!-- List View Item -->
  <tr v-else class="file-item list-item" @click="handleClick" @dblclick="handleDblClick" @contextmenu="handleContextMenu">
    <td class="col-name">
      <div class="file-name-cell">
        <svg v-if="props.item.is_folder" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <svg v-else-if="isImage" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path :d="ICONS.image.path" />
          <polyline :points="ICONS.image.points" />
        </svg>
        <svg v-else-if="isPdf" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path :d="ICONS.pdf.path" />
          <polyline :points="ICONS.pdf.points" />
        </svg>
        <svg v-else-if="isVideo" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path :d="ICONS.video.path" />
          <polyline :points="ICONS.video.points" />
        </svg>
        <svg v-else-if="isAudio" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <polyline :points="ICONS.audio.points" />
        </svg>
        <svg v-else-if="isText" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path :d="ICONS.text.path" />
          <polyline :points="ICONS.text.points" />
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path :d="ICONS.file.path" />
          <polyline :points="ICONS.file.points" />
        </svg>
        <span class="name-text">{{ props.item.name }}</span>
      </div>
    </td>
    <td class="col-size" v-if="!props.item.is_folder">{{ props.item.size_formatted }}</td>
    <td class="col-size" v-else>—</td>
    <td class="col-type">
      <span v-if="props.item.is_folder">Folder</span>
      <span v-else>{{ props.item.mime_type || 'File' }}</span>
    </td>
    <td class="col-modified">{{ formatDate(props.item.updated_at) }}</td>
    <td class="col-actions">
      <div class="file-actions">
        <button class="action-btn" @click.stop="handleDownload" :title="'Download'" :disabled="props.item.is_folder">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        </button>
        <button class="action-btn" @click.stop="handleRename" :title="'Rename'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="action-btn" @click.stop="handleMove" :title="'Move'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="5 9 2 12 5 15"/><polyline points="9 5 12 2 15 5"/><polyline points="15 19 12 22 9 19"/><polyline points="19 9 22 12 19 15"/><line x1="2" y1="12" x2="22" y2="12"/>
          </svg>
        </button>
        <button class="action-btn danger" @click.stop="handleDelete" :title="'Delete'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
      </div>
    </td>
  </tr>
</template>

<style scoped>
.file-item {
  transition: transform 0.15s, box-shadow 0.15s;
}

.file-item.grid-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  border-radius: 12px;
  background: var(--code-bg);
  border: 1px solid transparent;
  cursor: pointer;
}

.file-item.grid-item:hover {
  border-color: var(--border);
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.file-item.grid-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.file-thumbnail {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  background: var(--bg);
}

.file-thumbnail.folder {
  background: linear-gradient(135deg, var(--accent-bg), var(--accent-border));
}

.thumb-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  color: var(--accent);
}

.file-type-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  padding: 2px 6px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 10px;
  border-radius: 4px;
  text-transform: uppercase;
}

.file-info {
  flex: 1;
  min-height: 0;
}

.file-name {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-h);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  margin: 0;
  font-size: 12px;
  color: var(--text);
}

.file-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
  opacity: 0;
  transition: opacity 0.15s;
}

.file-item.grid-item:hover .file-actions {
  opacity: 1;
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

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* List View */
.file-item.list-item {
  cursor: pointer;
}

.file-item.list-item:hover {
  background: var(--accent-bg);
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-name-cell svg {
  flex-shrink: 0;
  color: var(--accent);
}

.name-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.list-item .file-actions {
  display: flex;
  gap: 4px;
  justify-content: flex-end;
  opacity: 1;
}

.list-item .action-btn {
  width: 28px;
  height: 28px;
}
</style>