<script setup lang="ts">
import { ref } from 'vue'
import FolderTreeItem from './FolderTreeItem.vue'

interface Props {
  folder: any
  currentFolderId: number | null
}

interface Emits {
  navigate: [folderId: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const expanded = ref(true)

function toggleExpand() {
  expanded.value = !expanded.value
}

function handleClick(event: Event) {
  event.stopPropagation()
  emit('navigate', props.folder.id)
}
</script>

<template>
  <li class="folder-item">
    <button
      class="folder-button"
      :class="{ active: props.folder.id === props.currentFolderId }"
      @click="handleClick"
    >
      <button
        v-if="props.folder.children && props.folder.children.length > 0"
        class="expand-toggle"
        @click.stop="toggleExpand"
        aria-label="Toggle folder"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline :points="expanded ? '6 9 12 15 18 9' : '9 6 15 12 9 18'" />
        </svg>
      </button>
      <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="expand-placeholder" />

      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>
      <span class="folder-name">{{ props.folder.name }}</span>
    </button>

    <ul v-show="expanded" v-if="props.folder.children && props.folder.children.length > 0" class="folder-children">
      <FolderTreeItem
        v-for="child in props.folder.children"
        :key="child.id"
        :folder="child"
        :current-folder-id="props.currentFolderId"
        @navigate="emit('navigate', $event)"
      />
    </ul>
  </li>
</template>

<style scoped>
.folder-item {
  padding-left: 16px;
}

.folder-button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 6px 10px;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: var(--text);
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.folder-button:hover {
  background: var(--accent-bg);
  color: var(--text-h);
}

.folder-button.active {
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 500;
}

.expand-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  border-radius: 4px;
  color: var(--text);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s;
}

.expand-toggle:hover {
  background: var(--code-bg);
}

.expand-placeholder {
  flex-shrink: 0;
  opacity: 0;
}

.folder-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-children {
  list-style: none;
  padding: 0;
  margin: 0;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>