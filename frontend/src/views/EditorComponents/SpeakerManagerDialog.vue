<template>
  <el-dialog
    v-model="visible"
    title="说话人管理"
    width="500px"
  >
    <div class="speaker-manager">
      <div class="speaker-list">
        <div v-for="speaker in speakers" :key="speaker.id" class="speaker-item">
          <div class="speaker-name-mapping">
            <span class="original-name">{{ speaker.originalName }}</span>
            <el-icon><ArrowRight /></el-icon>
            <el-input v-model="speaker.name" placeholder="新名称" />
          </div>
          <el-color-picker v-model="speaker.color" size="small" />
        </div>
      </div>
      
      <div class="speaker-actions">
        <el-button @click="handleBatchReplace">批量替换</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const props = defineProps({
  speakers: {
    type: Array,
    required: true,
    default: () => []
  }
})

const localSpeakers = ref(
  Array.isArray(props.speakers) 
    ? [...props.speakers] 
    : []
)

const handleBatchReplace = () => {
  const nameMapping = {}
  localSpeakers.value.forEach(speaker => {
    if (speaker.name !== speaker.originalName) {
      nameMapping[speaker.originalName] = speaker.name
    }
  })
  
  // 触发事件通知父组件
  emit('batch-replace', nameMapping)
}

const handleReset = () => {
  localSpeakers.value.forEach(speaker => {
    speaker.name = speaker.originalName
    speaker.color = speaker.originalColor
  })
  emit('reset')
}

// 定义事件
const emit = defineEmits(['batch-replace', 'reset'])
</script>

<style scoped>
.speaker-manager {
  padding: 16px;
}

.speaker-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.speaker-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.speaker-name-mapping {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.speaker-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style> 