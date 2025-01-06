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
    >
      <el-icon class="upload-icon"><Upload /></el-icon>
      <div class="upload-text">
        <h3>将文件拖到此处或点击上传</h3>
        <p>支持 WAV、MP3、FLAC、OGG 格式，单个文件不超过 50MB</p>
      </div>
    </el-upload>

    <!-- 文件列表 -->
    <div v-if="fileList.length" class="file-list">
      <div v-for="file in fileList" :key="file.uid" class="file-item">
        <div class="file-info">
          <el-icon><Document /></el-icon>
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
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
        <div class="upload-info" v-if="fileList.length">
          <span>共 {{ fileList.length }} 个文件</span>
          <span>总大小：{{ totalSize }}</span>
          <span>预计用时：{{ estimatedTime }}</span>
        </div>
        <div class="button-group">
          <el-button @click="handleClose">取消</el-button>
          <el-button
            type="primary"
            :disabled="!fileList.length"
            :loading="isUploading"
            @click="handleUpload"
          >
            {{ isUploading ? '上传中...' : '开始上传' }}
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Upload } from '@element-plus/icons-vue'
import * as asrApi from '@/api/modules/asr'

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
  // 检查文件类型
  const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/flac', 'audio/ogg']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('不支持的文件格式')
    return false
  }

  // 检查文件大小（50MB）
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }

  return true
}

const handleFileChange = (file) => {
  console.log('File changed:', file)
}

const handleFileRemove = (file) => {
  console.log('File removed:', file)
}

const handleUpload = async () => {
  if (!fileList.value.length) return

  isUploading.value = true
  try {
    // 并行上传所有文件
    await Promise.all(fileList.value.map(async file => {
      file.status = 'uploading'
      file.percentage = 0

      const onProgress = progressEvent => {
        if (progressEvent.total) {
          file.percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      }

      try {
        const res = await asrApi.uploadAudio(file.raw, {
          language: options.value.language,
          hotwordLibraries: options.value.hotwordLibraries,
          onProgress
        })

        file.status = 'success'
        file.taskId = res.taskId
        file.fileId = res.fileId

        // 开始轮询转写进度
        startProgressPolling(file)
      } catch (error) {
        file.status = 'error'
        file.error = error.message || '上传失败'
        throw error
      }
    }))

    ElMessage.success('文件上传成功')
    emit('upload-success', fileList.value)
    handleClose()
  } catch (error) {
    console.error('Upload error:', error)
    ElMessage.error('部分文件上传失败')
    emit('upload-error', error)
  } finally {
    isUploading.value = false
  }
}

// 轮询转写进度
const startProgressPolling = async (file) => {
  const checkProgress = async () => {
    try {
      const res = await asrApi.getProgress(file.taskId)
      file.transcriptionProgress = res.progress
      file.transcriptionStatus = res.status

      if (res.progress < 100) {
        setTimeout(checkProgress, 2000)
      } else {
        file.transcriptionStatus = 'completed'
      }
    } catch (error) {
      console.error('Failed to check progress:', error)
      file.transcriptionStatus = 'error'
    }
  }

  await checkProgress()
}

const handleClose = () => {
  fileList.value = []
  isUploading.value = false
  dialogVisible.value = false
}

// 组件状态
const options = ref({
  language: 'auto',
  hotwordLibraries: []
})
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
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
  background-color: var(--el-fill-color-light);
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
</style> 