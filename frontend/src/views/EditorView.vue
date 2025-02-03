<template>
  <div class="editor-view">
    <!-- 顶部标题和工具栏 -->
    <div class="editor-header">
      <h1>{{ formatDisplayName(fileName) }}</h1>
      <div class="header-tools">
        <ExportToolbar />
        <ShareToolbar />
        <StyleTemplateToolbar />
        <div class="divider"></div>
        <AutoSaveToolbar
          v-model:autoSave="autoSaveEnabled"
          v-model:saveInterval="autoSaveInterval"
          v-model:maxVersions="maxVersions"
          :saving="saving"
          :lastSaveTime="lastSaveTime"
        />
        <VersionHistoryToolbar />
      </div>
    </div>

    <!-- 编辑工具栏 -->
    <div class="edit-toolbar">
      <UndoRedoToolbar />
      <EditToolbar 
        @format-apply="applyFormat"
        @note-add="addNote"
        @timestamp-insert="insertTimestamp"
      />
      <NoteToolbar />
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <Transcript 
        ref="transcriptRef"
        :segments="segments"
        :speakers="speakers"
        :currentTime="currentTime"
        @segment-update="handleSegmentUpdate"
        @speaker-change="handleSpeakerChange"
        @timeupdate="handleTimeUpdate"
        @segment-select="handleSegmentSelect"
      />
    </div>

    <!-- 底部固定播放器 -->
    <div class="player-container">
      <AudioPlayer 
        ref="audioPlayerRef"
        :currentTime="currentTime"
        :duration="duration"
        :playing="playing"
        :playbackRate="playbackRate"
        @play="togglePlay"
        @seek="seekTo"
        @speed-change="handleSpeedChange"
        @timeupdate="handleTimeUpdate"
      />
    </div>

    <!-- 对话框组件 -->
    <ReplaceDialog v-model="replaceDialogVisible" />
    <HotwordsDialog v-model="hotwordsDialogVisible" />
    <SpeedMenuDialog v-model="speedMenuVisible" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getFileDetail, formatFileData, getAudioFile, fileApi } from '@/api/modules/file'
import { useFileStore } from '@/stores/fileStore'
import { nanoid } from 'nanoid'

// 获取 store 实例
const fileStore = useFileStore()

// 导入所有组件
import AudioPlayer from './EditorComponents/AudioPlayer.vue'
import Transcript from './EditorComponents/Transcript.vue'
import EditToolbar from './EditorComponents/EditToolbar.vue'
import ReplaceDialog from './EditorComponents/ReplaceDialog.vue'
import HotwordsDialog from './EditorComponents/HotwordsDialog.vue'
import SpeedMenuDialog from './EditorComponents/SpeedMenuDialog.vue'
import AutoSaveToolbar from './EditorComponents/AutoSaveToolbar.vue'
import ExportToolbar from './EditorComponents/ExportToolbar.vue'
import NoteToolbar from './EditorComponents/NoteToolbar.vue'
import ShareToolbar from './EditorComponents/ShareToolbar.vue'
import StyleTemplateToolbar from './EditorComponents/StyleTemplateToolbar.vue'
import UndoRedoToolbar from './EditorComponents/UndoRedoToolbar.vue'
import VersionHistoryToolbar from './EditorComponents/VersionHistoryToolbar.vue'

// 导入事件总线
import { editorBus, EVENT_TYPES } from './EditorComponents/eventBus'

// 路由
const route = useRoute()

// 状态
const file = ref(null)
const segments = ref([])
const speakers = ref([
  {
    speakerKey: 'speaker_0',
    speakerDisplayName: '说话人 1',
    color: '#409EFF',
    speaker_id: 'speaker_0',
    speaker_name: '说话人 1'
  },
  {
    speakerKey: 'speaker_1',
    speakerDisplayName: '说话人 2',
    color: '#F56C6C',
    speaker_id: 'speaker_1',
    speaker_name: '说话人 2'
  }
])
const saving = ref(false)

// 对话框状态
const replaceDialogVisible = ref(false)
const hotwordsDialogVisible = ref(false)
const speedMenuVisible = ref(false)

// 音频播放器相关
const audioPlayerRef = ref(null)
const playing = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1)

// 音频相关
const audio = ref(new Audio())

// 添加自动保存相关的状态
const autoSaveEnabled = ref(true)
const autoSaveInterval = ref(5)
const maxVersions = ref(10)
const lastSaveTime = ref(null)
// 添加定时器变量
let autoSaveTimer = null

// 初始化音频
const initAudio = async () => {
  try {
    const blob = await getAudioFile(route.params.id)  // 现在直接返回 blob
    console.log('Audio blob:', {
      type: blob.type,
      size: blob.size
    })
    
    if (!(blob instanceof Blob)) {
      console.error('Response is not a Blob:', blob)
      throw new Error('Invalid response data type')
    }
    
    // 在设置 src 之前先移除旧的 URL
    if (audio.value.src) {
      URL.revokeObjectURL(audio.value.src)
    }
    
    // 确保 blob 类型正确
    const audioBlob = blob.type.includes('audio/') 
      ? blob 
      : new Blob([blob], { type: 'audio/mpeg' })  // 默认使用 mp3 格式
    
    const audioUrl = URL.createObjectURL(audioBlob)
    
    // 设置音频源
    audio.value.src = audioUrl
    
    // 添加时间更新监听
    audio.value.addEventListener('timeupdate', () => {
      currentTime.value = audio.value.currentTime
    })
    
    // 添加加载事件监听
    const loadPromise = new Promise((resolve, reject) => {
      audio.value.addEventListener('loadedmetadata', () => {
        console.log('Audio loaded:', {
          audioDuration: audio.value.duration,
          fileDuration: duration.value
        })
        // 如果文件数据中没有时长，才使用音频时长
        if (!duration.value) {
          duration.value = audio.value.duration
        }
        resolve()
      })
      
      audio.value.addEventListener('error', (e) => {
        console.error('Audio load failed:', e)
        reject(new Error('Failed to load audio'))
      })
    })
    
    // 等待音频加载完成
    await loadPromise
    
    audio.value.addEventListener('loadedmetadata', () => {
      console.log('音频加载完成:', {
        duration: audio.value.duration,
        currentDuration: duration.value
      })
      duration.value = audio.value.duration
    })
    
  } catch (error) {
    console.error('加载音频失败:', error)
    ElMessage.error('音频加载失败')
    throw error
  }
}

// 方法
const handleSave = async () => {
  console.log('开始保存:', {
    currentSegments: segments.value,
    currentSpeakers: speakers.value
  })
  
  saving.value = true
  try {
    // 确保数据存在且是数组
    if (!Array.isArray(segments.value) || !Array.isArray(speakers.value)) {
      console.error('数据格式错误:', {
        segments: segments.value,
        speakers: speakers.value
      })
      throw new Error('数据格式错误')
    }

    const saveData = {
      segments: segments.value.map(segment => {
        // 确保每个 segment 都有必要的属性
        const safeSegment = {
          speaker_id: segment.speaker_id || '',
          speaker_name: segment.speakerDisplayName || '',
          speakerKey: segment.speakerKey || '',
          speakerDisplayName: segment.speakerDisplayName || '',
          start_time: segment.start_time || 0,
          end_time: segment.end_time || 0,
          text: segment.text || '',  // 添加文本内容
          timestamps: segment.timestamps || [], // 添加时间戳数组
          subSegments: segment.subSegments || []
        }
        return safeSegment
      }),
      speakers: speakers.value.map(speaker => ({
        id: speaker.speakerKey || '',
        name: speaker.speakerDisplayName || ''
      }))
    }
    
    console.log('准备发送到后端的数据:', saveData)
    
    // 使用 saveVersion 接口
    const response = await fileApi.saveVersion(route.params.id, {
      content: saveData,
      type: 'manual',
      note: '手动保存'
    })
    
    if (response.code === 200) {
      lastSaveTime.value = new Date()
      console.log('保存成功')
      ElMessage.success('保存成功')
      // 触发版本保存成功事件
      editorBus.emit(EVENT_TYPES.VERSION_SAVED, response.data)
    } else {
      throw new Error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleSegmentUpdate = (updatedSegments) => {
  // 处理批量更新
  if (Array.isArray(updatedSegments)) {
    console.log('处理批量更新:', {
      updatedSegmentsCount: updatedSegments.length
    })

    // 如果是合并后的结果（包含 subSegments），直接替换
    if (updatedSegments[0]?.subSegments) {
      segments.value = updatedSegments
      return
    }
    
    // 原有的更新逻辑保持不变
    const updatedSegmentIds = new Set(updatedSegments.map(s => s.segmentId))
    
    segments.value = segments.value.map(segment => {
      if (updatedSegmentIds.has(segment.segmentId)) {
        const updatedSegment = updatedSegments.find(s => s.segmentId === segment.segmentId)
        return {
          ...segment,
          ...updatedSegment
        }
      }
      return segment
    })
    
    // 添加新段落（如果有）
    const newSegments = updatedSegments.filter(s => !updatedSegmentIds.has(s.segmentId))
    if (newSegments.length > 0) {
      console.log('添加新段落:', {
        count: newSegments.length
      })
      segments.value = [...segments.value, ...newSegments]
    }
  } 
  // 处理单个段落更新（保持兼容）
  else {
    const index = segments.value.findIndex(s => s.segmentId === updatedSegments.segmentId)
    if (index > -1) {
      segments.value[index] = {
        ...segments.value[index],
        ...updatedSegments
      }
    }
  }
}

// 音频播放器相关方法
const handleTimeUpdate = (time) => {
  if (audio.value) {
    audio.value.currentTime = time
    currentTime.value = time
    // 只有在当前正在播放时，点击才会继续播放
    if (playing.value) {
      // 如果已经在播放，就继续播放
      audio.value.play()
    }
  }
}

const togglePlay = () => {
  if (audio.value) {
    if (playing.value) {
      audio.value.pause()
    } else {
      audio.value.play()
    }
    playing.value = !playing.value
  }
}

const seekTo = (time) => {
  if (audio.value) {
    audio.value.currentTime = time
    currentTime.value = time
  }
}

const handleSpeedChange = (speed) => {
  playbackRate.value = speed
  audio.value.playbackRate = speed
}

// 从完整文件名中提取原始文件名
const getOriginalFilename = (fullname) => {
  if (!fullname) return ''
  // 移除时间戳前缀 (20250109_141133_)
  return fullname.split('_').slice(2).join('_')
}

// 修改自动保存逻辑
const startAutoSave = () => {
  if (autoSaveEnabled.value) {
    // 先清除已存在的定时器
    if (autoSaveTimer) {
      clearInterval(autoSaveTimer)
    }
    autoSaveTimer = setInterval(handleSave, autoSaveInterval.value * 60 * 1000)
  }
}

// 监听自动保存设置变化
watch([autoSaveEnabled, autoSaveInterval], () => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
  startAutoSave()
})

// 提取加载文件数据的方法
const loadFileData = async () => {
  console.log('开始加载文件数据')
  const response = await getFileDetail(route.params.id)
  const formattedData = formatFileData(response)
  file.value = formattedData
  
  // 初始化 segments
  segments.value = formattedData.segments.map((segment, index) => {
    // 确保基本字段存在
    const safeSegment = {
      ...segment,  // 包含了所有原始字段
      speakerKey: segment.speaker_id || `speaker_${index}`,
      speakerDisplayName: segment.speaker_name || `说话人 ${index + 1}`,
      color: segment.color || '#409EFF',
      isSelected: false,
      subsegmentId: `${segment.speaker_id || `speaker_${index}`}-${segment.start_time || 0}-${segment.end_time || 0}`
    }
    
    return safeSegment
  })

  // 只在第一次加载时初始化 speakers
  if (!speakers.value.length) {
    const colors = ['#409EFF', '#F56C6C', '#67C23A', '#E6A23C', '#909399']
    speakers.value = formattedData.speakers.map((speaker, index) => ({
      speakerKey: speaker.id || `speaker_${index}`,
      speakerDisplayName: speaker.name || `说话人 ${index + 1}`,
      color: colors[index % colors.length],
      speaker_id: speaker.id || `speaker_${index}`,
      speaker_name: speaker.name || `说话人 ${index + 1}`
    }))
  }
  
  duration.value = formattedData.duration || 0
}

// 生命周期钩子
onMounted(async () => {
  try {
    await loadFileData()
    await initAudio()
    
    // 监听版本保存事件
    editorBus.on(EVENT_TYPES.SAVE_VERSION, async () => {
      try {
        // 先保存当前内容
        await handleSave()
        
        // 确保数据存在
        if (!segments.value || !speakers.value) {
          throw new Error('数据不完整')
        }
        
        // 保存版本
        const versionData = {
          segments: segments.value.map(segment => ({
            ...segment,
            subSegments: segment.subSegments || []
          })),
          speakers: speakers.value.map(speaker => ({
            ...speaker
          })),
          timestamp: new Date()
        }
        
        const response = await fileApi.saveVersion(route.params.id, versionData)
        
        if (response.code === 200) {
          // 触发保存完成事件
          editorBus.emit(EVENT_TYPES.VERSION_SAVED, response.data)
          ElMessage.success('版本保存成功')
        } else {
          throw new Error(response.message || '保存版本失败')
        }
      } catch (error) {
        console.error('保存版本失败:', error)
        ElMessage.error(error.message || '保存版本失败')
      }
    })
    
    // 监听版本加载事件
    editorBus.on(EVENT_TYPES.LOAD_VERSION, async (version) => {
      try {
        if (version.content) {
          if (version.mode === 'preview') {
            // TODO: 实现预览模式
            ElMessage.info('预览功能开发中')
          } else if (version.mode === 'restore') {
            // 还原版本
            segments.value = version.content.segments
            speakers.value = version.content.speakers
            
            // 保存还原后的状态
            await handleSave()
            ElMessage.success('还原版本成功')
          }
        }
      } catch (error) {
        console.error('加载版本失败:', error)
        ElMessage.error('加载版本失败')
      }
    })
  } catch (error) {
    console.error('Failed to load file:', error)
    ElMessage.error('加载失败')
  }
  startAutoSave()
})

onUnmounted(() => {
  if(autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
  // 清理音频资源
  if (audio.value.src) {
    URL.revokeObjectURL(audio.value.src)
  }
  audio.value = null
})

const formatDisplayName = (fullName) => {
  if (!fullName) return ''
  const match = fullName.match(/\d{8}_\d{6}_(.+)/)
  return match ? match[1] : fullName
}

const handleBatchReplace = (nameMapping) => {
  speakers.value = speakers.value.map(speaker => {
    if (nameMapping[speaker.speakerDisplayName]) {  // 使用 speakerDisplayName
      const updatedSpeaker = {
        ...speaker,
        speakerDisplayName: nameMapping[speaker.speakerDisplayName],  // 更新显示名字
        original_name: speaker.speakerDisplayName
      }
      return updatedSpeaker
    }
    return speaker
  })

  segments.value = segments.value.map(segment => {
    const speaker = speakers.value.find(s => s.speakerKey === segment.speakerKey)  // 使用 speakerKey
    if (speaker && nameMapping[speaker.speakerDisplayName]) {  // 使用 speakerDisplayName
      const updatedSegment = {
        ...segment,
        speakerDisplayName: speaker.speakerDisplayName,  // 使用显示名字
        speakerKey: speaker.speakerKey  // 使用 speakerKey
      }
      return updatedSegment
    }
    return segment
  })
}

const handleReset = () => {
  // 重置说话人列表
  speakers.value = speakers.value.map(speaker => ({
    ...speaker,
    speakerDisplayName: speaker.speaker_name,    // 使用原始名字
    speakerKey: speaker.speaker_id              // 使用原始ID
  }))
  
  // 同时重置所有段落
  segments.value = segments.value.map(segment => ({
    ...segment,
    speakerDisplayName: segment.speaker_name,  // 恢复原始名字作为显示名字
    speakerKey: segment.speaker_id            // 恢复原始ID作为key
  }))
  
  ElMessage.success('重置成功')
}

const currentSpeaker = computed(() => {
  if (!segments.value.length) return null
  const selectedSegment = segments.value.find(s => s.isSelected)
  if (!selectedSegment) return null
  
  const speaker = speakers.value.find(s => s.speakerKey === selectedSegment.speakerKey)
  if (!speaker) return null

  return {
    ...speaker,
    speaker_name: speaker.speaker_name,  // 使用原始名字
    speakerDisplayName: speaker.speakerDisplayName  // 使用当前显示名字
  }
})

const handleSegmentSelect = (updatedSegments) => {
  // 确保更新选中状态时保持原始字段不变
  segments.value = updatedSegments.map(segment => ({
    ...segment,
    speaker_id: segment.speaker_id,
    speaker_name: segment.speaker_name,
    speakerDisplayName: segment.speakerDisplayName || segment.speaker_name,
    speakerKey: segment.speakerKey || segment.speaker_id
  }))
}

const handleSpeakerChange = (updatedSegment) => {
  if (updatedSegment.batchUpdate) {
    console.log('处理批量说话人更新:', {
      oldSpeakerKey: updatedSegment.oldSpeakerKey,
      newSpeakerKey: updatedSegment.speakerKey,
      speakerDisplayName: updatedSegment.speakerDisplayName,
      updatedSegmentsCount: updatedSegment.updatedSegments?.length
    })
    
    // 批量更新所有相同说话人的段落
    segments.value = segments.value.map(segment => {
      if (segment.speakerKey === updatedSegment.oldSpeakerKey) {
        return {
          ...segment,
          speakerKey: updatedSegment.speakerKey,
          speakerDisplayName: updatedSegment.speakerDisplayName,
          speaker_name: updatedSegment.speakerDisplayName
        }
      }
      return segment
    })
  } else {
    const index = segments.value.findIndex(s => s.segmentId === updatedSegment.segmentId)
    
    if (index > -1) {
      segments.value = segments.value.map(segment => {
        if (segment.segmentId === updatedSegment.segmentId) {
          return {
            ...segment,
            speakerKey: updatedSegment.speakerKey,
            speakerDisplayName: updatedSegment.speakerDisplayName,
            speaker_name: updatedSegment.speakerDisplayName
          }
        }
        return segment
      })
    } else {
      console.warn('未找到要更新的段落:', updatedSegment.segmentId)
    }
  }
}

// 修改获取说话人名字的函数
const getSpeakerName = (segment) => {
  // 只使用 speakerDisplayName
  return segment.speakerDisplayName
}
</script>

<style scoped>
.editor-view {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  position: relative;
}

.editor-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
  flex-shrink: 0;  /* 防止标题被挤压 */
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  padding-bottom: 120px;
  min-height: calc(100vh - 200px);
}

.player-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
  padding: 16px 24px;
  height: 80px;
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.edit-toolbar {
  padding: 8px 24px;
  border-bottom: 1px solid #eee;
  background: #fff;
  display: flex;
  align-items: center;
  gap: 16px;
}

.divider {
  width: 1px;
  height: 24px;
  background-color: #dcdfe6;
  margin: 0 8px;
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
    padding-bottom: 100px;
  }
  
  .player-container {
    padding: 12px 16px;
    height: 70px;
  }
}
</style>

