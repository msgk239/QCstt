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
              :color="getSpeakerColor(props.segment.speaker_id)"
              class="speaker-icon"
            >
              <User />
            </el-icon>
            {{ getSpeakerName(props.segment.speaker_id) }}
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
    </div>
  </el-popover>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'

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

const emit = defineEmits(['update:speakers', 'speaker-select'])

// 恢复内部状态
const dialogVisible = ref(false)
const newSpeakerName = ref('')

// 添加计算属性获取当前说话人
const currentSpeaker = computed(() => {
  const speaker = props.speakers.find(s => s.id === props.segment.speaker_id)
  return speaker || null
})

// 监听对话框状态
watch(dialogVisible, (val) => {
  if (!val) {
    newSpeakerName.value = ''
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

const getSpeakerColor = (id) => {
  const speaker = props.speakers.find(s => s.id === id)
  return speaker?.color || '#409EFF'
}

const getSpeakerName = (id) => {
  // 优先使用自定义显示名字
  if (props.segment.speakerDisplayName) {
    return props.segment.speakerDisplayName
  }
  // 否则使用原始名字
  const speaker = props.speakers.find(s => s.id === id)
  return speaker?.name || (id === 'speaker_0' ? '说话人 1' : '说话人 2')
}

const handleNameConfirm = () => {
  if (!newSpeakerName.value.trim()) {
    ElMessage.warning('请输入说话人名字')
    return
  }

  // 不修改原始的 speakers 数组
  const updatedSegment = {
    ...props.segment,
    speakerDisplayName: newSpeakerName.value.trim()
  }

  // 发出事件，让父组件处理更新
  emit('speaker-select', updatedSegment)
  
  // 关闭对话框
  dialogVisible.value = false
  
  // 清空输入
  newSpeakerName.value = ''
  
  ElMessage.success('更新成功')
}

// 添加 inputRef
const inputRef = ref(null)

// 添加焦点处理函数
const handleFocus = () => {
  // 确保输入框为空
  newSpeakerName.value = ''
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