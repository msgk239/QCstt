<template>
  <div class="note-toolbar">
    <el-dropdown trigger="click" @command="addNote">
      <el-button>
        添加注释<el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item :command="{ type: 'normal' }">
            <el-icon><InfoFilled /></el-icon>普通注释
          </el-dropdown-item>
          <el-dropdown-item :command="{ type: 'important' }">
            <el-icon><Warning /></el-icon>重要注释
          </el-dropdown-item>
          <el-dropdown-item :command="{ type: 'todo' }">
            <el-icon><Check /></el-icon>待办事项
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
    
    <el-switch
      v-model="showNotes"
      active-text="显示注释"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const showNotes = ref(true)
const notes = ref([])

const addNote = ({ type }) => {
  const selection = window.getSelection()
  if (!selection.rangeCount) return
  
  const range = selection.getRangeAt(0)
  const noteId = Date.now().toString()
  
  const noteSpan = document.createElement('span')
  noteSpan.className = `note-anchor note-type-${type}`
  noteSpan.dataset.noteId = noteId
  
  range.surroundContents(noteSpan)
  
  notes.value.push({
    id: noteId,
    type,
    text: '',
    visible: true,
    position: {
      segmentId: getCurrentSegmentId(),
      offset: range.startOffset
    }
  })
}

const getCurrentSegmentId = () => {
  // TODO: 获取当前段落ID
}

const jumpToNote = (noteId) => {
  const noteSpan = document.querySelector(`[data-note-id="${noteId}"]`)
  if (noteSpan) {
    noteSpan.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}
</script>

<style scoped>
.note-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.note-anchor {
  position: relative;
  cursor: pointer;
}

.note-type-normal {
  border-bottom: 2px dotted var(--el-color-info);
}

.note-type-important {
  border-bottom: 2px solid var(--el-color-danger);
}

.note-type-todo {
  border-bottom: 2px dashed var(--el-color-success);
}
</style> 