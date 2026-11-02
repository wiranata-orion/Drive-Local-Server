<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { filesApi } from '@/api/files'

interface Props {
  item: any
}

interface Emits {
  close: []
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const imageScale = ref(1)
const imagePosition = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const textContent = ref('')

const isImage = computed(() => props.item?.mime_type?.startsWith('image/'))
const isPdf = computed(() => props.item?.mime_type === 'application/pdf')
const isText = computed(() => props.item?.mime_type?.startsWith('text/'))
const isVideo = computed(() => props.item?.mime_type?.startsWith('video/'))
const isAudio = computed(() => props.item?.mime_type?.startsWith('audio/'))

const previewUrl = computed(() => {
  if (!props.item) return ''
  return props.item.preview_url || (props.item.file ? `/media/${props.item.file}` : '')
})

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

function handleOverlayClick(event: MouseEvent) {
  if (event.target === event.currentTarget) {
    emit('close')
  }
}

function handleWheel(event: WheelEvent) {
  if (!isImage.value) return
  event.preventDefault()
  const delta = event.deltaY > 0 ? 0.9 : 1.1
  imageScale.value = Math.min(Math.max(imageScale.value * delta, 0.25), 5)
}

function handleMouseDown(event: MouseEvent) {
  if (!isImage.value || imageScale.value <= 1) return
  isDragging.value = true
  dragStart.value = { x: event.clientX - imagePosition.value.x, y: event.clientY - imagePosition.value.y }
}

function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value) return
  imagePosition.value = { x: event.clientX - dragStart.value.x, y: event.clientY - dragStart.value.y }
}

function handleMouseUp() {
  isDragging.value = false
}

function resetImage() {
  imageScale.value = 1
  imagePosition.value = { x: 0, y: 0 }
}

function zoomIn() {
  imageScale.value = Math.min(imageScale.value * 1.2, 5)
}

function zoomOut() {
  imageScale.value = Math.max(imageScale.value / 1.2, 0.25)
}

async function loadTextContent() {
  if (!props.item.preview_url) return
  try {
    const response = await fetch(props.item.preview_url)
    textContent.value = await response.text()
  } catch {
    textContent.value = 'Failed to load text content'
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)

  if (isText.value) {
    loadTextContent()
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<template>
  <div class="preview-overlay" @click="handleOverlayClick">
    <div class="preview-modal" @click.stop>
      <!-- Header -->
      <header class="preview-header">
        <div class="preview-title">
          <svg v-if="props.item.is_folder" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <svg v-else-if="isImage" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
          </svg>
          <svg v-else-if="isPdf" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
          </svg>
          <svg v-else-if="isVideo" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
          </svg>
          <svg v-else-if="isAudio" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><polyline points="10 15 15 10 15 15"/>
          </svg>
          <svg v-else-if="isText" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="4 7 4 4 20 4 20 17"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
          </svg>
          <span>{{ props.item.name }}</span>
        </div>

        <div class="preview-actions">
          <button v-if="isImage" class="preview-btn" @click="zoomOut" title="Zoom out">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/>
            </svg>
          </button>
          <button v-if="isImage" class="preview-btn" @click="zoomIn" title="Zoom in">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
            </svg>
          </button>
          <button v-if="isImage" class="preview-btn" @click="resetImage" title="Reset zoom">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="2" width="20" height="20" rx="2"/>
            </svg>
          </button>
          <a v-if="!props.item.is_folder" :href="previewUrl" download class="preview-btn" target="_blank">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </a>
          <button class="preview-btn close-btn" @click="emit('close')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </header>

      <!-- Content -->
      <div class="preview-content" @wheel.passive="handleWheel">
        <!-- Image -->
        <div v-if="isImage" class="image-preview" @mousedown="handleMouseDown">
          <img
            :src="previewUrl"
            :alt="props.item.name"
            class="preview-image"
            :style="{ transform: `translate(${imagePosition.x}px, ${imagePosition.y}px) scale(${imageScale})` }"
          />
          <div v-if="imageScale > 1" class="zoom-indicator">{{ Math.round(imageScale * 100) }}%</div>
        </div>

        <!-- PDF -->
        <iframe v-else-if="isPdf" class="pdf-preview" :src="previewUrl" title="PDF Preview"></iframe>

        <!-- Video -->
        <video v-else-if="isVideo" class="video-preview" controls :src="previewUrl" title="Video Preview"></video>

        <!-- Audio -->
        <audio v-else-if="isAudio" class="audio-preview" controls :src="previewUrl" title="Audio Preview"></audio>

        <!-- Text -->
        <pre v-else-if="isText" class="text-preview">
          <code v-text="textContent"></code>
        </pre>

        <!-- Unsupported -->
        <div v-else class="unsupported-preview">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <p>Preview not available</p>
          <a :href="previewUrl" download class="btn-primary" target="_blank">Download to view</a>
        </div>
      </div>

      <!-- Footer -->
      <footer class="preview-footer">
        <div class="file-info">
          <span>{{ props.item.size_formatted }}</span>
          <span>·</span>
          <span>{{ props.item.mime_type || 'Unknown' }}</span>
          <span>·</span>
          <span>{{ new Date(props.item.updated_at).toLocaleString() }}</span>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
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

.preview-modal {
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  background: var(--bg);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-h);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.preview-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preview-btn {
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
  transition: background 0.15s, color 0.15s;
}

.preview-btn:hover {
  background: var(--accent-bg);
  color: var(--accent);
}

.preview-btn a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: var(--text-h);
}

.close-btn {
  margin-left: 4px;
}

.preview-content {
  flex: 1;
  overflow: auto;
  position: relative;
  background: #1a1a2e;
}

.image-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  position: relative;
  touch-action: none;
}

.preview-image {
  max-width: 100%;
  max-height: 80vh;
  transform-origin: center center;
  transition: transform 0.1s ease-out;
  cursor: grab;
}

.preview-image:active {
  cursor: grabbing;
}

.zoom-indicator {
  position: absolute;
  bottom: 16px;
  right: 16px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-family: var(--mono);
}

.pdf-preview, .video-preview, .audio-preview {
  width: 100%;
  height: 60vh;
  border: none;
  background: #000;
}

.text-preview {
  padding: 20px;
  max-height: 60vh;
  overflow: auto;
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-h);
  background: var(--code-bg);
}

.text-preview code {
  white-space: pre-wrap;
  word-break: break-word;
}

.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: var(--text);
  gap: 16px;
  text-align: center;
  padding: 20px;
}

.unsupported-preview svg {
  opacity: 0.4;
}

.preview-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--text);
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>