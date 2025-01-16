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
import { getFileDetail, formatFileData, getAudioFile } from '@/api/modules/file'
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
    const saveData = {
      segments: segments.value.map(segment => ({
        speaker_id: segment.speaker_id,
        speaker_name: segment.speakerDisplayName,
        speakerKey: segment.speakerKey,
        speakerDisplayName: segment.speakerDisplayName,
        start_time: segment.start_time,
        end_time: segment.end_time,
        subSegments: segment.subSegments.map(sub => ({
          subsegmentId: sub.subsegmentId,
          text: sub.text,
          start_time: sub.start_time,
          end_time: sub.end_time,
          timestamps: sub.timestamps
        }))
      })),
      speakers: speakers.value.map(speaker => ({
        id: speaker.speakerKey,
        name: speaker.speakerDisplayName
      }))
    }
    
    console.log('准备发送到后端的数据:', saveData)
    
    await fileStore.saveFile(route.params.id, saveData)
    lastSaveTime.value = new Date()
    
    console.log('保存成功')
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSegmentUpdate = (updatedSegments) => {
  if (Array.isArray(updatedSegments)) {
    segments.value = updatedSegments.map((segment, index) => {
      // 确保基本字段存在
      const safeSegment = {
        ...segment,
        speaker_id: segment.speaker_id || `speaker_${index}`,
        speaker_name: segment.speaker_name || `说话人 ${index + 1}`,
        speakerKey: segment.speakerKey || segment.speaker_id || `speaker_${index}`,
        speakerDisplayName: segment.speakerDisplayName || segment.speaker_name || `说话人 ${index + 1}`,
        color: segment.color || '#409EFF',
        start_time: segment.start_time || 0,
        end_time: segment.end_time || 0,
        text: segment.text || '',
        timestamps: segment.timestamps || []
      }
      
      return {
        ...safeSegment,
        subSegments: segment.subSegments?.map(sub => ({
          subsegmentId: `${safeSegment.speaker_id}-${sub.start_time || 0}-${sub.end_time || 0}`,
          text: sub.text || '',
          start_time: sub.start_time || 0,
          end_time: sub.end_time || 0,
          timestamps: sub.timestamps || []
        })) || [{
          subsegmentId: `${safeSegment.speaker_id}-${safeSegment.start_time}-${safeSegment.end_time}`,
          text: safeSegment.text,
          start_time: safeSegment.start_time,
          end_time: safeSegment.end_time,
          timestamps: safeSegment.timestamps
        }]
      }
    })
  } else {
    const index = segments.value.findIndex(s => s.segmentId === updatedSegments.segmentId)
    if (index > -1) {
      // 确保基本字段存在
      const safeSegment = {
        ...updatedSegments,
        speaker_id: updatedSegments.speaker_id || segments.value[index].speaker_id,
        speaker_name: updatedSegments.speaker_name || segments.value[index].speaker_name,
        speakerKey: updatedSegments.speakerKey || updatedSegments.speaker_id || segments.value[index].speakerKey,
        speakerDisplayName: updatedSegments.speakerDisplayName || updatedSegments.speaker_name || segments.value[index].speakerDisplayName,
        color: updatedSegments.color || segments.value[index].color || '#409EFF',
        start_time: updatedSegments.start_time || 0,
        end_time: updatedSegments.end_time || 0,
        text: updatedSegments.text || '',
        timestamps: updatedSegments.timestamps || []
      }
      
      segments.value[index] = {
        ...safeSegment,
        subSegments: updatedSegments.subSegments?.map(sub => ({
          subsegmentId: `${safeSegment.speaker_id}-${sub.start_time || 0}-${sub.end_time || 0}`,
          text: sub.text || '',
          start_time: sub.start_time || 0,
          end_time: sub.end_time || 0,
          timestamps: sub.timestamps || []
        })) || [{
          subsegmentId: `${safeSegment.speaker_id}-${safeSegment.start_time}-${safeSegment.end_time}`,
          text: safeSegment.text,
          start_time: safeSegment.start_time,
          end_time: safeSegment.end_time,
          timestamps: safeSegment.timestamps
        }]
      }
    }
  }
}

// 播放控制方法
const togglePlay = () => {
  if (playing.value) {
    audio.value.pause()
  } else {
    audio.value.play()
  }
  playing.value = !playing.value
}

const seekTo = (time) => {
  if (audio.value.readyState >= 1) {  // 确保音频已加载
    audio.value.currentTime = time
    currentTime.value = time  // 立即更新当前时间，避免延迟
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
  const response = await getFileDetail(route.params.id)
  const formattedData = formatFileData(response)
  file.value = formattedData
  
  // 初始化 segments
  segments.value = formattedData.segments.map((segment, index) => {
    // 确保基本字段存在
    const safeSegment = {
      // 原始字段（不变）
      speaker_id: segment.speaker_id || `speaker_${index}`,
      speaker_name: segment.speaker_name || `说话人 ${index + 1}`,
      
      // 前端使用的字段（可变）
      speakerKey: segment.speaker_id || `speaker_${index}`,
      speakerDisplayName: segment.speaker_name || `说话人 ${index + 1}`,
      color: segment.color || '#409EFF',
      
      // 段落标识（可变）
      segmentId: `${segment.speaker_id || `speaker_${index}`}_${nanoid(6)}`,
      
      // 时间信息（可变）
      start_time: segment.start_time || 0,
      end_time: segment.end_time || 0,
      
      // 子段落信息
      text: segment.text || '',
      timestamps: segment.timestamps || [],
      
      // 其他状态
      isSelected: false
    }
    
    return {
      ...safeSegment,
      subSegments: [{
        subsegmentId: `${safeSegment.speaker_id}-${safeSegment.start_time}-${safeSegment.end_time}`,
        text: safeSegment.text,
        start_time: safeSegment.start_time,
        end_time: safeSegment.end_time,
        timestamps: safeSegment.timestamps
      }]
    }
  })

  // 只在第一次加载时初始化 speakers
  if (!speakers.value.length) {
    const colors = ['#409EFF', '#F56C6C', '#67C23A', '#E6A23C', '#909399']
    speakers.value = formattedData.speakers.map((speaker, index) => ({
      // 前端使用的字段（可变）
      speakerKey: speaker.id || `speaker_${index}`,
      speakerDisplayName: speaker.name || `说话人 ${index + 1}`,
      color: colors[index % colors.length],
      
      // 原始字段（不变）
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

const handleTimeUpdate = (time) => {
  currentTime.value = time
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
    // 批量更新的逻辑保持不变
    segments.value = segments.value.map(segment => {
      if (segment.speakerKey === updatedSegment.speakerKey) {
        const updatedSegmentData = {
          ...segment,
          speakerKey: updatedSegment.speakerKey,
          speakerDisplayName: updatedSegment.speakerDisplayName,
          speaker_id: segment.speaker_id,
          speaker_name: segment.speaker_name,
          segmentId: `${updatedSegment.speakerKey}_${nanoid(6)}`
        }
        return updatedSegmentData
      }
      return segment
    })
  } else {
    // 单个段落更新
    const index = segments.value.findIndex(s => s.segmentId === updatedSegment.segmentId)
    
    if (index > -1) {
      const oldSegment = segments.value[index]
      console.log('更新前:', {
        speakerKey: oldSegment.speakerKey,
        subSegments: oldSegment.subSegments.map(s => s.speakerKey)
      })
      
      // 更新整个 segments 数组，确保每个子段落都更新 speakerKey
      segments.value = segments.value.map(segment => {
        if (segment.segmentId === updatedSegment.segmentId) {
          return {
            ...segment,
            speakerKey: updatedSegment.speakerKey,
            speakerDisplayName: updatedSegment.speakerDisplayName,
            subSegments: segment.subSegments.map(sub => ({
              ...sub,
              speakerKey: updatedSegment.speakerKey  // 更新所有子段落
            }))
          }
        }
        return segment
      })
      
      console.log('更新后:', {
        speakerKey: segments.value[index].speakerKey,
        subSegments: segments.value[index].subSegments.map(s => s.speakerKey)
      })
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

