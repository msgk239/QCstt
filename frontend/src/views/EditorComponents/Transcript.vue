<template>
  <div class="transcript">
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
        <div 
          class="segment-content"
          contenteditable="true"
          @input="(e) => handleContentChange(e, segment)"
          v-html="segment.text"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watchEffect } from 'vue'

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

// 判断当前段落是否正在播放
const isSegmentPlaying = (segment) => {
  return props.currentTime >= segment.start_time && 
         props.currentTime <= segment.end_time
}

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
  const updatedSegment = {
    ...segment,
    text: event.target.innerHTML
  }
  emit('segment-update', updatedSegment)
}

// 添加调试代码
watchEffect(() => {
  console.log('segments:', props.segments)
  console.log('speakers:', props.speakers)
})
</script>

<style scoped>
.transcript {
  padding: 20px;
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
  background: #f5f7fa;
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

.segment-content:focus {
  background: #f5f7fa;
  border-radius: 4px;
}
</style> 