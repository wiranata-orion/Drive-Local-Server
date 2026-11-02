<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  item: any
}

interface Emits {
  close: []
  rename: [id: number, newName: string]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const name = ref('')
const error = ref('')

watch(() => props.item, (newItem) => {
  if (newItem) {
    name.value = newItem.name
    error.value = ''
  }
}, { immediate: true })

function validate() {
  if (!name.value.trim()) {
    error.value = 'Name cannot be empty'
    return false
  }
  if (name.value.trim() === props.item.name) {
    error.value = 'Name is unchanged'
    return false
  }
  const invalidChars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
  for (const char of invalidChars) {
    if (name.value.includes(char)) {
      error.value = `Name cannot contain '${char}'`
      return false
    }
  }
  error.value = ''
  return true
}

function handleSubmit() {
  if (validate()) {
    emit('rename', props.item.id, name.value.trim())
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    handleSubmit()
  } else if (event.key === 'Escape') {
    emit('close')
  }
}
</script>

<template>
  <div class="dialog-overlay" @click="emit('close')">
    <div class="dialog" @click.stop>
      <header class="dialog-header">
        <h2>Rename {{ props.item.is_folder ? 'Folder' : 'File' }}</h2>
        <button class="dialog-close" @click="emit('close')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </header>

      <div class="dialog-body">
        <div class="form-group">
          <label for="rename-input">New Name</label>
          <input
            id="rename-input"
            type="text"
            v-model="name"
            @keydown="handleKeydown"
            placeholder="Enter new name"
            class="form-input"
            :class="{ error: error }"
            autofocus
          />
          <p v-if="error" class="form-error">{{ error }}</p>
        </div>
      </div>

      <footer class="dialog-footer">
        <button class="btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn-primary" @click="handleSubmit" :disabled="!name.trim() || name.trim() === props.item.name">Rename</button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
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

.dialog {
  width: 100%;
  max-width: 400px;
  background: var(--bg);
  border-radius: 12px;
  box-shadow: var(--shadow);
  overflow: hidden;
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.dialog-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
}

.dialog-close {
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

.dialog-close:hover {
  background: var(--code-bg);
  color: var(--text-h);
}

.dialog-body {
  padding: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-h);
}

.form-input {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--code-bg);
  color: var(--text-h);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.form-input.error {
  border-color: #ef4444;
}

.form-error {
  margin: 0;
  font-size: 12px;
  color: #ef4444;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
}

.btn-secondary {
  padding: 10px 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-h);
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.btn-secondary:hover {
  background: var(--code-bg);
  border-color: var(--accent-border);
}

.btn-primary {
  padding: 10px 20px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 8px;
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