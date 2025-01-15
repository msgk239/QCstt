<template>
  <div class="transcript" ref="transcriptRef">
    <!-- 转写内容段落列表 -->
    <div class="segments">
      <div 
        v-for="segment in mergedSegments" 
        :key="segment.id"
        class="segment"
        :class="{ 
          'is-playing': isSegmentPlaying(segment),
          'is-selected': segment.isSelected 
        }"
      >
        <!-- 说话人信息 -->
        <div class="segment-header">
          <SpeakerManager
            :segment="segment"
            :speakers="props.speakers"
            :manager-id="segment.id"
            @speaker-select="handleSpeakerChange"
          />
          <span class="time">{{ formatTime(segment.start_time) }}</span>
        </div>

        <!-- 转写文本 -->
        <div 
          class="segment-content"
          @click="handleSegmentClick(segment)"
        >
          <div 
            class="segment-text"
            contenteditable="true"
            @input="(e) => handleContentChange(e, segment)"
          >
            <template v-for="(subSegment, subIndex) in segment.subSegments" :key="subIndex">
              <span
                v-for="(word, wordIndex) in splitTextWithTimestamps(subSegment)"
                :key="`${subIndex}-${wordIndex}`"
                :class="{ 'word-highlight': isWordPlaying(word) }"
              >{{ word.text }}</span>
              <br v-if="subIndex < segment.subSegments.length - 1">
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, watchEffect, computed } from 'vue'
import SpeakerManager from '@/components/common/SpeakerManager.vue'

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

const emit = defineEmits(['segment-update', 'speaker-change', 'timeupdate', 'segment-select'])

const transcriptRef = ref(null)

// 格式化时间
const formatTime = (seconds) => {
  const date = new Date(seconds * 1000)
  return date.toISOString().substr(11, 8).replace(/^00:/, '')
}

// 处理说话人变更
const handleSpeakerChange = (updatedSegment) => {
  // 仅通过事件通知父组件更新
  emit('speaker-change', updatedSegment)
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
  return props.currentTime >= segment.start_time && 
         props.currentTime <= segment.end_time
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

// 添加合并段落的计算属性
const mergedSegments = computed(() => {
  if (!props.segments) return []
  
  const result = []
  let currentGroup = null
  
  props.segments.forEach(segment => {
    // 使用 speakerKey 判断是否是同一个说话人
    const currentKey = segment.speakerKey
    const groupKey = currentGroup?.speakerKey
    
    // 如果是新的说话人或者第一个段落
    if (!currentGroup || groupKey !== currentKey) {
      // 保存当前组
      if (currentGroup) {
        result.push(currentGroup)
      }
      
      // 创建新组
      currentGroup = {
        ...segment,
        subSegments: [segment],
        text: segment.text || ''
      }
    } else {
      // 添加到当前组
      currentGroup.subSegments.push(segment)
      currentGroup.text = `${currentGroup.text}\n${segment.text || ''}`.trim()
      currentGroup.end_time = segment.end_time
    }
  })
  
  // 添加最后一组
  if (currentGroup) {
    result.push(currentGroup)
  }
  
  return result
})

// 添加新的方法
const handleSegmentClick = (segment) => {
  const updatedSegments = props.segments.map(s => ({
    ...s,
    isSelected: s.id === segment.id
  }))
  emit('segment-select', updatedSegments)
}

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

.sub-segment {
  margin-bottom: 8px;
}
.sub-segment:last-child {
  margin-bottom: 0;
}

.segment.is-selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}
</style> 