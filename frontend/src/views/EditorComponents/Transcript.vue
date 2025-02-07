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
                @click="handleWordClick(word, $event)"
                style="cursor: pointer"
                :data-subsegment-id="subSegment.subsegmentId"
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
import { ref, watch, watchEffect, computed, onMounted, nextTick } from 'vue'
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
const handleSpeakerChange = (updatedData) => {
  if (updatedData.batchUpdate) {
    // 批量更新：找到所有相同说话人的段落进行更新
    const oldSpeakerKey = mergedSegmentsCache.value.find(
      segment => segment.segmentId === updatedData.segmentId
    )?.speakerKey

    if (oldSpeakerKey) {
      // 创建一个包含所有需要更新的段落的数组
      const updatedSegments = mergedSegmentsCache.value.map(segment => {
        if (segment.speakerKey === oldSpeakerKey) {
          // 更新主段落
          return {
            ...segment,
            speakerKey: updatedData.speakerKey,
            speakerDisplayName: updatedData.speakerDisplayName,
            speaker_name: updatedData.speakerDisplayName,
            // 更新子段落
            subSegments: segment.subSegments.map(sub => ({
              ...sub,
              speakerKey: updatedData.speakerKey,
              speakerDisplayName: updatedData.speakerDisplayName,
              speaker_name: updatedData.speakerDisplayName
            }))
          }
        }
        return segment
      })

      // 更新缓存
      mergedSegmentsCache.value = updatedSegments

      // 发送批量更新事件给父组件
      emit('speaker-change', {
        ...updatedData,
        batchUpdate: true,
        oldSpeakerKey,
        updatedSegments: updatedSegments.filter(seg => seg.speakerKey === updatedData.speakerKey)
      })
    }
  } else {
    // 单独更新：只更新指定的段落
    const currentSegmentIndex = mergedSegmentsCache.value.findIndex(
      segment => segment.segmentId === updatedData.segmentId
    )

    if (currentSegmentIndex !== -1) {
      // 更新主段落
      const updatedMergedSegment = {
        ...mergedSegmentsCache.value[currentSegmentIndex],
        speakerKey: updatedData.speakerKey,
        speakerDisplayName: updatedData.speakerDisplayName,
        speaker_name: updatedData.speakerDisplayName,
        // 更新子段落
        subSegments: mergedSegmentsCache.value[currentSegmentIndex].subSegments.map(sub => ({
          ...sub,
          speakerKey: updatedData.speakerKey,
          speakerDisplayName: updatedData.speakerDisplayName,
          speaker_name: updatedData.speakerDisplayName
        }))
      }

      // 更新缓存
      mergedSegmentsCache.value = [
        ...mergedSegmentsCache.value.slice(0, currentSegmentIndex),
        updatedMergedSegment,
        ...mergedSegmentsCache.value.slice(currentSegmentIndex + 1)
      ]

      // 发送单个更新事件给父组件
      emit('speaker-change', updatedMergedSegment)
    }
  }
}

// 添加一个辅助函数来更新说话人信息
const updateSpeakerInfo = (segment, newSpeakerInfo) => {
  return {
    ...segment,
    speakerKey: newSpeakerInfo.speakerKey,
    speakerDisplayName: newSpeakerInfo.speakerDisplayName,
    speaker_name: newSpeakerInfo.speakerDisplayName,
    subSegments: segment.subSegments?.map(sub => ({
      ...sub,
      speakerKey: newSpeakerInfo.speakerKey,
      speakerDisplayName: newSpeakerInfo.speakerDisplayName,
      speaker_name: newSpeakerInfo.speakerDisplayName
    }))
  }
}

// 更新文本内容
const handleContentChange = (event, segment) => {
  // 获取当前编辑的元素
  const editedElement = event.target;
  const spans = editedElement.querySelectorAll('span');
  const updatedSubSegments = new Map();

  // 收集每个 subsegmentId 对应的文本
  spans.forEach(span => {
    const subsegmentId = span.getAttribute('data-subsegment-id');
    if (subsegmentId) {
      if (!updatedSubSegments.has(subsegmentId)) {
        updatedSubSegments.set(subsegmentId, []);
      }
      updatedSubSegments.get(subsegmentId).push(span.textContent);
    }
  });

  // 更新每个子段落的文本
  const updatedSegment = {
    ...segment,
    subSegments: segment.subSegments.map(sub => {
      const updatedTexts = updatedSubSegments.get(sub.subsegmentId);
      if (updatedTexts) {
        return {
          ...sub,
          text: updatedTexts.join('')
        };
      }
      return sub;
    })
  };

  // 更新主段落的文本（保持现有逻辑）
  updatedSegment.text = updatedSegment.subSegments.map(sub => sub.text).join('');

  // 添加日志记录
  console.log('段落更新数据:\n', JSON.stringify(updatedSegment, null, 2));

  emit('segment-update', updatedSegment);
}

// 优化 isSegmentPlaying 函数
const isSegmentPlaying = (segment) => {
  return props.currentTime >= segment.start_time && 
         props.currentTime <= segment.end_time
}

// 将文本按时间戳分割
const splitTextWithTimestamps = (segment) => {
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
    return [{ text: segment.text || '' }]
  }
  
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


watch(() => props.segments, (newVal) => {
    if (newVal.length > 0 && mergedSegmentsCache.value.length === 0) {
      nextTick(() => {
        const merged = mergeSegments(newVal, true)
        if (merged.length > 0) {
          // 发送所有合并后的数据
          console.log('首次更新数据:\n', JSON.stringify(merged, null, 2));
          
          // 更新所有segments
          merged.forEach(segment => {
            emit('segment-update', segment)
          })
        }
      })
    }
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

  const result = []
  let currentGroup = null
  
  rawSegments.forEach((segment, index) => {
    const currentKey = segment.speakerKey
    const groupKey = currentGroup?.speakerKey
    
    if (!currentGroup || groupKey !== currentKey) {
      if (currentGroup) {
        result.push(currentGroup)
      }

      // 使用第一个子段落的 segmentId 或生成新的
      const segmentId = segment.segmentId || `${currentKey}_${nanoid(6)}`
      
      // 保留更多原始数据
      currentGroup = {
        segmentId,
        speakerKey: currentKey,
        speakerDisplayName: segment.speakerDisplayName,
        speaker_name: segment.speaker_name,  // 保留 speaker_name
        start_time: segment.start_time,
        end_time: segment.end_time,
        text: segment.text,
        timestamps: segment.timestamps,
        subSegments: [{
          ...segment,
          segmentId,
          subsegmentId: segment.subsegmentId || `${segmentId}_sub_${nanoid(6)}`,
          text: segment.text,
          timestamps: segment.timestamps,
          speakerKey: currentKey,
          speakerDisplayName: segment.speakerDisplayName,
          speaker_name: segment.speaker_name
        }]
      }
    } else {
      currentGroup.subSegments.push({
        ...segment,
        segmentId: currentGroup.segmentId,
        subsegmentId: segment.subsegmentId || `${currentGroup.segmentId}_sub_${nanoid(6)}`,
        text: segment.text,
        timestamps: segment.timestamps,
        speakerKey: currentKey,
        speakerDisplayName: segment.speakerDisplayName,
        speaker_name: segment.speaker_name
      })
      // 更新结束时间
      currentGroup.end_time = segment.end_time

      // 动态更新主段落的 text，拼接所有子段落的文本
      currentGroup.text = currentGroup.subSegments.map(sub => sub.text).join('')
    }
  })
  
  if (currentGroup) {
    result.push(currentGroup)
  }

  return result
}

// 3. 修改计算属性，使用缓存的结果
const mergedSegments = computed(() => {
  // 如果有缓存，直接返回
  if (mergedSegmentsCache.value.length > 0) {
    return mergedSegmentsCache.value
  }

  const result = mergeSegments(props.segments, !mergedSegmentsCache.value.length)
  
  // 更新缓存
  mergedSegmentsCache.value = result
  
  return result
})

// 添加对 segments 的深度监听
watch(() => props.segments, (newSegments) => {
  // 检查是否有说话人信息变化
  const hasChanges = newSegments.some((segment, index) => {
    const cached = mergedSegmentsCache.value.find(m => 
      m.subSegments.some(sub => sub.subsegmentId === segment.subsegmentId)
    )
    return !cached || 
           cached.speakerKey !== segment.speakerKey || 
           cached.speakerDisplayName !== segment.speakerDisplayName
  })

  if (hasChanges) {
    console.log('检测到说话人变化，清除缓存')
    mergedSegmentsCache.value = []
  }
}, { deep: true })

// 4. 添加新的方法
const handleSegmentClick = (segment) => {
  if (segment && segment.start_time !== undefined) {
    // 更新当前选中的段落
    mergedSegmentsCache.value = mergedSegmentsCache.value.map(s => ({
      ...s,
      isSelected: s.segmentId === segment.segmentId
    }))
    emit('timeupdate', segment.start_time)
  }
}

// 处理单词点击
const handleWordClick = (word, event) => {
  event.stopPropagation() // 防止触发段落的点击事件
  if (word && word.start !== undefined) {
    // 找到并更新当前选中的段落
    const parentSegment = mergedSegmentsCache.value.find(segment => 
      segment.subSegments.some(sub => 
        splitTextWithTimestamps(sub).some(w => w === word)
      )
    )
    if (parentSegment) {
      mergedSegmentsCache.value = mergedSegmentsCache.value.map(s => ({
        ...s,
        isSelected: s.segmentId === parentSegment.segmentId
      }))
    }
    emit('timeupdate', word.start)
  }
}

// 暴露 mergedSegments 给父组件
defineExpose({
  mergedSegments
})

// 添加初始化检查
onMounted(() => {
  if (props.segments && props.segments.length > 0) {
    mergedSegments.value // 触发首次合并
  }
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

.segment-text span {
  cursor: pointer;
  user-select: none;
}

.segment-text span.current-position {
  background-color: var(--el-color-primary-light-8);
  border-radius: 2px;
  padding: 0 2px;
}

.segment-text span:hover {
  background-color: var(--el-color-primary-light-9);
}
</style> 