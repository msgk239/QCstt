<template>
  <div class="transcript" ref="transcriptRef">
    <!-- 转写内容段落列表 -->
    <div class="segments">
      <div 
        v-for="segment in mergedSegments" 
        :key="segment.segmentId"
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
            :manager-id="segment.segmentId"
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
            <template v-for="(subSegment, subIndex) in segment.subSegments" :key="subSegment.subsegmentId">
              <span
                v-for="(word, wordIndex) in splitTextWithTimestamps(subSegment)"
                :key="`${subSegment.subsegmentId}-${wordIndex}`"
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
import { nanoid } from 'nanoid'

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
  console.log('Transcript 收到说话人变更:', updatedSegment)
  
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
watch(() => props.segments, (newVal) => {
    console.log('segments 发生变化:', {
        segments: newVal,
        firstThreeSegments: newVal.slice(0, 3).map(s => ({
            speakerKey: s.speakerKey,
            text: s.text
        }))
    })
}, { deep: true })

// 1. 添加一个用于存储合并后段落的 ref
const mergedSegmentsCache = ref([])

// 1. 生成 segmentId 的方法
const generateSegmentId = (segment, isFirstMerge = false) => {
  // 如果没有 segmentId 就生成新的，保持向后兼容
  if (!segment.segmentId || isFirstMerge) {
    return `${segment.speakerKey}_${nanoid(6)}`
  }
  return segment.segmentId
}

// 2. 纯合并逻辑
const mergeSegments = (rawSegments, isFirstMerge = false) => {
  console.log('开始合并段落:', {
    rawSegmentsCount: rawSegments.length,
    firstThreeRawSegments: rawSegments.slice(0, 3).map(s => ({
      speakerKey: s.speakerKey,
      text: s.text?.slice(0, 20) // 只显示前20个字符
    }))
  })

  const result = []
  let currentGroup = null
  
  rawSegments.forEach((segment, index) => {
    const currentKey = segment.speakerKey
    const groupKey = currentGroup?.speakerKey
    
    if (!currentGroup || groupKey !== currentKey) {
      if (currentGroup) {
        result.push(currentGroup)
      }
      
      // 创建新组时记录日志
      console.log('创建新组:', {
        index,
        speakerKey: currentKey,
        previousGroupKey: groupKey
      })

      currentGroup = {
        // 原始字段（不变）
        speaker_id: segment.speaker_id,
        speaker_name: segment.speaker_name,
        
        // 前端使用的字段（可变）
        speakerKey: segment.speakerKey,
        speakerDisplayName: segment.speakerDisplayName,
        color: segment.color,
        
        // 使用独立的方法生成父段落的 segmentId
        segmentId: generateSegmentId(segment, isFirstMerge),
        
        // 时间信息（可变）
        start_time: segment.start_time,
        end_time: segment.end_time,
        
        // 子段落信息，保留原始段落的 subsegmentId
        subSegments: [{
          subsegmentId: segment.subsegmentId,
          speakerKey: segment.speakerKey,
          text: segment.text || '',
          start_time: segment.start_time,
          end_time: segment.end_time,
          timestamps: segment.timestamps
        }]
      }
    } else {
      // 添加到当前组时记录日志
      console.log('添加到现有组:', {
        index,
        speakerKey: currentKey,
        subSegmentsCount: currentGroup.subSegments.length
      })
      
      currentGroup.subSegments.push({
        subsegmentId: segment.subsegmentId,
        speakerKey: segment.speakerKey,
        text: segment.text || '',
        start_time: segment.start_time,
        end_time: segment.end_time,
        timestamps: segment.timestamps
      })
      currentGroup.text = currentGroup.subSegments.map(sub => sub.text).join('\n').trim()
      currentGroup.end_time = segment.end_time  // 更新合并后的 end_time
    }
  })
  
  // 添加最后一组
  if (currentGroup) {
    result.push(currentGroup)
  }

  console.log('合并完成:', {
    resultCount: result.length,
    firstGroupInfo: result[0] ? {
      speakerKey: result[0].speakerKey,
      subSegmentsCount: result[0].subSegments.length
    } : null
  })
  
  return result
}

// 3. 修改计算属性，使用缓存的结果
const mergedSegments = computed(() => {
    console.log('mergedSegments computed 触发:', {
        segments: props.segments,
        cache: mergedSegmentsCache.value,
        isEqual: props.segments === mergedSegmentsCache.value
    })
    
    if (!props.segments) return []
    
    if (props.segments !== mergedSegmentsCache.value) {
        console.log('需要重新合并段落，原因:', {
            oldCache: mergedSegmentsCache.value,
            newSegments: props.segments,
            diff: props.segments.map((s, i) => ({
                index: i,
                segmentId: s.segmentId,
                speakerKey: s.speakerKey,
                isDifferent: s !== mergedSegmentsCache.value?.[i]
            }))
        })
        
        const isFirstMerge = !mergedSegmentsCache.value.length
        mergedSegmentsCache.value = mergeSegments(props.segments, isFirstMerge)
        
        console.log('合并后的结果:', {
            newCache: mergedSegmentsCache.value,
            segmentCount: mergedSegmentsCache.value.length
        })
    } else {
        console.log('使用缓存的合并结果')
    }
    
    return mergedSegmentsCache.value
})

// 4. 添加新的方法
const handleSegmentClick = (segment) => {
  const updatedSegments = props.segments.map(s => ({
    ...s,
    isSelected: s.segmentId === segment.segmentId
  }))
  emit('segment-select', updatedSegments)
}

// 暴露 mergedSegments 给父组件
defineExpose({
  mergedSegments
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

.segment.is-selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}
</style> 