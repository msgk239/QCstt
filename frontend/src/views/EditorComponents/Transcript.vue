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
import { ref, watch, watchEffect, computed, onMounted } from 'vue'
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
  console.log('内容变更事件:', {
    newText: event.target.textContent,
    segmentId: segment.segmentId,
    originalText: segment.text
  })
  
  const text = event.target.textContent
  const updatedSegment = {
    ...segment,
    text: text,
  }
  console.log('准备发送 segment-update:', {
    segment,
    segmentId: updatedSegment.segmentId,
    isFirstMerge: false
  })
  emit('segment-update', updatedSegment)
  console.log('已发送 segment-update')
}

// 优化 isSegmentPlaying 函数
const isSegmentPlaying = (segment) => {
  return props.currentTime >= segment.start_time && 
         props.currentTime <= segment.end_time
}

// 将文本按时间戳分割
const splitTextWithTimestamps = (segment) => {
  console.log('splitTextWithTimestamps 详细输入:', {
    segment,
    hasTimestamps: !!segment?.timestamps,
    hasText: !!segment?.text,
    textLength: segment?.text?.length,
    timestampsLength: segment?.timestamps?.length,
    segmentContent: segment?.text,
    firstTimestamp: segment?.timestamps?.[0]
  })

  // 添加数据完整性检查
  if (!segment || typeof segment !== 'object') {
    console.warn('segment 对象无效:', segment)
    return [{ text: '' }]
  }

  if (!segment.timestamps || !segment.text) {
    console.warn('缺少必要的数据:', {
      text: segment.text,
      hasTimestamps: !!segment.timestamps
    })
    // 如果只有文本没有时间戳，至少显示文本
    return [{ text: segment.text || '' }]
  }
  
  const text = segment.text
  const timestamps = segment.timestamps
  const minLength = Math.min(text.length, timestamps.length)
  
  const result = Array.from({ length: minLength }, (_, index) => ({
    text: text[index],
    start: timestamps[index].start,
    end: timestamps[index].end
  }))

  console.log('splitTextWithTimestamps 处理结果:', {
    inputTextLength: text.length,
    inputTimestampsLength: timestamps.length,
    outputLength: result.length,
    sampleOutput: result.slice(0, 3)
  })
  
  return result
}

// 判断单个词是否正在播放
const lastLogTime = ref(0)
const isWordPlaying = (word) => {
  const now = Date.now()
  if (now - lastLogTime.value > 1000) { // 每秒最多记录一次
    console.log('检查单词播放状态:', {
      word,
      currentTime: props.currentTime,
      isPlaying: props.currentTime >= (word.start - 0.05) && 
                 props.currentTime <= (word.end + 0.05)
    })
    lastLogTime.value = now
  }
  
  if (!word.start || !word.end) return false
  const buffer = 0.05
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

// 批量生成逻辑
const generateSegmentIds = (segments, isFirstMerge = false) => {
  return segments.map(segment => {
    if (!segment.segmentId || isFirstMerge) {
      return {
        ...segment,
        segmentId: `${segment.speakerKey}_${nanoid(6)}`
      }
    }
    return segment
  })
}

// 2. 纯合并逻辑
const mergeSegments = (rawSegments, isFirstMerge = false) => {
  if (!rawSegments || rawSegments.length === 0) {
    console.log('跳过合并：rawSegments为空')
    return []
  }

  console.log('开始合并段落:', {
    rawSegmentsCount: rawSegments.length,
    isFirstMerge,
    firstThreeRawSegments: rawSegments.slice(0, 3).map(s => ({
      speakerKey: s.speakerKey,
      segmentId: s.segmentId,
      subsegmentId: s.subsegmentId,
      text: s.text?.slice(0, 20),
      hasTimestamps: !!s.timestamps,
      timestampsCount: s.timestamps?.length
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

      const segmentId = `${currentKey}_${nanoid(6)}`
      
      // 保留更多原始数据
      currentGroup = {
        segmentId,
        speakerKey: currentKey,
        speakerDisplayName: segment.speakerDisplayName,
        start_time: segment.start_time,
        end_time: segment.end_time,
        text: segment.text, // 保留原始文本
        timestamps: segment.timestamps, // 保留原始时间戳
        subSegments: [{
          ...segment,
          segmentId,
          subsegmentId: segment.subsegmentId,
          text: segment.text,
          timestamps: segment.timestamps
        }]
      }

      console.log('子段落数据:', {
        segmentId,
        subsegmentId: segment.subsegmentId,
        text: segment.text?.slice(0, 20),
        hasTimestamps: !!segment.timestamps,
        timestampsLength: segment.timestamps?.length,
        rawSegment: segment
      })

    } else {
      currentGroup.subSegments.push({
        ...segment,
        segmentId: currentGroup.segmentId,
        subsegmentId: segment.subsegmentId,
        text: segment.text,
        timestamps: segment.timestamps
      })
      // 更新结束时间
      currentGroup.end_time = segment.end_time
    }
  })
  
  if (currentGroup) {
    result.push(currentGroup)
  }

  return result
}

// 3. 修改计算属性，使用缓存的结果
const mergedSegments = computed(() => {
  // 使用缓存避免重复计算
  if (mergedSegmentsCache.value.length > 0 && !props.segments.some(s => !s.segmentId)) {
    return mergedSegmentsCache.value
  }

  const isFirstMerge = !mergedSegmentsCache.value.length
  const result = mergeSegments(props.segments, isFirstMerge)
  
  // 缓存结果
  mergedSegmentsCache.value = result
  
  return result
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

// 添加初始化检查
onMounted(() => {
  console.log('Transcript 组件挂载完成')
  if (props.segments && props.segments.length > 0) {
    console.log('Transcript 初始化合并开始:', {
      segmentsCount: props.segments.length,
      firstThreeSegments: props.segments.slice(0, 3).map(s => ({
        segmentId: s.segmentId,
        speakerKey: s.speakerKey,
        subsegmentId: s.subsegmentId
      }))
    })
    const value = mergedSegments.value // 触发首次合并
    console.log('Transcript 初始化合并完成:', {
      resultCount: value.length,
      firstThreeResults: value.slice(0, 3).map(s => ({
        segmentId: s.segmentId,
        speakerKey: s.speakerKey,
        subSegmentsCount: s.subSegments.length
      }))
    })
  }
})

// 3. 在模板渲染前添加调试日志
watchEffect(() => {
  console.log('模板渲染数据状态:', {
    mergedSegmentsLength: mergedSegments.value?.length,
    firstSegmentInfo: mergedSegments.value?.[0] ? {
      segmentId: mergedSegments.value[0].segmentId,
      hasSubSegments: !!mergedSegments.value[0].subSegments,
      subSegmentsLength: mergedSegments.value[0].subSegments?.length,
      firstSubSegmentText: mergedSegments.value[0].subSegments?.[0]?.text?.slice(0, 50)
    } : null
  })
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