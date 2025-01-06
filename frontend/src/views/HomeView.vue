<template>
  <div class="home-view">
    <!-- 文件列表 -->
    <div class="file-list">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-radio-group v-model="viewMode" size="large">
            <el-radio-button value="list">
              <el-icon><List /></el-icon>列表
            </el-radio-button>
            <el-radio-button value="grid">
              <el-icon><Grid /></el-icon>网格
            </el-radio-button>
          </el-radio-group>

          <el-input
            v-model="searchQuery"
            placeholder="搜索文件..."
            :prefix-icon="Search"
            clearable
            class="search-input"
          />
        </div>

        <div class="toolbar-right">
          <el-button type="primary" @click="showUploadDialog">
            <el-icon><Plus /></el-icon>上传文件
          </el-button>
          
          <el-dropdown>
            <el-button>
              <el-icon><Filter /></el-icon>筛选
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>全部文件</el-dropdown-item>
                <el-dropdown-item>最近添加</el-dropdown-item>
                <el-dropdown-item>最近修改</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 列表视图 -->
      <el-table
        v-if="viewMode === 'list'"
        :data="filteredFiles"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="name" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon><Document /></el-icon>
              <audio :ref="'audio-' + row.id" :src="'/api/v1/files/' + row.id + '/audio'" @ended="handleAudioEnded(row)" hidden></audio>
              <div v-if="row.isRenaming" class="rename-input">
                <el-input
                  v-model="row.newName"
                  size="small"
                  @blur="handleRenameConfirm(row)"
                  @keyup.enter="handleRenameConfirm(row)"
                  @keyup.esc="handleRenameCancel(row)"
                />
              </div>
              <span v-else class="filename" @click="handlePlay(row)" :title="'点击播放: ' + row.name">
                {{ row.name }}
                <el-icon v-if="row.isPlaying"><VideoPlay /></el-icon>
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长" width="100">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.duration || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="上传时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-tooltip content="播放/暂停" placement="top">
                <el-button 
                  type="primary" 
                  link
                  @click="handlePlay(row)"
                >
                  <el-icon>
                    <component :is="row.isPlaying ? 'VideoPause' : 'VideoPlay'" />
                  </el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="重命名" placement="top">
                <el-button 
                  type="primary" 
                  link
                  @click="handleRename(row)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="下载" placement="top">
                <el-button 
                  type="primary" 
                  link
                  @click="handleExport(row)"
                >
                  <el-icon><Download /></el-icon>
                </el-button>
              </el-tooltip>
              <el-button 
                type="primary" 
                link 
                :disabled="row.status !== '已上传'"
                @click="startRecognition(row)"
              >
                开始识别
              </el-button>
              <el-button type="danger" link @click="handleDeleteFile(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 网格视图 -->
      <div v-else class="grid-view">
        <el-card
          v-for="file in filteredFiles"
          :key="file.id"
          class="file-card"
          shadow="hover"
        >
          <div class="file-icon">
            <el-icon size="40"><Document /></el-icon>
          </div>
          <h4 class="file-name">{{ file.name }}</h4>
          <div class="file-info">
            <el-tag size="small" type="info">{{ file.duration || '未知' }}</el-tag>
            <el-tag size="small" :type="getStatusType(file.status)">
              {{ file.status }}
            </el-tag>
          </div>
          <div class="file-actions">
            <el-button-group>
              <el-button 
                type="primary" 
                link 
                :disabled="file.status !== '已上传'"
                @click="startRecognition(file)"
              >
                开始识别
              </el-button>
              <el-button type="primary" link>
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button type="danger" link @click="handleDeleteFile(file)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </el-card>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalFiles"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </div>

    <!-- 上传对话框 -->
    <FileUpload
      v-model:visible="uploadDialogVisible"
      @upload-success="handleUploadSuccess"
      @upload-error="handleUploadError"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as asrApi from '@/api/modules/asr'
import FileUpload from '@/components/file/FileUpload.vue'
import {
  Document,
  Edit,
  Download,
  Delete,
  Plus,
  Search,
  Filter,
  List,
  Grid,
  VideoPlay,
  VideoPause
} from '@element-plus/icons-vue'

// 视图模式
const viewMode = ref('list')

// 搜索和筛选
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 文件列表状态
const fileList = ref([])
const loading = ref(false)
const totalFiles = ref(0)

// 上传对话框
const uploadDialogVisible = ref(false)

// 获取文件列表
const fetchFileList = async () => {
  try {
    loading.value = true
    const response = await asrApi.getFileList({
      page: currentPage.value,
      page_size: pageSize.value,
      query: searchQuery.value
    })
    
    if (response.code === 200) {
      fileList.value = response.data.items.map(item => ({
        ...item,
        isPlaying: false,
        isRenaming: false,
        newName: item.name
      }))
      totalFiles.value = response.data.total
    } else {
      ElMessage.error('获取文件列表失败')
    }
  } catch (error) {
    console.error('Fetch file list error:', error)
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

// 监听分页和搜索变化
watch([currentPage, pageSize, searchQuery], () => {
  fetchFileList()
})

// 计算属性
const filteredFiles = computed(() => {
  return fileList.value
})

// 显示上传对话框
const showUploadDialog = () => {
  uploadDialogVisible.value = true
}

// 上传成功回调
const handleUploadSuccess = ({ files, options }) => {
  console.log('Upload success:', { files, options })
  ElMessage.success('文件上传成功')
  fetchFileList() // 刷新文件列表
}

// 上传失败回调
const handleUploadError = (error) => {
  console.error('Upload error:', error)
  ElMessage.error('文件上传失败')
}

// 删除文件
const handleDeleteFile = async (file) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该文件吗？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用删除 API
    const response = await asrApi.deleteFile(file.id)
    if (response.code === 200) {
      ElMessage.success('文件已删除')
      fetchFileList() // 刷新列表
    } else {
      ElMessage.error('删除文件失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete file error:', error)
      ElMessage.error('删除文件失败')
    }
  }
}

// 开始识别
const startRecognition = async (file) => {
  ElMessage.info('识别功能尚未实现')
}

// 音频播放相关
const handlePlay = (file) => {
  const audio = document.querySelector(`#audio-${file.id}`)
  if (file.isPlaying) {
    audio.pause()
    file.isPlaying = false
  } else {
    // 先停止其他正在播放的音频
    fileList.value.forEach(f => {
      if (f.id !== file.id && f.isPlaying) {
        const otherAudio = document.querySelector(`#audio-${f.id}`)
        otherAudio?.pause()
        f.isPlaying = false
      }
    })
    audio.play()
    file.isPlaying = true
  }
}

const handleAudioEnded = (file) => {
  file.isPlaying = false
}

// 重命名相关
const handleRename = (file) => {
  file.isRenaming = true
  file.newName = file.name
}

const handleRenameConfirm = async (file) => {
  if (file.newName && file.newName !== file.name) {
    try {
      const response = await asrApi.renameFile(file.id, file.newName)
      if (response.code === 200) {
        file.name = file.newName
        ElMessage.success('重命名成功')
      } else {
        ElMessage.error('重命名失败')
      }
    } catch (error) {
      console.error('Rename error:', error)
      ElMessage.error('重命名失败')
    }
  }
  file.isRenaming = false
}

const handleRenameCancel = (file) => {
  file.isRenaming = false
}

// 导出相关
const handleExport = async (file) => {
  try {
    const response = await fetch(`/api/v1/files/${file.id}/audio`)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = file.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败')
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case '已上传':
      return 'info'
    case '待识别':
      return 'warning'
    case '已完成':
      return 'success'
    default:
      return 'info'
  }
}

// 初始化
onMounted(() => {
  fetchFileList()
})
</script>

<style scoped>
.home-view {
  padding: 20px;
  height: 100%;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 300px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.hidden-upload {
  display: inline-block;
}

.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.file-card {
  text-align: center;
}

.file-icon {
  margin: 16px 0;
  color: var(--el-color-primary);
}

.file-name {
  margin: 8px 0;
  font-size: 14px;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-info {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--el-text-color-secondary);
}

.file-actions {
  border-top: 1px solid var(--el-border-color-lighter);
  padding-top: 8px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* 表格内的图标和文字间距 */
.filename {
  margin-left: 8px;
}

/* 工具栏按钮图标间距 */
.el-button .el-icon {
  margin-right: 4px;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filename {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
  
  &:hover {
    color: var(--el-color-primary);
    background-color: var(--el-fill-color-light);
  }
}

.playing-icon {
  font-size: 14px;
  color: var(--el-color-primary);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.rename-input {
  flex: 1;
  margin-right: 8px;
}
</style>
