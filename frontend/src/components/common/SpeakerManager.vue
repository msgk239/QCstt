<template>
  <el-popover
    v-model:visible="dialogVisible"
    :width="320"
    trigger="manual"
    placement="bottom-start"
    popper-class="speaker-manager-popover"
    :offset="4"
    :show-arrow="false"
  >
    <template #reference>
      <div class="speaker-trigger">
        <el-select 
          :model-value="currentSpeaker?.speaker_id"
          size="small"
          placeholder="选择说话人"
          @change="handleSpeakerSelect"
        >
          <el-option
            v-for="id in ['speaker_0', 'speaker_1']"
            :key="id"
            :label="getSpeakerName(id)"
            :value="id"
          >
            <div class="speaker-option">
              <el-icon 
                :color="getSpeakerColor(id)"
                class="speaker-icon"
              >
                <User />
              </el-icon>
              {{ getSpeakerName(id) }}
            </div>
          </el-option>
          <el-option
            key="manage"
            label="管理说话人"
            value="manage"
            class="manage-option"
            @click="dialogVisible = true"
          >
            <div class="speaker-option">
              <el-icon class="speaker-icon"><Setting /></el-icon>
              管理说话人
            </div>
          </el-option>
        </el-select>
      </div>
    </template>

    <div class="speaker-manager">
      <div class="manager-header">
        <h3>说话人管理</h3>
      </div>
      <div class="current-speaker" v-if="currentSpeaker">
        <div class="speaker-info">
          <span class="label">当前选中：</span>
          <span class="original-name">{{ currentSpeaker.originalName }}</span>
          <el-icon><ArrowRight /></el-icon>
          <el-select
            v-model="currentSpeaker.newName"
            placeholder="选择说话人"
            size="small"
            class="name-input"
          >
            <el-option
              v-for="speaker in uniqueSpeakers"
              :key="speaker.name"
              :label="speaker.name"
              :value="speaker.name"
            >
              <div class="speaker-option">
                <el-icon :color="speaker.color" class="speaker-icon"><User /></el-icon>
                {{ speaker.name }}
              </div>
            </el-option>
          </el-select>
        </div>
      </div>

      <div class="speaker-list">
        <div
          v-for="(speaker, index) in uniqueSpeakers"
          :key="speaker.id"
          class="speaker-item"
        >
          <div class="speaker-info">
            <span class="original-name">{{ speaker.name }}</span>
            <el-icon><ArrowRight /></el-icon>
            <el-select
              v-model="speaker.newName"
              placeholder="选择说话人"
              size="small"
              class="name-input"
            >
              <el-option
                v-for="otherSpeaker in uniqueSpeakers"
                :key="otherSpeaker.name"
                :label="otherSpeaker.name"
                :value="otherSpeaker.name"
              >
                <div class="speaker-option">
                  <el-icon :color="otherSpeaker.color" class="speaker-icon"><User /></el-icon>
                  {{ otherSpeaker.name }}
                </div>
              </el-option>
            </el-select>
          </div>
          <div class="speaker-actions">
            <el-color-picker
              v-model="speaker.color"
              size="small"
              :predefine="predefineColors"
            />
          </div>
        </div>
      </div>

      <div class="batch-actions">
        <el-button type="primary" size="small" @click="handleBatchReplace">
          批量替换
        </el-button>
        <el-button size="small" @click="handleReset">
          重置
        </el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight, Delete, User, Setting } from '@element-plus/icons-vue'
import { useFileStore } from '@/stores/fileStore'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  speakers: {
    type: Array,
    required: true
  },
  currentSpeaker: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'save', 'update:speakers', 'speaker-select'])

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

// 获取 store
const fileStore = useFileStore()

// 监听对话框可见性
watch(() => props.visible, (val) => {
  console.log('SpeakerManager visible changed:', {
    val,
    speakers: props.speakers,
    currentSpeaker: props.currentSpeaker
  })
  dialogVisible.value = val
  if (val) {
    // 初始化说话人列表
    speakers.value = props.speakers.map(speaker => ({
      ...speaker,
      originalName: speaker.name,
      newName: speaker.name
    }))
    console.log('Initialized speakers:', speakers.value)
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 方法
const handleDelete = (index) => {
  speakers.value.splice(index, 1)
}

const handleBatchReplace = async () => {
  console.log('handleBatchReplace called with:', {
    uniqueSpeakers: uniqueSpeakers.value,
    speakers: speakers.value
  })
  const changes = uniqueSpeakers.value
    .filter(speaker => speaker.newName && speaker.name !== speaker.newName)
    .map(speaker => ({
      id: speaker.id,
      name: speaker.newName,
      color: speaker.color
    }))

  console.log('Changes to apply:', changes)

  if (!changes.length) {
    ElMessage.warning('没有需要更新的内容')
    return
  }

  // 更新所有说话人
  const updatedSpeakers = props.speakers.map(speaker => {
    const change = changes.find(c => c.id === speaker.id)
    if (change) {
      return {
        ...speaker,
        name: change.name,
        color: change.color
      }
    }
    return speaker
  })

  console.log('Updated speakers:', updatedSpeakers)
  // 发送更新事件
  emit('update:speakers', updatedSpeakers)
  ElMessage.success('更新成功')
  dialogVisible.value = false
}

const handleReset = () => {
  console.log('handleReset called')
  speakers.value = speakers.value.map(speaker => ({
    ...speaker,
    newName: speaker.originalName
  }))
  console.log('Reset speakers:', speakers.value)
}

// 计算唯一的说话人列表
const uniqueSpeakers = computed(() => {
  const uniqueMap = new Map()
  speakers.value.forEach(speaker => {
    if (!uniqueMap.has(speaker.id)) {
      uniqueMap.set(speaker.id, speaker)
    }
  })
  console.log('Computed uniqueSpeakers:', Array.from(uniqueMap.values()))
  return Array.from(uniqueMap.values())
})

// 添加当前说话人变更处理
watch(() => props.currentSpeaker, (val) => {
  console.log('Current speaker changed:', {
    currentSpeaker: val,
    speakerId: val?.speaker_id,
    name: val?.name
  })
}, { deep: true })

// 添加获取说话人颜色的方法
const getSpeakerColor = (id) => {
  const speaker = props.speakers.find(s => s.id === id)
  return speaker?.color || '#409EFF'
}

// 添加获取说话人名称的方法
const getSpeakerName = (id) => {
  const speaker = props.speakers.find(s => s.id === id)
  return speaker?.name || (id === 'speaker_0' ? '说话人 1' : '说话人 2')
}

// 修改选择处理方法
const handleSpeakerSelect = (speakerId) => {
  console.log('handleSpeakerSelect called with:', speakerId)
  if (speakerId === 'manage') {
    dialogVisible.value = true
    return
  }
  emit('speaker-select', speakerId)
}

// 修改 watch 以查看传入的 speakers
watch(() => props.speakers, (newSpeakers) => {
  console.log('Speakers prop changed:', newSpeakers)
}, { deep: true })
</script>

<style scoped>
.speaker-manager {
  padding: 0;
}

.manager-header {
  padding: 8px 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 12px;
}

.manager-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.speaker-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 0 12px;
}

.speaker-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.current-speaker {
  padding: 12px;
  margin: 0 12px 12px;
  background-color: var(--el-fill-color-lighter);
  border-radius: 4px;
}

.batch-actions {
  margin-top: 16px;
  padding: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
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

.speaker-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.speaker-icon {
  font-size: 16px;
}

.label {
  color: var(--el-text-color-secondary);
  margin-right: 8px;
}

.speaker-trigger {
  display: inline-block;
}

.speaker-trigger :deep(.el-select) {
  width: 150px;
}

.speaker-trigger :deep(.el-input__wrapper) {
  cursor: pointer;
}

.speaker-trigger :deep(.el-select__caret) {
  display: none;
}

.manage-option {
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: 4px;
  padding-top: 4px;
}

.speaker-trigger :deep(.el-select__caret) {
  display: inline-block;  /* 显示下拉箭头 */
}
</style>

<style>
/* 全局样式 */
.speaker-manager-popover {
  padding: 0 !important;
  max-width: 90vw;
  margin-top: 0 !important;
}

.speaker-manager-popover .el-popover__title {
  margin: 0;
  padding: 8px 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

/* 确保 popover 在其他元素之上 */
.speaker-manager-popover.el-popper {
  z-index: 2000;
}
</style> 