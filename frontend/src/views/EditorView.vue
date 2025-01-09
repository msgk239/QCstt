<template>
  <div class="editor-view">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <div class="file-info">
          <h2 class="file-name">{{ file?.name }}</h2>
          <span class="file-meta">{{ file?.duration }} · {{ file?.date }}</span>
        </div>
      </div>
      <div class="toolbar-right">
        <el-button-group>
          <el-button type="primary" @click="handleSave" :loading="saving">
            <el-icon><Save /></el-icon>保存
          </el-button>
          <el-dropdown trigger="click">
            <el-button type="primary">
              <el-icon><Download /></el-icon>导出<el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleExport('txt')">文本文件 (.txt)</el-dropdown-item>
                <el-dropdown-item @click="handleExport('docx')">Word文档 (.docx)</el-dropdown-item>
                <el-dropdown-item @click="handleExport('pdf')">PDF文件 (.pdf)</el-dropdown-item>
                <el-dropdown-item @click="handleExport('srt')">字幕文件 (.srt)</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-button-group>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 音频播放器 -->
      <div class="audio-player">
        <div class="waveform" ref="waveformRef"></div>
        <div class="player-controls">
          <el-button-group>
            <el-button :icon="PlaybackSpeed" @click="toggleSpeedMenu">
              {{ playbackRate }}x
            </el-button>
            <el-button :icon="Previous" @click="skipBackward" />
            <el-button :icon="playing ? Pause : Play" @click="togglePlay" />
            <el-button :icon="Next" @click="skipForward" />
          </el-button-group>
          <span class="time-display">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </span>
        </div>
      </div>

      <!-- 转写内容 -->
      <div class="transcript" ref="transcriptRef">
        <div
          v-for="(segment, index) in segments"
          :key="index"
          class="segment"
          :class="{ active: isSegmentActive(segment) }"
          @click="seekTo(segment.start)"
        >
          <div class="segment-header">
            <el-dropdown trigger="click" @command="handleSpeakerChange($event, segment)">
              <span class="speaker-name" :style="{ color: getSpeakerColor(segment.speaker) }">
                {{ segment.speaker }}
                <el-icon><Edit /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="speaker in speakers"
                    :key="speaker.id"
                    :command="speaker.id"
                  >
                    {{ speaker.name }}
                  </el-dropdown-item>
                  <el-dropdown-item divided command="new">
                    <el-icon><Plus /></el-icon>添加新说话人
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <span class="segment-time">{{ formatTime(segment.start) }}</span>
          </div>
          <div
            class="segment-text"
            contenteditable
            @input="handleSegmentInput($event, segment)"
            @blur="handleSegmentBlur($event, segment)"
            v-html="segment.text"
          ></div>
        </div>
      </div>
    </div>

    <!-- 说话人管理对话框 -->
    <el-dialog
      v-model="speakerDialogVisible"
      title="说话人管理"
      width="500px"
    >
      <div class="speaker-list">
        <div v-for="speaker in speakers" :key="speaker.id" class="speaker-item">
          <el-color-picker v-model="speaker.color" size="small" />
          <el-input v-model="speaker.name" placeholder="说话人名称" />
          <el-button type="danger" circle @click="deleteSpeaker(speaker)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <el-button type="primary" plain @click="addSpeaker">
          <el-icon><Plus /></el-icon>添加说话人
        </el-button>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="speakerDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSpeakers">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 播放速度菜单 -->
    <el-dialog
      v-model="speedMenuVisible"
      title="播放速度"
      width="300px"
    >
      <div class="speed-list">
        <el-radio-group v-model="playbackRate" @change="handleSpeedChange">
          <el-radio-button v-for="speed in speeds" :key="speed" :value="speed">
            {{ speed }}x
          </el-radio-button>
        </el-radio-group>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import WaveSurfer from 'wavesurfer.js'
import {
  ArrowLeft,
  ArrowDown,
  Download,
  Edit,
  Delete,
  Plus,
  CaretRight as Play,
  VideoPause as Pause,
  DArrowLeft as Previous,
  DArrowRight as Next,
  Timer as PlaybackSpeed,
  Document as Save
} from '@element-plus/icons-vue'
import * as fileApi from '@/api/modules/file'

// 路由
const route = useRoute()
const router = useRouter()

// 状态
const file = ref(null)
const segments = ref([])
const speakers = ref([])
const saving = ref(false)
const speakerDialogVisible = ref(false)
const speedMenuVisible = ref(false)

// 音频播放器
const waveformRef = ref(null)
const wavesurfer = ref(null)
const playing = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1)
const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2]

// 计算属性
const speakerColors = computed(() => {
  const colors = {}
  speakers.value.forEach(speaker => {
    colors[speaker.id] = speaker.color
  })
  return colors
})

// 方法
const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  return `${h > 0 ? h + ':' : ''}${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const initWaveSurfer = () => {
  wavesurfer.value = WaveSurfer.create({
    container: waveformRef.value,
    waveColor: '#A8C8FF',
    progressColor: '#1867C0',
    cursorColor: '#1867C0',
    barWidth: 2,
    barGap: 1,
    responsive: true,
    height: 100
  })

  wavesurfer.value.on('ready', () => {
    duration.value = wavesurfer.value.getDuration()
  })

  wavesurfer.value.on('audioprocess', () => {
    currentTime.value = wavesurfer.value.getCurrentTime()
    updateActiveSegment()
  })

  wavesurfer.value.on('play', () => {
    playing.value = true
  })

  wavesurfer.value.on('pause', () => {
    playing.value = false
  })

  // 加载音频文件
  wavesurfer.value.load(`/api/v1/files/${route.params.id}/audio`)
}

const togglePlay = () => {
  wavesurfer.value?.playPause()
}

const skipBackward = () => {
  const newTime = currentTime.value - 5
  wavesurfer.value?.seekTo(Math.max(0, newTime) / duration.value)
}

const skipForward = () => {
  const newTime = currentTime.value + 5
  wavesurfer.value?.seekTo(Math.min(duration.value, newTime) / duration.value)
}

const seekTo = (time) => {
  wavesurfer.value?.seekTo(time / duration.value)
}

const toggleSpeedMenu = () => {
  speedMenuVisible.value = true
}

const handleSpeedChange = (speed) => {
  playbackRate.value = speed
  wavesurfer.value?.setPlaybackRate(speed)
  speedMenuVisible.value = false
}

const updateActiveSegment = () => {
  const time = currentTime.value
  const activeSegment = segments.value.find(
    segment => time >= segment.start && time <= segment.end
  )
  if (activeSegment) {
    const element = document.querySelector(`[data-segment-id="${activeSegment.id}"]`)
    element?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const isSegmentActive = (segment) => {
  const time = currentTime.value
  return time >= segment.start && time <= segment.end
}

const getSpeakerColor = (speakerId) => {
  return speakerColors.value[speakerId] || '#409EFF'
}

const handleSegmentInput = (event, segment) => {
  segment.text = event.target.innerHTML
}

const handleSegmentBlur = (event, segment) => {
  // 可以在这里添加自动保存逻辑
}

const handleSpeakerChange = (speakerId, segment) => {
  if (speakerId === 'new') {
    speakerDialogVisible.value = true
    return
  }
  segment.speaker = speakerId
}

const addSpeaker = () => {
  speakers.value.push({
    id: Date.now().toString(),
    name: '新说话人',
    color: '#409EFF'
  })
}

const deleteSpeaker = (speaker) => {
  const index = speakers.value.findIndex(s => s.id === speaker.id)
  if (index > -1) {
    speakers.value.splice(index, 1)
  }
}

const saveSpeakers = async () => {
  try {
    await fileApi.updateFile(route.params.id, {
      speakers: speakers.value
    })
    speakerDialogVisible.value = false
    ElMessage.success('说话人信息已更新')
  } catch (error) {
    console.error('Failed to save speakers:', error)
    ElMessage.error('保存失败')
  }
}

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

const handleExport = async (format) => {
  try {
    await fileApi.exportFile(route.params.id, format)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Failed to export:', error)
    ElMessage.error('导出失败')
  }
}

// 生命周期钩子
onMounted(() => {
  initWaveSurfer()
})

onUnmounted(() => {
  wavesurfer.value?.destroy()
})
</script>

<style scoped>
.editor-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.file-info {
  display: flex;
  flex-direction: column;
}

.file-name {
  margin: 0;
  font-size: 18px;
}

.file-meta {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.main-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.audio-player {
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.player-controls {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.time-display {
  font-family: monospace;
  color: var(--el-text-color-regular);
}

.transcript {
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
}

.segment {
  margin-bottom: 16px;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.segment:hover {
  background-color: var(--el-fill-color-light);
}

.segment.active {
  background-color: var(--el-color-primary-light-9);
}

.segment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.speaker-name {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.segment-time {
  color: var(--el-text-color-secondary);
  font-family: monospace;
}

.segment-text {
  padding: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  min-height: 24px;
  line-height: 1.5;
}

.segment-text:focus {
  outline: none;
  border-color: var(--el-color-primary);
}

.speaker-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.speaker-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.speed-list {
  display: flex;
  justify-content: center;
}
</style>
