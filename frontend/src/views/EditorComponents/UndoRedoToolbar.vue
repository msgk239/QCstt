<template>
  <div class="undo-redo-toolbar">
    <el-button-group>
      <el-button @click="handleUndo" :disabled="!canUndo">
        <el-icon><Back /></el-icon>撤销
      </el-button>
      <el-button @click="handleRedo" :disabled="!canRedo">
        <el-icon><Right /></el-icon>重做
      </el-button>
    </el-button-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  undoStack: {
    type: Array,
    default: () => []
  },
  redoStack: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['undo', 'redo'])

const canUndo = computed(() => props.undoStack.length > 0)
const canRedo = computed(() => props.redoStack.length > 0)

const handleUndo = () => {
  if (canUndo.value) {
    emit('undo')
  }
}

const handleRedo = () => {
  if (canRedo.value) {
    emit('redo')
  }
}
</script>

<style scoped>
.undo-redo-toolbar {
  display: flex;
  align-items: center;
}
</style> 