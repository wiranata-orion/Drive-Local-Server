<script setup lang="ts">
import { computed } from 'vue'
import FileItem from './FileItem.vue'

interface Props {
  items: any[]
  viewMode: 'grid' | 'list'
  sortBy: 'name' | 'size' | 'modified' | 'type'
  sortAsc: boolean
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

// Sort items
const sortedItems = computed(() => {
  return [...props.items].sort((a, b) => {
    // Folders first
    if (a.is_folder !== b.is_folder) {
      return a.is_folder ? -1 : 1
    }

    let comparison = 0
    switch (props.sortBy) {
      case 'name':
        comparison = a.name.localeCompare(b.name)
        break
      case 'size':
        comparison = a.size - b.size
        break
      case 'modified':
        comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime()
        break
      case 'type':
        comparison = (a.mime_type || '').localeCompare(b.mime_type || '')
        break
    }
    return props.sortAsc ? comparison : -comparison
  })
})
</script>

<template>
  <div class="file-grid" :class="props.viewMode">
    <!-- Grid View -->
    <div v-if="props.viewMode === 'grid'" class="grid-view" role="grid">
      <FileItem
        v-for="item in sortedItems"
        :key="item.id"
        :item="item"
        @open="emit('open', $event)"
        @context-menu="emit('contextMenu', $event, $event)"
        @download="emit('download', $event)"
        @rename="emit('rename', $event)"
        @move="emit('move', $event)"
        @delete="emit('delete', $event)"
      />
    </div>

    <!-- List View -->
    <table v-else class="list-view" role="grid">
      <thead>
        <tr>
          <th scope="col" class="col-name">
            <button @click="$emit('update:sortBy', 'name')" class="sortable-header">
              Name
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="18" x2="12" y2="6"/>
              </svg>
            </button>
          </th>
          <th scope="col" class="col-size">
            <button @click="$emit('update:sortBy', 'size')" class="sortable-header">
              Size
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="18" x2="12" y2="6"/>
              </svg>
            </button>
          </th>
          <th scope="col" class="col-type">
            <button @click="$emit('update:sortBy', 'type')" class="sortable-header">
              Type
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="18" x2="12" y2="6"/>
              </svg>
            </button>
          </th>
          <th scope="col" class="col-modified">
            <button @click="$emit('update:sortBy', 'modified')" class="sortable-header">
              Modified
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="18" x2="12" y2="6"/>
              </svg>
            </button>
          </th>
          <th scope="col" class="col-actions"></th>
        </tr>
      </thead>
      <tbody>
        <FileItem
          v-for="item in sortedItems"
          :key="item.id"
          :item="item"
          :list-view="true"
          @open="emit('open', $event)"
          @context-menu="emit('contextMenu', $event, $event)"
          @download="emit('download', $event)"
          @rename="emit('rename', $event)"
          @move="emit('move', $event)"
          @delete="emit('delete', $event)"
        />
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.file-grid {
  height: 100%;
}

.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  padding: 4px;
}

.list-view {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.list-view th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 500;
  color: var(--text);
  border-bottom: 1px solid var(--border);
  background: var(--code-bg);
  white-space: nowrap;
}

.list-view td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.list-view tr:hover td {
  background: var(--accent-bg);
}

.sortable-header {
  display: flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: transparent;
  color: var(--text);
  font: inherit;
  cursor: pointer;
  padding: 0;
}

.sortable-header:hover {
  color: var(--accent);
}

.col-name { width: 40%; min-width: 200px; }
.col-size { width: 15%; min-width: 100px; text-align: right; }
.col-type { width: 15%; min-width: 100px; }
.col-modified { width: 20%; min-width: 150px; }
.col-actions { width: 10%; min-width: 80px; }
</style>