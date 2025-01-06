<template>
  <div class="audio-recognizer">
    <!-- 上传区域 -->
    <el-upload
      class="upload-area"
      drag
      :action="null"
      :auto-upload="false"
      :show-file-list="true"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
      accept=".mp3,.wav,.ogg,.m4a,.flac"
    >
      <el-icon class="upload-icon"><Upload /></el-icon>
      <div class="upload-text">
        <span>将音频文件拖到此处，或<em>点击上传</em></span>
        <p class="upload-tip">支持 MP3、WAV、OGG、M4A、FLAC 格式</p>
      </div>
    </el-upload>

    <!-- 识别选项 -->
    <div class="recognize-options" v-if="fileList.length">
      <el-form :model="options" label-width="100px">
        <el-form-item label="识别语言">
          <el-select v-model="options.language" placeholder="请选择语言">
            <el-option
              v-for="lang in languages"
              :key="lang.code"
              :label="lang.name"
              :value="lang.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="热词库">
          <el-select
            v-model="options.hotwordLibraries"
            multiple
            collapse-tags
            placeholder="请选择热词库"
          >
            <el-option
              v-for="lib in hotwordLibraries"
              :key="lib.id"
              :label="lib.name"
              :value="lib.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 文件列表和进度 -->
    <div class="file-list" v-if="fileList.length">
      <div
        v-for="file in fileList"
        :key="file.uid"
        class="file-item"
      >
        <div class="file-info">
          <el-icon><Document /></el-icon>
          <span class="filename">{{ file.name }}</span>
          <span class="filesize">{{ formatSize(file.size) }}</span>
        </div>
        <div class="file-status">
          <template v-if="file.status === 'ready'">
            <el-button type="primary" @click="handleRecognize(file)">
              开始识别
            </el-button>
            <el-button @click="handleRemove(file)">
              移除
            </el-button>
          </template>
          <template v-else-if="file.status === 'processing'">
            <el-progress
              :percentage="file.progress || 0"
              :status="file.progress >= 100 ? 'success' : ''"
            />
            <div class="progress-text">{{ file.progressText }}</div>
          </template>
          <template v-else-if="file.status === 'success'">
            <el-button type="success" @click="handleViewResult(file)">
              查看结果
            </el-button>
          </template>
          <template v-else-if="file.status === 'error'">
            <div class="error-message">{{ file.error }}</div>
            <el-button type="primary" @click="handleRetry(file)">
              重试
            </el-button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Upload } from '@element-plus/icons-vue'
import * as asrApi from '@/api/modules/asr'

const router = useRouter()

// 状态
const fileList = ref([])
const languages = ref([])
const hotwordLibraries = ref([])
const options = ref({
  language: 'auto',
  hotwordLibraries: []
})

// 获取支持的语言列表
const fetchLanguages = async () => {
  try {
    const res = await asrApi.getSupportedLanguages()
    languages.value = res
  } catch (error) {
    console.error('Failed to fetch languages:', error)
    ElMessage.error('获取语言列表失败')
  }
}

// 获取热词库列表
const fetchHotwordLibraries = async () => {
  try {
    const res = await asrApi.getHotwordLibraries()
    hotwordLibraries.value = res
  } catch (error) {
    console.error('Failed to fetch hotword libraries:', error)
    ElMessage.error('获取热词库列表失败')
  }
}

// 文件大小格式化
const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 文件上传前检查
const beforeUpload = (file) => {
  const isAudio = /\\.(mp3|wav|ogg|m4a|flac)$/i.test(file.name)
  if (!isAudio) {
    ElMessage.error('只能上传音频文件！')
    return false
  }
  const isLt2G = file.size / 1024 / 1024 / 1024 < 2
  if (!isLt2G) {
    ElMessage.error('文件大小不能超过 2GB！')
    return false
  }
  return true
}

// 文件变更处理
const handleFileChange = (file) => {
  if (file.status === 'ready') {
    fileList.value.push({
      ...file,
      progress: 0,
      progressText: '',
      error: null
    })
  }
}

// 移除文件
const handleRemove = (file) => {
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

// 开始识别
const handleRecognize = async (file) => {
  try {
    file.status = 'processing'
    file.progress = 0
    file.progressText = '准备上传...'

    // 上传文件
    const uploadRes = await asrApi.uploadAudio(file.raw, {
      language: options.value.language,
      hotwordLibraries: options.value.hotwordLibraries
    })

    // 轮询进度
    const taskId = uploadRes.taskId
    const checkProgress = async () => {
      try {
        const progressRes = await asrApi.getProgress(taskId)
        file.progress = progressRes.progress
        file.progressText = progressRes.status

        if (progressRes.progress < 100) {
          setTimeout(checkProgress, 2000)
        } else {
          file.status = 'success'
          file.fileId = progressRes.fileId
        }
      } catch (error) {
        file.status = 'error'
        file.error = '获取进度失败'
        console.error('Failed to check progress:', error)
      }
    }

    await checkProgress()
  } catch (error) {
    file.status = 'error'
    file.error = '识别失败'
    console.error('Failed to recognize:', error)
  }
}

// 重试识别
const handleRetry = (file) => {
  file.status = 'ready'
  file.progress = 0
  file.progressText = ''
  file.error = null
  handleRecognize(file)
}

// 查看结果
const handleViewResult = (file) => {
  if (file.fileId) {
    router.push('/editor/' + file.fileId)
  }
}

// 初始化
onMounted(() => {
  fetchLanguages()
  fetchHotwordLibraries()
})
</script>

<style scoped>
.audio-recognizer {
  padding: 20px;
}

.upload-area {
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  background-color: var(--el-bg-color-page);
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: var(--el-color-primary);
}

.upload-icon {
  font-size: 48px;
  color: var(--el-text-color-secondary);
  margin-bottom: 16px;
}

.upload-text {
  color: var(--el-text-color-regular);
}

.upload-text em {
  color: var(--el-color-primary);
  font-style: normal;
  cursor: pointer;
}

.upload-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}

.recognize-options {
  margin-top: 24px;
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.file-list {
  margin-top: 24px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filename {
  font-weight: 500;
}

.filesize {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-text {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  min-width: 100px;
}

.error-message {
  color: var(--el-color-danger);
  font-size: 12px;
}
</style> 