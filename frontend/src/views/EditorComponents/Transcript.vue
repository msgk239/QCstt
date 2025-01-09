<template>
  <div class="transcript" ref="transcriptRef">
    <div
      v-for="(segment, index) in segments"
      :key="index"
      class="segment"
      :class="{ active: isSegmentActive(segment) }"
      @click="seekTo(segment.start)"
    >
      <div class="segment-header">
        <el-dropdown trigger="click" @command="handleSpeakerChange($event, segment)">
          <span class="speaker-name" :style="{ color: getSpeakerColor(segment.speaker) }">
            {{ segment.speaker }}
            <el-icon><Edit /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="speaker in speakers"
                :key="speaker.id"
                :command="speaker.id"
              >
                {{ speaker.name }}
              </el-dropdown-item>
              <el-dropdown-item divided command="new">
                <el-icon><Plus /></el-icon>添加新说话人
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <span class="segment-time">{{ formatTime(segment.start) }}</span>
      </div>
      <div
        class="segment-text"
        contenteditable
        @input="handleSegmentInput($event, segment)"
        @blur="handleSegmentBlur($event, segment)"
        v-html="segment.text"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 状态
const segments = ref([])
const speakers = ref([])

// 方法
const isSegmentActive = (segment) => {
  // 判断段落是否激活
}

const seekTo = (time) => {
  // 跳转到指定时间
}

const handleSpeakerChange = (speakerId, segment) => {
  // 处理说话人变更
}

const getSpeakerColor = (speakerId) => {
  // 获取说话人颜色
}

const handleSegmentInput = (event, segment) => {
  // 处理段落输入
}

const handleSegmentBlur = (event, segment) => {
  // 处理段落失去焦点
}

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  return `${h > 0 ? h + ':' : ''}${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.transcript {
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
}

.segment {
  margin-bottom: 16px;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.segment:hover {
  background-color: var(--el-fill-color-light);
}

.segment.active {
  background-color: var(--el-color-primary-light-9);
}

.segment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.speaker-name {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.segment-time {
  color: var(--el-text-color-secondary);
  font-family: monospace;
}

.segment-text {
  padding: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  min-height: 24px;
  line-height: 1.5;
}

.segment-text:focus {
  outline: none;
  border-color: var(--el-color-primary);
}
</style> 