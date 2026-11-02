<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  currentFolderId: number | null
  folders: any[]
}

interface Emits {
  navigate: [folderId: number | null]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const router = useRouter()

const breadcrumbs = computed(() => {
  const crumbs = [{ id: null, name: 'My Drive' }]

  if (props.currentFolderId) {
    // Find the folder and build path
    const buildPath = (folderId: number, allFolders: any[]): any[] => {
      for (const folder of allFolders) {
        if (folder.id === folderId) {
          return [{ id: folder.id, name: folder.name }]
        }
        if (folder.children && folder.children.length > 0) {
          const childPath = buildPath(folderId, folder.children)
          if (childPath.length > 0) {
            return [{ id: folder.id, name: folder.name }, ...childPath]
          }
        }
      }
      return []
    }

    const path = buildPath(props.currentFolderId, props.folders)
    crumbs.push(...path.reverse())
  }

  return crumbs
})

function navigateTo(index: number) {
  if (index === 0) {
    emit('navigate', null)
  } else {
    emit('navigate', breadcrumbs.value[index].id)
  }
}
</script>

<template>
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <ol class="breadcrumb-list">
      <li v-for="(crumb, index) in breadcrumbs" :key="crumb.id" class="breadcrumb-item">
        <button
          v-if="index < breadcrumbs.length - 1"
          class="breadcrumb-link"
          @click="navigateTo(index)"
        >
          <svg v-if="index === 0" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <span v-else>{{ crumb.name }}</span>
          <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
        <span v-else class="breadcrumb-current">{{ crumb.name }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumbs {
  overflow-x: auto;
  white-space: nowrap;
  padding: 4px 0;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: 4px;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  color: var(--text);
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.breadcrumb-link:hover {
  background: var(--accent-bg);
  color: var(--accent);
}

.breadcrumb-link svg {
  flex-shrink: 0;
}

.chevron {
  margin-left: 4px;
  opacity: 0.6;
}

.breadcrumb-current {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  color: var(--text-h);
  font-size: 14px;
  font-weight: 500;
}
</style>