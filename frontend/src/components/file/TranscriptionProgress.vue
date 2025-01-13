<template>
  <div class="transcription-progress" v-if="files.length">
    <div class="header">
      <span>正在转写 ({{ files.length }}个文件)</span>
      <div class="actions">
        <el-button link @click="isExpanded = !isExpanded">
          {{ isExpanded ? '收起' : '展开' }}详情
        </el-button>
        <el-button link @click="$emit('close')">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="files">
      <div v-for="file in files" :key="file.id" class="file-item">
        <div class="file-name">
          <el-icon><Document /></el-icon>
          {{ file.name }}
        </div>
        <div class="file-status">
          <template v-if="file.status === 'processing'">
            <el-progress 
              :percentage="file.progress" 
              :format="() => `${file.progress}% 预计还需 ${formatFileTime(file.remainingTime)}`"
              :color="file.progress > 50 ? '#67c23a' : '#409eff'"
            />
          </template>
          <template v-else-if="file.status === 'error'">
            <div class="error-message">
              <el-icon><Warning /></el-icon>
              {{ file.error }}
            </div>
            <el-button type="primary" link @click="$emit('retry', file)">
              重试
            </el-button>
          </template>
        </div>
        
        <template v-if="isExpanded">
          <div class="details">
            <div>• 正在处理：{{ file.currentSegment }}</div>
            <div>• 文件大小：{{ file.size }}</div>
            <div>• 预计完成时间：{{ calculateFinishTime(file) }}</div>
            <div>• 状态：{{ getStatusText(file.status) }}</div>
          </div>
        </template>
      </div>
    </div>

    <div class="footer" v-if="isExpanded">
      <div class="total-progress">
        总体进度：{{ totalProgress }}% 预计还需 {{ totalRemainingTime }}
      </div>
      <div class="actions">
        <el-button size="small" @click="handlePause">
          {{ isPaused ? '继续' : '暂停' }}
        </el-button>
        <el-button size="small" @click="handleCancel">取消</el-button>
        <el-button 
          size="small" 
          type="primary"
          v-if="hasErrors"
          @click="$emit('retry-all')"
        >
          全部重试
        </el-button>
      </div>
      <div class="auto-open">
        <el-checkbox v-model="autoOpenEditor">完成后自动打开编辑器</el-checkbox>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Close, Warning, Document } from '@element-plus/icons-vue'

const props = defineProps({
  files: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'pause', 'cancel', 'retry', 'retry-all'])

const isExpanded = ref(false)
const isPaused = ref(false)
const autoOpenEditor = ref(true)

const totalProgress = computed(() => {
  if (!props.files.length) return 0
  return Math.floor(props.files.reduce((sum, file) => sum + file.progress, 0) / props.files.length)
})

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}分${secs}秒`
}

const totalRemainingTime = computed(() => {
  const total = props.files.reduce((sum, file) => {
    const [min, sec] = file.remainingTime.split(':').map(Number)
    return sum + min * 60 + sec
  }, 0)
  
  return formatTime(total)
})

const formatFileTime = (time) => {
  const [min, sec] = time.split(':').map(Number)
  return formatTime(min * 60 + sec)
}

const handlePause = () => {
  isPaused.value = !isPaused.value
  emit('pause', isPaused.value)
}

const handleCancel = () => {
  emit('cancel')
}

const getStatusText = (status) => {
  const statusMap = {
    ready: '准备就绪',
    processing: '处理中',
    success: '已完成',
    error: '出错'
  }
  return statusMap[status] || status
}

const hasErrors = computed(() => {
  return props.files.some(file => file.status === 'error')
})

const calculateFinishTime = (file) => {
  const now = new Date()
  const remainingSeconds = file.remainingTime.split(':').reduce((acc, time) => (60 * acc) + +time)
  const finishTime = new Date(now.getTime() + remainingSeconds * 1000)
  return finishTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.transcription-progress {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  background: var(--el-bg-color);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
  z-index: 1000;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.file-item {
  margin-bottom: 16px;
}

.file-name {
  margin-bottom: 4px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.details {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.total-progress {
  margin-bottom: 12px;
}

.actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.auto-open {
  font-size: 12px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--el-color-danger);
  font-size: 12px;
}

.file-status {
  margin: 8px 0;
}

.el-progress {
  margin: 8px 0;
}
</style> 