<template>
  <el-dialog
    v-model="dialogVisible"
    title="说话人管理"
    width="500px"
  >
    <div class="speaker-manager">
      <div class="speaker-list">
        <div
          v-for="(speaker, index) in speakers"
          :key="speaker.id"
          class="speaker-item"
        >
          <div class="speaker-info">
            <span class="original-name">{{ speaker.originalName }}</span>
            <el-icon><ArrowRight /></el-icon>
            <el-input
              v-model="speaker.newName"
              placeholder="新名称"
              size="small"
              class="name-input"
            />
          </div>
          <div class="speaker-actions">
            <el-color-picker
              v-model="speaker.color"
              size="small"
              :predefine="predefineColors"
            />
            <el-button
              type="danger"
              circle
              size="small"
              @click="handleDelete(index)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <div class="batch-actions">
        <el-button type="primary" @click="handleBatchReplace">
          批量替换
        </el-button>
        <el-button @click="handleReset">
          重置
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  initialSpeakers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'save'])

// 状态
const dialogVisible = ref(false)
const speakers = ref([])
const predefineColors = [
  '#409EFF',
  '#67C23A',
  '#E6A23C',
  '#F56C6C',
  '#909399',
  '#9B59B6',
  '#3498DB',
  '#1ABC9C'
]

// 监听对话框可见性
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    // 初始化说话人列表
    speakers.value = props.initialSpeakers.map(speaker => ({
      ...speaker,
      originalName: speaker.name,
      newName: speaker.name
    }))
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 方法
const handleDelete = (index) => {
  speakers.value.splice(index, 1)
}

const handleBatchReplace = () => {
  const changes = speakers.value
    .filter(speaker => speaker.originalName !== speaker.newName)
    .map(speaker => ({
      id: speaker.id,
      name: speaker.newName,
      color: speaker.color
    }))

  if (!changes.length) {
    ElMessage.warning('没有需要更新的内容')
    return
  }

  emit('save', changes)
  dialogVisible.value = false
  ElMessage.success('更新成功')
}

const handleReset = () => {
  speakers.value = speakers.value.map(speaker => ({
    ...speaker,
    newName: speaker.originalName
  }))
}
</script>

<style scoped>
.speaker-manager {
  padding: 0 20px;
}

.speaker-list {
  max-height: 400px;
  overflow-y: auto;
}

.speaker-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.speaker-item:last-child {
  border-bottom: none;
}

.speaker-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.original-name {
  min-width: 80px;
}

.name-input {
  width: 150px;
}

.speaker-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.batch-actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style> 