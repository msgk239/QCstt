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
        @speakers-update="handleSpeakersUpdate"
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
const speakers = ref([])
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
  saving.value = true
  try {
    await fileStore.saveFile(route.params.id, {
      segments: segments.value,
      speakers: speakers.value
    })
    lastSaveTime.value = new Date()
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSegmentUpdate = (segment) => {
  const index = segments.value.findIndex(s => s.id === segment.id)
  if (index > -1) {
    segments.value[index] = segment
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
  segments.value = formattedData.segments
  // 只在 speakers 为空时初始化
  if (!speakers.value.length) {
    speakers.value = formattedData.speakers
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
  // 更新说话人列表
  speakers.value = speakers.value.map(speaker => {
    if (nameMapping[speaker.name]) {
      return {
        ...speaker,
        name: nameMapping[speaker.name]
      }
    }
    return speaker
  })
  
  // 更新所有相关片段的说话人
  segments.value = segments.value.map(segment => {
    const speaker = speakers.value.find(s => s.id === segment.speaker_id)
    if (speaker && nameMapping[speaker.name]) {
      // 保持 speaker_id 不变，只更新关联的说话人信息
      return {
        ...segment,
        speaker_id: segment.speaker_id
      }
    }
    return segment
  })
  
  ElMessage.success('批量替换成功')
}

const handleReset = () => {
  // 重置说话人列表
  speakers.value = speakers.value.map(speaker => ({
    ...speaker,
    name: speaker.originalName,
    color: speaker.originalColor
  }))
  
  ElMessage.success('重置成功')
}

const currentSpeaker = computed(() => {
  if (!segments.value.length) return null
  const selectedSegment = segments.value.find(s => s.isSelected)
  if (!selectedSegment) return null
  
  const speaker = speakers.value.find(s => s.id === selectedSegment.speaker_id)
  if (!speaker) return null

  return {
    ...speaker,
    originalName: speaker.name,
    newName: speaker.name
  }
})

const handleSpeakersUpdate = (updatedSpeakers) => {
  // 确保只更新当前说话人，不影响其他说话人的状态
  speakers.value = updatedSpeakers
}

const handleSegmentSelect = (updatedSegments) => {
  // 确保只更新选中状态，不影响其他状态
  segments.value = updatedSegments
}

const handleSpeakerChange = (speakerId, segment) => {
  // 只更新当前段落的说话人
  segments.value = segments.value.map(s => {
    if (s.id === segment.id) {
      return {
        ...s,
        speaker_id: speakerId
      }
    }
    return s
  })
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

