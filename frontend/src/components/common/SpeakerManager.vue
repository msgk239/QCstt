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
        <el-button 
          size="small"
          @click.stop="handleButtonClick"
          class="speaker-button"
        >
          <div class="speaker-option">
            <el-icon 
              :color="getSpeakerColor()"
              class="speaker-icon"
            >
              <User />
            </el-icon>
            {{ getSpeakerName() }}
          </div>
        </el-button>
      </div>
    </template>

    <div class="speaker-manager">
      <div class="name-editor">
        <el-input
          v-model="newSpeakerName"
          size="small"
          placeholder="可以修改说话人名字"
          ref="inputRef"
          @focus="handleFocus"
        >
          <template #append>
            <el-button @click="handleNameConfirm">确认</el-button>
          </template>
        </el-input>
      </div>
      
      <!-- 添加说话人列表 -->
      <div class="speaker-list">
        <div 
          v-for="speaker in localSpeakers" 
          :key="speaker.speakerKey" 
          class="speaker-item"
          @click="handleSpeakerItemClick(speaker)"
          :class="{ 'disabled': isCurrentSpeaker(speaker) }"
        >
          <div class="speaker-info">
            <el-checkbox 
              v-model="speaker.selected" 
              @change="(val) => handleSpeakerCheck(speaker, val)"
              @click.stop
              :disabled="isCurrentSpeaker(speaker)"
            >
              <div class="speaker-label">
                <el-icon :color="speaker.color" class="speaker-icon">
                  <User />
                </el-icon>
                <span>{{ speaker.speakerDisplayName }}</span>
              </div>
            </el-checkbox>
          </div>
        </div>
      </div>

      <!-- 添加批量更新选项和确认按钮 -->
      <div class="batch-update-section">
        <el-checkbox v-model="batchUpdate" class="batch-checkbox">
          批量修改相同名称的说话人
        </el-checkbox>
        <el-button 
          type="primary" 
          size="small" 
          @click="handleConfirm"
          class="confirm-button"
        >
          确认
        </el-button>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { nanoid } from 'nanoid'

const props = defineProps({
  speakers: {
    type: Array,
    required: true
  },
  segment: {
    type: Object,
    required: true
  },
  managerId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['speaker-select'])

// 恢复内部状态
const dialogVisible = ref(false)
const newSpeakerName = ref('')

// 添加计算属性获取当前说话人
const currentSpeaker = computed(() => {
  const speaker = props.speakers.find(s => s.speakerKey === props.segment.speakerKey)
  return speaker || null
})

// 监听对话框状态
watch(dialogVisible, (val) => {
  if (!val) {
    newSpeakerName.value = ''
    localSpeakers.value.forEach(speaker => speaker.selected = false)
  } else {
    // 当对话框打开时，清空输入框并设置焦点
    newSpeakerName.value = ''
    // 使用 nextTick 确保 DOM 更新后再设置焦点
    nextTick(() => {
      inputRef.value?.input?.focus()
    })
  }
})

const handleButtonClick = () => {
  // 阻止事件冒泡，防止触发父组件的点击事件
  event.stopPropagation()
  dialogVisible.value = true
}

const getSpeakerColor = () => {
  const speaker = props.speakers.find(s => s.speakerKey === props.segment.speakerKey)
  return speaker?.color || '#409EFF'
}

const getSpeakerName = () => {
  // 优先使用 speakerDisplayName
  if (props.segment.speakerDisplayName) {
    return props.segment.speakerDisplayName
  }
  
  // 如果没有 speakerDisplayName，尝试从 currentSpeaker 获取
  if (currentSpeaker.value?.speakerDisplayName) {
    return currentSpeaker.value.speakerDisplayName
  }
  
  // 最后尝试使用 speaker_name
  if (props.segment.speaker_name) {
    return props.segment.speaker_name
  }
  
  // 如果都没有，返回默认值
  return '未知说话人'
}

const handleNameConfirm = () => {
  if (!newSpeakerName.value.trim()) {
    ElMessage.warning('请输入说话人名字')
    return
  }

  // 生成随机颜色
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  const randomColor = colors[Math.floor(Math.random() * colors.length)]

  // 使用新的格式生成speakerKey
  const speakerKey = `custom_${Date.now()}`
  
  // 创建新说话人
  const newSpeaker = {
    // 前端使用的字段（可变）
    speakerKey,                                  // 当前说话人Key
    speakerDisplayName: newSpeakerName.value.trim(),  // 显示用的名字
    color: randomColor,                          // 显示颜色
    
    // 原始字段（不变）
    speaker_id: null,                           // 新添加的说话人没有原始ID
    speaker_name: null,                         // 新添加的说话人没有原始名字
    
    selected: true
  }

  // 更新本地列表
  localSpeakers.value = [...localSpeakers.value, {
    ...newSpeaker,
    selected: true
  }]

  // 设置选中的说话人
  selectedSpeaker.value = newSpeaker

  // 清空输入
  newSpeakerName.value = ''
  
  ElMessage.success('已添加新说话人并选中，请选择是否批量更新后点击确认')
}

// 添加 inputRef
const inputRef = ref(null)

// 添加焦点处理函数
const handleFocus = () => {
  // 确保输入框为空
  newSpeakerName.value = ''
}

// 添加批量更新状态
const batchUpdate = ref(false)
const selectedSpeaker = ref(null)

// 在 script setup 中添加
const localSpeakers = ref(props.speakers.map(speaker => ({
  // 前端使用的字段（可变）
  speakerKey: speaker.speakerKey,
  speakerDisplayName: speaker.speakerDisplayName,
  color: speaker.color,
  
  // 原始字段（不变）
  speaker_id: speaker.speaker_id,
  speaker_name: speaker.speaker_name,
  
  selected: false
})))

// 修改 watch 以确保深度监听
watch(() => props.speakers, (newSpeakers) => {
  localSpeakers.value = newSpeakers.map(speaker => ({
    // 前端使用的字段（可变）
    speakerKey: speaker.speakerKey,
    speakerDisplayName: speaker.speakerDisplayName,
    color: speaker.color,
    
    // 原始字段（不变）
    speaker_id: speaker.speaker_id,
    speaker_name: speaker.speaker_name,
    
    selected: false
  }))
}, { deep: true, immediate: true })

// 修改选择处理函数
const handleSpeakerCheck = (speaker, checked) => {
  if (!checked) {
    selectedSpeaker.value = null
    speaker.selected = false
    return
  }
  
  // 取消其他说话人的选中状态
  localSpeakers.value.forEach(s => {
    s.selected = s.speakerKey === speaker.speakerKey
  })
  
  // 更新选中的说话人
  selectedSpeaker.value = speaker
}

// 修改确认处理函数
const handleConfirm = () => {
  if (!selectedSpeaker.value) {
    ElMessage.warning('请先选择一个说话人')
    return
  }

  // 创建更新对象
  const updatedSegment = {
    ...props.segment,           // 保留原段落的所有信息
    
    // 更新所有相关字段
    speakerKey: selectedSpeaker.value.speakerKey,
    speakerDisplayName: selectedSpeaker.value.speakerDisplayName,
    speaker_name: selectedSpeaker.value.speakerDisplayName,  // 同步更新 speaker_name
    speaker_id: selectedSpeaker.value.speakerKey,  // 同步更新 speaker_id
    color: selectedSpeaker.value.color,  // 使用新说话人的颜色
    oldSpeakerKey: props.segment.speakerKey,  // 添加当前说话人的 key
    batchUpdate: true  // 设置为 true
  }

  // 如果有子段落，也更新子段落
  if (props.segment.subSegments) {
    updatedSegment.subSegments = props.segment.subSegments.map(sub => ({
      ...sub,
      speakerKey: selectedSpeaker.value.speakerKey,
      speakerDisplayName: selectedSpeaker.value.speakerDisplayName,
      speaker_name: selectedSpeaker.value.speakerDisplayName,
      speaker_id: selectedSpeaker.value.speakerKey
    }))
  }

  // 发送更新事件
  emit('speaker-select', updatedSegment)
  
  // 重置状态
  dialogVisible.value = false
  newSpeakerName.value = ''
  batchUpdate.value = false
  selectedSpeaker.value = null
  localSpeakers.value.forEach(speaker => speaker.selected = false)
}

// 修改 handleSpeakerItemClick
const handleSpeakerItemClick = (speaker) => {
  if (isCurrentSpeaker(speaker)) return
  
  // 更新选中的说话人
  selectedSpeaker.value = speaker
  
  // 更新选中状态
  localSpeakers.value.forEach(s => {
    s.selected = s.speakerKey === speaker.speakerKey
  })

  // 创建更新对象
  const updatedSegment = {
    ...props.segment,           // 保留原段落的所有信息
    
    // 更新所有相关字段
    speakerKey: speaker.speakerKey,
    speakerDisplayName: speaker.speakerDisplayName,
    speaker_name: speaker.speakerDisplayName,  // 同步更新 speaker_name
    speaker_id: speaker.speakerKey,  // 同步更新 speaker_id
    color: speaker.color,  // 使用新说话人的颜色
    oldSpeakerKey: props.segment.speakerKey,  // 添加当前说话人的 key
    batchUpdate: true  // 设置为 true
  }

  // 如果有子段落，也更新子段落
  if (props.segment.subSegments) {
    updatedSegment.subSegments = props.segment.subSegments.map(sub => ({
      ...sub,
      speakerKey: speaker.speakerKey,
      speakerDisplayName: speaker.speakerDisplayName,
      speaker_name: speaker.speakerDisplayName,
      speaker_id: speaker.speakerKey
    }))
  }

  // 发送更新事件
  emit('speaker-select', updatedSegment)
  
  // 关闭对话框
  dialogVisible.value = false
}

// 修改 isCurrentSpeaker 函数
const isCurrentSpeaker = (speaker) => {
  // 使用 speakerKey 来判断是否是当前说话人
  return speaker.speakerKey === props.segment.speakerKey
}

// 仅在本地管理说话人的状态
const localSpeakerState = ref({})

const updateSpeaker = (key, newSpeaker) => {
  if (batchUpdate.value) {
    // 仅在选项勾选时更新全局状态
    emit('update-global-speaker', key, newSpeaker)
  } else {
    // 否则仅更新本地状态
    localSpeakerState.value[key] = newSpeaker
  }
}
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
  margin-top: 12px;
  max-height: 200px;
  overflow-y: auto;
  border-top: 1px solid var(--el-border-color-lighter);
}

.speaker-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  transition: background-color 0.3s;
  cursor: pointer;
}

.speaker-item:hover {
  background-color: var(--el-fill-color-light);
}

.speaker-info {
  display: flex;
  align-items: center;
  width: 100%;
}

.speaker-info :deep(.el-checkbox) {
  width: 100%;
  margin-right: 0;
}

.speaker-info :deep(.el-checkbox__label) {
  padding-left: 8px;
  width: 100%;
}

.speaker-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.speaker-icon {
  font-size: 16px;
}

.speaker-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.speaker-item.disabled:hover {
  background-color: transparent;
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

.speaker-button {
  width: 150px;
  display: flex;
  justify-content: flex-start;
  padding: 8px 12px;
}

.speaker-button .speaker-option {
  width: 100%;
}

.name-editor {
  padding: 20px;
}

.name-editor :deep(.el-input-group__append) {
  padding: 0;
  position: relative;
  left: 0;  /* 移除左偏移 */
}

.name-editor :deep(.el-input-group__append button) {
  border: none;
  height: 32px;
  padding: 0 24px;  /* 增加内边距 */
  min-width: 80px;  /* 设置最小宽度 */
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  transition: background-color 0.3s ease;  /* 添加过渡效果 */
}

.name-editor :deep(.el-input-group__append button:hover) {
  background-color: var(--el-color-primary) !important;
  color: white !important;
}

.batch-update-section {
  padding: 12px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.batch-checkbox {
  color: var(--el-text-color-regular);
}

.confirm-button {
  min-width: 80px;
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