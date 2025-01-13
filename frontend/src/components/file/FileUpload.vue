<template>
  <el-dialog
    v-model="dialogVisible"
    title="上传文件"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 上传区域 -->
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      multiple
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :before-upload="beforeUpload"
      :file-list="fileList"
      accept="audio/*"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="upload-text">
        <h3>将文件拖到此处或点击上传</h3>
        <p>支持所有常见音频格式，单个文件不超过 50MB</p>
      </div>
    </el-upload>

    <!-- 上传选项 -->
    <div class="upload-options">
      <div class="option-item">
        <span class="option-label">识别语言：</span>
        <el-select 
          v-model="language" 
          size="small"
        >
          <el-option label="自动检测" value="auto" />
          <el-option label="中文" value="zh" />
          <el-option label="英文" value="en" />
          <el-option label="日语" value="ja" />
          <el-option label="韩语" value="ko" />
        </el-select>
      </div>
    </div>

    <!-- 文件列表 -->
    <div v-if="fileList.length" class="file-list">
      <div v-for="file in fileList" :key="file.uid" class="file-item">
        <div class="file-info">
          <el-icon><Document /></el-icon>
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
          <span class="file-duration">{{ file.duration || '00:00' }}</span>
        </div>
        <div class="file-progress">
          <el-progress
            v-if="file.status === 'uploading'"
            :percentage="file.percentage || 0"
            :show-text="false"
            :stroke-width="2"
          />
          <el-tag
            v-else-if="file.status === 'success'"
            type="success"
            size="small"
          >
            已完成
          </el-tag>
          <el-tag
            v-else-if="file.status === 'error'"
            type="danger"
            size="small"
          >
            上传失败
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <div class="button-group">
          <el-button @click="handleClose">取消</el-button>
          <el-button
            plain
            :disabled="!fileList.length || isUploading"
            :loading="isUploading"
            @click.prevent="handleUploadOnly"
          >
            {{ isUploading ? '上传中...' : '仅上传' }}
          </el-button>
          <el-button
            type="primary"
            :disabled="!fileList.length || isUploading"
            :loading="isUploading"
            @click.prevent="handleUploadAndRecognize"
          >
            {{ isUploading ? '上传中...' : '上传后识别' }}
          </el-button>
        </div>
      </div>
    </template>

    <!-- 添加转写进度组件 -->
    <TranscriptionProgress
      v-if="showProgress"
      :files="transcribingFiles"
      @close="showProgress = false"
      @pause="handlePauseTranscription"
      @cancel="handleCancelTranscription"
    />
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, UploadFilled } from '@element-plus/icons-vue'
import * as asrApi from '@/api/modules/asr'
import { uploadFile } from '@/api/modules/file'
import { useFileStore } from '@/stores/fileStore'
import { formatDuration } from '@/utils/format'
import { useRouter } from 'vue-router'
import TranscriptionProgress from './TranscriptionProgress.vue'

// 获取 store
const fileStore = useFileStore()
const router = useRouter()

// 定义属性和事件
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'upload-success', 'upload-error'])

// 组件状态
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const uploadRef = ref(null)
const fileList = ref([])
const isUploading = ref(false)
const language = ref('auto')
const transcribingFiles = ref([])
const showProgress = ref(false)

// 计算属性
const totalSize = computed(() => {
  const total = fileList.value.reduce((sum, file) => sum + file.size, 0)
  return formatFileSize(total)
})

const estimatedTime = computed(() => {
  // 假设上传速度为 2MB/s
  const totalSeconds = Math.ceil(fileList.value.reduce((sum, file) => sum + file.size, 0) / (2 * 1024 * 1024))
  if (totalSeconds < 60) {
    return `${totalSeconds}秒`
  }
  return `${Math.ceil(totalSeconds / 60)}分钟`
})

// 方法
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const beforeUpload = (file) => {
  // 检查文件大小（50MB）
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }

  return true
}

const handleFileChange = (file) => {
  if (file.status === 'ready') {
    console.log('File changed:', file)
    // 获取音频时长
    const audio = new Audio()
    audio.src = URL.createObjectURL(file.raw)
    audio.onloadedmetadata = () => {
      file.duration = formatDuration(audio.duration)
      URL.revokeObjectURL(audio.src)
    }
    
    // 确保文件被添加到列表中
    const exists = fileList.value.some(f => f.uid === file.uid)
    if (!exists) {
      fileList.value.push(file)
    }
  }
}

const handleFileRemove = (file) => {
  console.log('Removing file:', file)
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const handleUploadOnly = async () => {
  console.log('handleUploadOnly clicked')
  if (!fileList.value.length) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  if (isUploading.value) {
    ElMessage.warning('文件正在上传中，请稍候')
    return
  }
  await handleUpload('upload')
}

const handleUploadAndRecognize = async () => {
  console.log('handleUploadAndRecognize clicked')
  if (!fileList.value.length) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  if (isUploading.value) {
    ElMessage.warning('文件正在上传中，请稍候')
    return
  }
  await handleUpload('recognize')
}

const handleUpload = async (action) => {
  if (!fileList.value.length) return
  
  isUploading.value = true
  
  try {
    const results = await fileStore.uploadFiles(
      fileList.value.map(file => file.raw),
      {
        action: 'upload',  // 先只上传
        language: language.value,
        onProgress: (progress, file) => {
          const targetFile = fileList.value.find(f => f.uid === file.uid)
          if (targetFile) {
            targetFile.status = 'uploading'
            targetFile.percentage = progress
          }
        }
      }
    )
    
    // 如果是上传并识别，则执行识别流程
    if (action === 'recognize') {
      showProgress.value = true
      for (const file of results) {
        // 添加到转写列表
        transcribingFiles.value.push({
          id: file.file_id,
          name: file.name,
          size: formatFileSize(file.size),
          progress: 0,
          remainingTime: '计算中...',
          currentSegment: '准备中...'
        })

        // 开始识别
        const response = await fileStore.startRecognition(file.file_id)
        
        if (response.code === 200) {
          // 轮询识别状态
          const pollRecognitionStatus = async () => {
            const progress = await asrApi.getRecognizeProgress(file.file_id)
            
            if (progress.code === 200) {
              const { status, progress: percentage, current_segment, remaining_time } = progress.data
              
              // 更新进度信息
              const fileIndex = transcribingFiles.value.findIndex(f => f.id === file.file_id)
              if (fileIndex > -1) {
                transcribingFiles.value[fileIndex] = {
                  ...transcribingFiles.value[fileIndex],
                  progress: percentage,
                  currentSegment: current_segment,
                  remainingTime: remaining_time
                }
              }
              
              if (status === '已完成') {
                ElMessage.success('识别完成')
                // 从列表中移除
                transcribingFiles.value = transcribingFiles.value.filter(f => f.id !== file.file_id)
                if (transcribingFiles.value.length === 0) {
                  showProgress.value = false
                  await router.push({
                    name: 'editor',
                    params: { id: file.file_id }
                  })
                }
                return true
              } else if (status === '识别中') {
                await new Promise(resolve => setTimeout(resolve, 1000))
                return pollRecognitionStatus()
              }
            }
          }
          await pollRecognitionStatus()
        }
      }
    }

    emit('upload-success', {
      files: results,
      options: { action, language: language.value }
    })
    handleClose()
  } catch (error) {
    console.error('Upload error:', error)
    const errorMessage = error.response?.data?.message || error.message || '上传失败'
    ElMessage.error(action === 'recognize' ? 
      `部分文件上传或识别失败: ${errorMessage}` : 
      `部分文件上传失败: ${errorMessage}`)
    emit('upload-error', error)
  } finally {
    isUploading.value = false
  }
}

// 轮询识别进度
const pollRecognizeProgress = async (fileId) => {
  try {
    console.log('Polling progress for file:', fileId)
    const response = await getRecognizeProgress(fileId)
    console.log('Progress response:', response)

    if (response.code === 200) {
      const progress = response.data.progress
      if (progress < 100) {
        // 每2秒轮询一次
        await new Promise(resolve => setTimeout(resolve, 2000))
        await pollRecognizeProgress(fileId)
      }
    } else {
      throw new Error(response.message || '获取识别进度失败')
    }
  } catch (error) {
    console.error('Get progress error:', error)
    throw error
  }
}

const handleClose = () => {
  fileList.value = []
  isUploading.value = false
  dialogVisible.value = false
  fileStore.loading = false // 确保关闭时重置加载状态
}
</script>

<style scoped>
.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  color: var(--el-color-primary);
  margin-bottom: 16px;
}

.upload-text {
  text-align: center;
}

.upload-text h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--el-text-color-primary);
}

.upload-text p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.file-list {
  margin-top: 20px;
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
  background-color: var(--el-fill-color-darker);
  color: var(--el-text-color-primary);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.file-duration {
  margin-left: 12px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.file-progress {
  width: 100px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-info {
  display: flex;
  gap: 16px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.button-group {
  display: flex;
  gap: 12px;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.2s ease;
}

.upload-options {
  margin-top: 20px;
  padding: 16px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.option-item {
  display: flex;
  align-items: center;
}

.option-label {
  width: 100px;
  color: var(--el-text-color-regular);
}
</style> 