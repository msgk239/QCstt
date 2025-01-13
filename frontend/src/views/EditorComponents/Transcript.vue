<template>
  <div class="transcript" ref="transcriptRef">
    <!-- 转写内容段落列表 -->
    <div class="segments">
      <div 
        v-for="segment in mergedSegments" 
        :key="segment.id"
        class="segment"
        :class="{ 'is-playing': isSegmentPlaying(segment) }"
      >
        <!-- 说话人信息 -->
        <div class="segment-header">
          <el-select 
            v-model="segment.speaker_id"
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
            v-for="(subSegment, index) in segment.subSegments"
            :key="index"
            class="sub-segment"
          >
            <div 
              class="segment-text"
              contenteditable="true"
              @input="(e) => handleContentChange(e, segment)"
            >
              <span
                v-for="(word, index) in splitTextWithTimestamps(subSegment)"
                :key="index"
                :class="{ 'word-highlight': isWordPlaying(word) }"
              >{{ word.text }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, watchEffect, computed } from 'vue'

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
  const date = new Date(seconds * 1000)
  return date.toISOString().substr(11, 8).replace(/^00:/, '')
}

// 处理说话人变更
const handleSpeakerChange = (speakerId, segment) => {
  const updatedSegment = {
    ...segment,
    speaker_id: speakerId
  }
  emit('speaker-change', speakerId, updatedSegment)
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

// 添加 speakerName 计算属性
const speakerName = computed(() => (speakerId) => {
  const speaker = props.speakers.find(s => s.id === speakerId)
  return speaker ? speaker.name : '未知说话人'
})

// 添加调试代码
watch([() => props.segments, () => props.speakers], () => {
  console.log('segments:', props.segments)
  console.log('speakers:', props.speakers)
})

// 添加合并段落的计算属性
const mergedSegments = computed(() => {
  const result = []
  let currentSegment = null
  const MIN_SEGMENT_LENGTH = 5 // 定义最小段落长度（按字数）

  props.segments.forEach(segment => {
    if (!currentSegment || currentSegment.speaker_id !== segment.speaker_id) {
      // 新说话人，创建新段落
      currentSegment = {
        ...segment,
        subSegments: [segment]
      }
      result.push(currentSegment)
    } else {
      // 检查是否需要合并短段落
      const lastSubSegment = currentSegment.subSegments[currentSegment.subSegments.length - 1]
      const isShortSegment = lastSubSegment.text.split(' ').length < MIN_SEGMENT_LENGTH
      
      if (isShortSegment) {
        // 合并短段落
        lastSubSegment.text += ' ' + segment.text
        lastSubSegment.end_time = segment.end_time
        if (segment.timestamps) {
          lastSubSegment.timestamps = [
            ...(lastSubSegment.timestamps || []),
            ...segment.timestamps
          ]
        }
      } else {
        // 添加新的子段落
        currentSegment.subSegments.push(segment)
      }
      
      // 更新合并后的段落信息
      currentSegment.text += ' ' + segment.text
      currentSegment.end_time = segment.end_time
      if (segment.timestamps) {
        currentSegment.timestamps = [
          ...(currentSegment.timestamps || []),
          ...segment.timestamps
        ]
      }
    }
  })

  return result
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

.sub-segment {
  margin-bottom: 8px;
}
.sub-segment:last-child {
  margin-bottom: 0;
}
</style> 