<template>
  <div class="editor-view">
    <!-- 顶部工具栏 -->
    <Toolbar 
      :file="file"
      @save="handleSave"
    />

    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 音频播放器 -->
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

      <!-- 转写内容 -->
      <Transcript 
        ref="transcriptRef"
        :segments="segments"
        :speakers="speakers"
        :currentTime="currentTime"
        @segment-update="handleSegmentUpdate"
        @speaker-change="handleSpeakerChange"
      />
    </div>

    <!-- 文本编辑工具栏 -->
    <EditToolbar 
      @format-apply="applyFormat"
      @note-add="addNote"
      @timestamp-insert="insertTimestamp"
    />

    <!-- 对话框组件 -->
    <ReplaceDialog v-model="replaceDialogVisible" />
    <HotwordsDialog v-model="hotwordsDialogVisible" />
    <SpeedMenuDialog v-model="speedMenuVisible" />
    <SpeakerManagerDialog v-model="speakerDialogVisible" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as fileApi from '@/api/modules/file'

// 导入拆分的组件
import Toolbar from './EditorComponents/Toolbar.vue'
import AudioPlayer from './EditorComponents/AudioPlayer.vue'
import Transcript from './EditorComponents/Transcript.vue'
import EditToolbar from './EditorComponents/EditToolbar.vue'
import ReplaceDialog from './EditorComponents/ReplaceDialog.vue'
import HotwordsDialog from './EditorComponents/HotwordsDialog.vue'
import SpeedMenuDialog from './EditorComponents/SpeedMenuDialog.vue'
import SpeakerManagerDialog from './EditorComponents/SpeakerManagerDialog.vue'

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

// 方法
const handleSave = async () => {
  saving.value = true
  try {
    await fileApi.updateFile(route.params.id, {
      segments: segments.value
    })
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('Failed to save:', error)
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

const togglePlay = () => {
  audioPlayerRef.value?.togglePlay()
}

const seekTo = (time) => {
  audioPlayerRef.value?.seekTo(time)
}

const handleSpeedChange = (speed) => {
  playbackRate.value = speed
  audioPlayerRef.value?.setPlaybackRate(speed)
}

// 生命周期钩子
onMounted(async () => {
  try {
    const response = await fileApi.getFile(route.params.id)
    file.value = response.data
    segments.value = response.data.segments
    speakers.value = response.data.speakers
  } catch (error) {
    console.error('Failed to load file:', error)
    ElMessage.error('加载失败')
  }
})
</script>

<style scoped>
.editor-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}
</style>

