<template>
  <div class="audio-recognizer">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span>语音识别</span>
            <el-select 
              v-model="language" 
              placeholder="选择语言"
              class="language-select"
            >
              <el-option
                v-for="lang in languages"
                :key="lang.code"
                :label="lang.name"
                :value="lang.code"
              />
            </el-select>
          </div>
          <div class="header-right">
            <el-select
              v-model="device"
              placeholder="运行模式"
              class="device-select"
            >
              <el-option
                v-for="dev in devices"
                :key="dev.value"
                :label="dev.label"
                :value="dev.value"
              />
            </el-select>
          </div>
        </div>
      </template>
      
      <el-upload
        class="upload-demo"
        drag
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        multiple
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 wav/mp3 格式音频文件，采样率需为 16KHz
          </div>
        </template>
      </el-upload>

      <div class="action-buttons">
        <el-button 
          type="primary" 
          @click="handleRecognize"
          :loading="recognizing"
          :disabled="!hasFiles"
        >
          开始识别
        </el-button>
        <el-button 
          @click="handleClear"
          :disabled="!hasFiles || recognizing"
        >
          清空
        </el-button>
      </div>

      <!-- 结果展示 -->
      <div class="results" v-if="results.length > 0">
        <h3>识别结果：</h3>
        <el-collapse>
          <el-collapse-item 
            v-for="result in results" 
            :key="result.key"
            :title="result.key"
          >
            <div class="result-item">
              <p class="result-text">{{ result.text }}</p>
              <div class="result-actions">
                <el-button 
                  type="primary" 
                  link 
                  @click="copyText(result.text)"
                >
                  复制文本
                </el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { getLanguages, recognizeAudio } from '@/api/asr'

// 状态
const language = ref('auto')
const languages = ref([])
const fileList = ref([])
const recognizing = ref(false)
const results = ref([])

// 设备选择
const device = ref('auto')
const devices = [
  { label: '自动选择', value: 'auto' },
  { label: 'GPU模式', value: 'gpu' },
  { label: 'CPU模式', value: 'cpu' }
]

// 计算属性
const hasFiles = computed(() => fileList.value.length > 0)

// 初始化语言列表
const initLanguages = async () => {
  try {
    const response = await getLanguages()
    if (response.code === 0) {
      languages.value = response.result
    }
  } catch (error) {
    ElMessage.error('获取语言列表失败')
  }
}

// 文件变更处理
const handleFileChange = (file) => {
  fileList.value.push(file)
}

// 文件移除处理
const handleFileRemove = (file) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

// 开始识别
const handleRecognize = async () => {
  if (!hasFiles.value) {
    ElMessage.warning('请先选择音频文件')
    return
  }

  recognizing.value = true
  try {
    const files = fileList.value.map(f => f.raw)
    const keys = fileList.value.map(f => f.name).join(',')
    
    const response = await recognizeAudio(files, keys, language.value, device.value)
    
    if (response.code === 0) {
      results.value = response.result
      ElMessage.success('识别完成')
    } else {
      ElMessage.error(response.message || '识别失败')
    }
  } catch (error) {
    ElMessage.error('识别失败：' + error.message)
  } finally {
    recognizing.value = false
  }
}

// 清空文件列表和结果
const handleClear = () => {
  fileList.value = []
  results.value = []
}

// 复制文本
const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 组件挂载时初始化
initLanguages()
</script>

<style scoped>
.audio-recognizer {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.language-select, .device-select {
  width: 120px;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.results {
  margin-top: 20px;
}

.result-item {
  padding: 10px;
}

.result-text {
  margin: 0;
  white-space: pre-wrap;
}

.result-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.upload-demo {
  margin-top: 20px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
</style> 