<template>
  <div class="transcript" ref="transcriptRef">
    <!-- 转写内容段落列表 -->
    <div class="segments">
      <div 
        v-for="segment in segments" 
        :key="segment.id"
        class="segment"
        :class="{ 'is-playing': isSegmentPlaying(segment) }"
      >
        <!-- 说话人信息 -->
        <div class="segment-header">
          <el-select 
            v-model="segment.speaker"
            size="small"
            @change="(val) => handleSpeakerChange(val, segment)"
          >
            <el-option
              v-for="speaker in speakers"
              :key="speaker.id"
              :label="speaker.name"
              :value="speaker.id"
            />
            <el-option key="new" label="+ 添加说话人" value="new" />
          </el-select>
          <span class="time">{{ formatTime(segment.start_time) }}</span>
        </div>

        <!-- 转写文本 -->
        <div class="segment-content">
          <div 
            class="segment-text"
            contenteditable="true"
            @input="(e) => handleContentChange(e, segment)"
          >
            <span
              v-for="(word, index) in splitTextWithTimestamps(segment)"
              :key="index"
              :class="{ 'word-highlight': isWordPlaying(word) }"
            >{{ word.text }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, watchEffect } from 'vue'

const props = defineProps({
  segments: {
    type: Array,
    required: true
  },
  speakers: {
    type: Array,
    required: true
  },
  currentTime: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['segment-update', 'speaker-change'])

const transcriptRef = ref(null)

// 格式化时间
const formatTime = (seconds) => {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 处理说话人变更
const handleSpeakerChange = (speakerId, segment) => {
  emit('speaker-change', speakerId, segment)
}

// 处理内容编辑
const handleContentChange = (event, segment) => {
  const text = event.target.textContent
  const updatedSegment = {
    ...segment,
    text: text,
  }
  emit('segment-update', updatedSegment)
}

// 优化 isSegmentPlaying 函数
const isSegmentPlaying = (segment) => {
  const buffer = 0.1 // 100ms 缓冲，避免边界判断问题
  return props.currentTime >= (segment.start_time - buffer) && 
         props.currentTime <= (segment.end_time + buffer)
}

// 将文本按时间戳分割
const splitTextWithTimestamps = (segment) => {
  if (!segment.timestamps || !segment.text) return [{ text: segment.text }]
  
  const text = segment.text
  const timestamps = segment.timestamps
  const minLength = Math.min(text.length, timestamps.length)
  
  return Array.from({ length: minLength }, (_, index) => ({
    text: text[index],
    start: timestamps[index].start,
    end: timestamps[index].end
  }))
}

// 判断单个词是否正在播放
const isWordPlaying = (word) => {
  if (!word.start || !word.end) return false
  const buffer = 0.05 // 50ms 缓冲
  return props.currentTime >= (word.start - buffer) && 
         props.currentTime <= (word.end + buffer)
}

// 添加调试代码
watch([() => props.segments, () => props.speakers], () => {
  console.log('segments:', props.segments)
  console.log('speakers:', props.speakers)
})
</script>

<style scoped>
.transcript {
  height: calc(100vh - 200px); /* 适当的高度 */
  overflow-y: auto;
  scroll-behavior: smooth;
}

.segments {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.segment {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}

.segment.is-playing {
  background: #f0f7ff;
  border-color: var(--el-color-primary);
}

.segment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.time {
  color: #666;
  font-size: 12px;
}

.segment-content {
  font-size: 14px;
  line-height: 1.6;
  min-height: 1.6em;
  outline: none;
  padding: 4px;
}

.segment-text {
  padding: 8px;
  border-radius: 4px;
  white-space: pre-wrap;
}

.word-highlight {
  background-color: var(--el-color-primary-light-5);
  border-radius: 2px;
}

.segment-text:focus {
  background: #f5f7fa;
  border-radius: 4px;
  outline: none;
}

.segment-text:focus .word-highlight {
  background-color: var(--el-color-primary-light-3);
}
</style> 