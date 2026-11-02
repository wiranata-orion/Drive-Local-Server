<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

interface Props {
  position: { x: number; y: number }
  item: any
}

interface Emits {
  close: []
  open: [item: any]
  download: [item: any]
  rename: [item: any]
  move: [item: any]
  delete: [item: any]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const menuRef = ref<HTMLElement>()

function handleClickOutside(event: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    emit('close')
  }
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeyDown)
  // Prevent context menu from showing browser menu
  document.addEventListener('contextmenu', (e) => e.preventDefault(), { once: true })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <div
    ref="menuRef"
    class="context-menu"
    :style="{ left: props.position.x + 'px', top: props.position.y + 'px' }"
    role="menu"
  >
    <div class="menu-header">
      <svg v-if="props.item.is_folder" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      </svg>
      <span>{{ props.item.name }}</span>
    </div>

    <div class="menu-divider"></div>

    <button class="menu-item" @click="emit('open', props.item)" role="menuitem">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
      <span>{{ props.item.is_folder ? 'Open' : 'Preview' }}</span>
    </button>

    <button class="menu-item" @click="emit('download', props.item)" role="menuitem" :disabled="props.item.is_folder">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      <span>Download</span>
    </button>

    <div class="menu-divider"></div>

    <button class="menu-item" @click="emit('rename', props.item)" role="menuitem">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
      <span>Rename</span>
      <kbd>F2</kbd>
    </button>

    <button class="menu-item" @click="emit('move', props.item)" role="menuitem">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="5 9 2 12 5 15"/>
        <polyline points="9 5 12 2 15 5"/>
        <polyline points="15 19 12 22 9 19"/>
        <polyline points="19 9 22 12 19 15"/>
        <line x1="2" y1="12" x2="22" y2="12"/>
      </svg>
      <span>Move to...</span>
    </button>

    <div class="menu-divider"></div>

    <button class="menu-item danger" @click="emit('delete', props.item)" role="menuitem">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="3 6 5 6 21 6"/>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
      </svg>
      <span>Move to Trash</span>
      <kbd>Del</kbd>
    </button>
  </div>
</template>

<style scoped>
.context-menu {
  position: fixed;
  z-index: 1000;
  min-width: 200px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
  animation: fadeIn 0.1s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-h);
  background: var(--code-bg);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-divider {
  height: 1px;
  background: var(--border);
  margin: 4px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-h);
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: background 0.1s;
}

.menu-item:hover:not(:disabled) {
  background: var(--accent-bg);
  color: var(--accent);
}

.menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-item svg {
  flex-shrink: 0;
  color: var(--text);
}

.menu-item kbd {
  margin-left: auto;
  padding: 2px 6px;
  background: var(--code-bg);
  border-radius: 4px;
  font-size: 11px;
  font-family: var(--mono);
  color: var(--text);
}

.menu-item.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
</style>