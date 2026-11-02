<script setup lang="ts">
import { ref } from 'vue'

interface Emits {
  createFolder: [parentId?: number]
  search: [query: string]
}

const emit = defineEmits<Emits>()

const searchQuery = ref('')
const isSearching = ref(false)
const showUpload = ref(false)

const props = defineProps<{
  currentFolderId: number | null
  loading: boolean
}>()

function handleSearch(event: Event) {
  const target = event.target as HTMLInputElement
  const query = target.value
  isSearching.value = query.length > 0
  emit('search', query)
}

function clearSearch() {
  searchQuery.value = ''
  isSearching.value = false
  emit('search', '')
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    // This would be handled by the parent component
    // We'll emit an event or use a composable
    input.value = ''
  }
}
</script>

<template>
  <div class="toolbar">
    <!-- Search - takes remaining space -->
    <div class="search-box" :class="{ active: isSearching }">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        type="text"
        v-model="searchQuery"
        @input="handleSearch"
        placeholder="Search files..."
        class="search-input"
      />
      <button v-if="isSearching" class="search-clear" @click="clearSearch" aria-label="Clear search">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <!-- Actions on the right -->
    <div class="toolbar-actions">
      <label class="upload-button">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <span>Upload</span>
        <input type="file" multiple @change="handleFileSelect" class="file-input" />
      </label>

      <button class="btn-primary" @click="emit('createFolder', props.currentFolderId)" :disabled="props.loading">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>New Folder</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  flex-shrink: 0;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 0;
  max-width: none;
}

.search-box.active .search-icon {
  color: var(--accent);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text);
  pointer-events: none;
  transition: color 0.2s;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 40px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--code-bg);
  color: var(--text-h);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.search-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text);
  border-radius: 4px;
  cursor: pointer;
}

.search-clear:hover {
  background: var(--code-bg);
  color: var(--text-h);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  min-width: fit-content;
}

/* Responsive: stack on small screens */
@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
  .search-box {
    order: 1;
    flex: 1 1 calc(100% - 16px);
    max-width: none;
  }
  .toolbar-actions {
    order: 2;
    width: 100%;
    justify-content: flex-end;
  }
}

.upload-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--code-bg);
  color: var(--text-h);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.upload-button:hover {
  background: var(--accent-bg);
  border-color: var(--accent-border);
}

.file-input {
  display: none;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 8px;
  font-size: 14px;
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