<template>
  <div class="editor-view">
    <!-- 顶部标题和工具栏 -->
    <div class="editor-header">
      <div class="header-left">
        <el-button 
          link
          type="primary" 
          @click="handleBack"
          class="back-button"
        >
          <el-icon><Back /></el-icon>返回
        </el-button>
        <div class="divider"></div>
        <h1>{{ formatDisplayName(fileName) }}</h1>
      </div>
      <div class="header-tools">
        <ExportToolbar @export="handleExport"/>
        <ShareToolbar />
        <StyleTemplateToolbar />
        <div class="divider"></div>
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
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getFileDetail, formatFileData, getAudioFile, fileApi } from '@/api/modules/file'
import { useFileStore } from '@/stores/fileStore'
import { nanoid } from 'nanoid'
import { Back } from '@element-plus/icons-vue'

// 获取 store 实例
const fileStore = useFileStore()

// 导入所有组件
import AudioPlayer from './EditorComponents/AudioPlayer.vue'
import Transcript from './EditorComponents/Transcript.vue'
import EditToolbar from './EditorComponents/EditToolbar.vue'
import ReplaceDialog from './EditorComponents/ReplaceDialog.vue'
import HotwordsDialog from './EditorComponents/HotwordsDialog.vue'
import SpeedMenuDialog from './EditorComponents/SpeedMenuDialog.vue'
import ExportToolbar from './EditorComponents/ExportToolbar.vue'
import NoteToolbar from './EditorComponents/NoteToolbar.vue'
import ShareToolbar from './EditorComponents/ShareToolbar.vue'
import StyleTemplateToolbar from './EditorComponents/StyleTemplateToolbar.vue'
import UndoRedoToolbar from './EditorComponents/UndoRedoToolbar.vue'

// 导入事件总线
import { editorBus, EVENT_TYPES } from './EditorComponents/eventBus'

// 路由
const route = useRoute()
const router = useRouter()

// 状态
const file = ref(null)
const segments = ref([])
const speakers = ref([])  // 初始为空数组，而不是 null
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

// 添加对 Transcript 组件的引用
const transcriptRef = ref(null)

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

const handleSegmentUpdate = async (updatedSegments) => {
  saving.value = true
  try {
    const response = await fileApi.saveContent(route.params.id, {
      type: 'content_update',
      segments: updatedSegments  // 直接传对象即可
    })
    
    if (response.code === 200) {
      console.log('保存成功')
      // 删除这里获取最新数据的部分,只保留保存功能
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

// 初始化默认说话人
const initDefaultSpeakers = () => {
  return [
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
  ]
}

// 在加载文件内容时初始化 speakers
const loadFileContent = async () => {
  try {
    const response = await fileApi.getContent(route.params.id)
    if (response.code === 200) {
      speakers.value = response.data?.speakers || []
      // ... 其他数据加载
    }
  } catch (error) {
    console.error('加载文件内容失败:', error)
  }
}

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
      subsegmentId: segment.subsegmentId || `subsegment_${segment.start_time || 0}-${segment.end_time || 0}`
    }
    
    return safeSegment
  })

  // 只在第一次加载时初始化 speakers
  if (!speakers.value.length) {
    const colors = ['#409EFF', '#F56C6C', '#67C23A', '#E6A23C', '#909399']
    speakers.value = formattedData.speakers.map((speaker, index) => ({
      speakerKey: speaker.speakerKey || speaker.id || `speaker_${index}`,
      speakerDisplayName: speaker.speakerDisplayName || speaker.name || `说话人 ${index + 1}`,
      color: speaker.color || colors[index % colors.length],
      speaker_id: speaker.speaker_id || speaker.id || `speaker_${index}`,
      speaker_name: speaker.speaker_name || speaker.name || `说话人 ${index + 1}`,
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
})

onUnmounted(() => {
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

const handleSpeakerChange = async (updatedSegment) => {
  console.log('handleSpeakerChange 被调用:', updatedSegment)  // 添加日志
  
  if (updatedSegment.batchUpdate) {
    console.log('进入 batchUpdate 分支')  // 添加日志
    console.log('更新前的 speakers:', JSON.stringify(speakers.value, null, 2))
    
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

    // 同步更新 speakers 数组
    speakers.value = speakers.value.map(speaker => {
      if (speaker.speakerKey === updatedSegment.oldSpeakerKey) {
        return {
          ...speaker,
          speakerDisplayName: updatedSegment.speakerDisplayName,
          speaker_name: updatedSegment.speakerDisplayName
        }
      }
      return speaker
    })
    
    console.log('更新后的 speakers:', JSON.stringify(speakers.value, null, 2))
    console.log('updatedSegment:', updatedSegment)

    // 等待 Vue 完成更新
    await nextTick()
  }

  // 说话人更新后保存
  await handleSave({ type: 'speaker_update' })
}

// 修改获取说话人名字的函数
const getSpeakerName = (segment) => {
  // 只使用 speakerDisplayName
  return segment.speakerDisplayName
}

// 添加 handleSave 函数
const handleSave = async (options = {}) => {
  try {
    if (options.type === 'speaker_update') {
      // 从 Transcript 组件获取合并的段落数据
      const transcriptData = transcriptRef.value.mergedSegments
      
      // 打印 speakers 的值
      console.log('保存前的 speakers:', JSON.stringify(speakers.value, null, 2))
      
      // 构建要保存的数据
      const saveData = {
        type: 'speaker_update',
        segments: {
          merged: transcriptData
        },
        speakers: speakers.value
      }
      
      // 在发送请求前打印最新数据
      //console.log('保存说话人数据:\n', JSON.stringify(saveData, null, 2))

      await fileApi.saveContent(route.params.id, saveData)
      ElMessage.success('说话人更新成功')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 添加导出处理函数
const handleExport = async (formats) => {
  try {
    console.log('准备导出格式：', formats)
    const format = formats[0] // 获取第一个格式
    const response = await fileApi.exportTranscript(route.params.id, format)
    
    console.log('收到的响应：', response)
    console.log('响应类型：', response.type) // 查看 Blob 的 MIME 类型
    
    // response 本身就是 Blob，不需要再次创建
    const downloadLink = document.createElement('a')
    downloadLink.href = URL.createObjectURL(response) // 直接使用 response
    downloadLink.download = `${formatDisplayName(file.value?.name || 'export')}.${format}`
    console.log('下载链接：', downloadLink.href)
    console.log('文件名：', downloadLink.download)
    
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
    URL.revokeObjectURL(downloadLink.href)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleBack = () => {
  router.push({ name: 'home' })
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

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.back-button:hover {
  opacity: 0.8;
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

