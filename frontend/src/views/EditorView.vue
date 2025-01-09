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
      />
    </div>

    <!-- 对话框组件 -->
    <ReplaceDialog v-model="replaceDialogVisible" />
    <HotwordsDialog v-model="hotwordsDialogVisible" />
    <SpeedMenuDialog v-model="speedMenuVisible" />
    <SpeakerManagerDialog v-model="speakerDialogVisible" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getFile, formatFileData, getAudioFile } from '@/api/modules/file'
import { useFileStore } from '@/stores/file'

// 获取 store 实例
const fileStore = useFileStore()

// 导入所有组件
import AudioPlayer from './EditorComponents/AudioPlayer.vue'
import Transcript from './EditorComponents/Transcript.vue'
import EditToolbar from './EditorComponents/EditToolbar.vue'
import ReplaceDialog from './EditorComponents/ReplaceDialog.vue'
import HotwordsDialog from './EditorComponents/HotwordsDialog.vue'
import SpeedMenuDialog from './EditorComponents/SpeedMenuDialog.vue'
import SpeakerManagerDialog from './EditorComponents/SpeakerManagerDialog.vue'
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
const speakerDialogVisible = ref(false)

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
    const response = await getAudioFile(route.params.id)
    const audioUrl = URL.createObjectURL(response.data)
    audio.value.src = audioUrl
    
    // 设置音频事件监听
    audio.value.addEventListener('loadedmetadata', () => {
      duration.value = audio.value.duration
    })
    
    audio.value.addEventListener('timeupdate', () => {
      currentTime.value = audio.value.currentTime
    })
    
    audio.value.addEventListener('ended', () => {
      playing.value = false
    })
  } catch (error) {
    console.error('加载音频失败:', error)
    ElMessage.error('音频加载失败')
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

const handleSpeakerChange = (speakerId, segment) => {
  if (speakerId === 'new') {
    speakerDialogVisible.value = true
    return
  }
  segment.speaker = speakerId
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
  audio.value.currentTime = time
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
  const response = await getFile(route.params.id)
  const formattedData = formatFileData(response)
  file.value = formattedData
  segments.value = formattedData.segments
  speakers.value = formattedData.speakers
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
  const match = fullName.match(/\d{8}_\d{6}_(.+)/)
  return match ? match[1] : fullName
}
</script>

<style scoped>
.editor-view {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
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
  /* 留出播放器的空间 */
  padding-bottom: 80px;
}

.player-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
  padding: 8px 24px;
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
</style>

