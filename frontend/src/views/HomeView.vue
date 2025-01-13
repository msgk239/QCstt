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
              <div v-if="row.isRenaming" class="rename-input">
                <el-input
                  v-model="row.newName"
                  size="small"
                  @blur="handleRenameConfirm(row)"
                  @keyup.enter="handleRenameConfirm(row)"
                  @keyup.esc="handleRenameCancel(row)"
                />
              </div>
              <span v-else class="filename" :title="row.name">
                {{ formatDisplayName(row.name) }}
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
            <el-tag size="small" type="info">{{ formatDuration(row.duration) }}</el-tag>
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
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-tooltip content="重命名" placement="top">
                <el-button 
                  type="primary" 
                  link
                  :loading="operationStates.rename"
                  @click="handleRenameStart(row)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-dropdown trigger="click">
                <el-button type="primary" link>
                  <el-icon><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleCopyPath(row)">
                      <el-icon><DocumentCopy /></el-icon>复制文件路径
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleShowPath(row)">
                      <el-icon><FolderOpened /></el-icon>查看文件位置
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleExport(row)">
                      <el-icon><Download /></el-icon>导出文件
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>

              <el-button 
                type="primary" 
                link 
                :loading="operationStates.recognize"
                :disabled="row.status !== '已上传'"
                @click="startRecognition(row)"
              >
                开始识别
              </el-button>
              <el-button 
                type="danger" 
                link 
                :loading="operationStates.delete"
                @click="handleDeleteFile(row)"
              >
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
            <el-tag size="small" type="info">{{ formatDuration(file.duration) }}</el-tag>
            <el-tag size="small" :type="getStatusType(file.status)">
              {{ file.status }}
            </el-tag>
          </div>
          <div class="file-actions">
            <el-button-group>
              <el-tooltip content="重命名" placement="top">
                <el-button 
                  type="primary" 
                  link
                  :loading="operationStates.rename"
                  @click="handleRenameStart(file)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-button 
                type="primary" 
                link 
                :loading="operationStates.recognize"
                :disabled="file.status !== '已上传'"
                @click="startRecognition(file)"
              >
                开始识别
              </el-button>
              <el-button 
                type="primary" 
                link
                @click="handleExport(file)"
              >
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button 
                type="danger" 
                link 
                :loading="operationStates.delete"
                @click="handleDeleteFile(file)"
              >
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
          :pager-count="7"
          prev-text="上一页"
          next-text="下一页"
          :sizes-text="'条/页'"
          :total-text="'共 {total} 条'"
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
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as asrApi from '@/api/modules/asr'
import FileUpload from '@/components/file/FileUpload.vue'
import { useRouter } from 'vue-router'
import { useFileStore } from '@/stores/fileStore'
import { storeToRefs } from 'pinia'
import { debounce } from 'lodash-es'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { formatFileSize, formatDuration, formatDisplayName } from '@/utils/format'

// 设置 Element Plus 的语言为中文
const locale = zhCn

const router = useRouter()
const fileStore = useFileStore()

// 从 store 中获取状态
const { 
  fileList, 
  totalFiles, 
  loading, 
  viewMode, 
  searchQuery, 
  currentPage, 
  pageSize,
  operationStates,
  uploadDialogVisible 
} = storeToRefs(fileStore)

// 获取文件列表的防抖处理
const debouncedFetchFiles = debounce(() => {
  fileStore.fetchFileList({
    page: currentPage.value,
    page_size: pageSize.value,
    query: searchQuery.value
  })
}, 300)

// 监听分页和搜索变化
watch(
  () => [currentPage.value, pageSize.value, searchQuery.value],
  () => {
    debouncedFetchFiles()
  }
)

// 监听视图模式变化
watch(viewMode, () => {
  fileStore.saveViewMode()
})

// 计算属性：过滤后的文件列表
const filteredFiles = computed(() => {
  if (!fileList.value) return []
  
  return fileList.value
    .filter(file => !file.status || file.status === '已上传' || file.status === '识别中' || file.status === '已完成' || file.status === '失败')
    .map(file => ({
      ...file,
      displayName: formatDisplayName(file.name),
      statusType: getStatusType(file.status),
      formattedSize: formatFileSize(file.size),
      formattedDuration: formatDuration(file.duration)
    }))
})

// 修改显示对话框方法
const showUploadDialog = () => {
  uploadDialogVisible.value = true
}

// 上传回调处理
const handleUploadSuccess = async ({ files, options }) => {
  console.log('Upload success:', { files, options })
  await fileStore.fetchFileList()
  ElMessage.success(`成功上传 ${files.length} 个文件`)
}

const handleUploadError = (error) => {
  console.error('Upload error:', error)
  ElMessage.error(error.message || '文件上传失败')
}

// 删除文件
const handleDeleteFile = async (file) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该文件吗？删除后可在回收站恢复',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await fileStore.deleteFile(file.id)
    ElMessage.success('文件已移至回收站')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete file error:', error)
      ElMessage.error(error.message || '删除文件失败')
    }
  }
}

// 开始识别
const startRecognition = async (file) => {
  console.log('开始识别文件:', file)
  
  if (!file?.file_id) {
    console.warn('文件对象:', file)
    ElMessage.error('文件ID不存在')
    return
  }

  try {
    console.log('发送识别请求, ID:', file.file_id)
    const response = await fileStore.startRecognition(file.file_id)
    console.log('识别请求响应:', response)
    
    if (response.code === 200) {
      // 使用 Promise 和 async/await 优化轮询逻辑
      const pollRecognitionStatus = async () => {
        const progress = await asrApi.getRecognizeProgress(file.file_id)
        console.log('识别进度响应:', progress)
        
        if (progress.code === 200) {
          const { status } = progress.data
          console.log('当前识别状态:', status)
          
          if (status === '已完成') {
            ElMessage.success('识别完成')
            try {
              console.log('准备跳转到编辑页面，file_id:', file.file_id)
              await router.push({
                name: 'editor',
                params: { id: file.file_id }
              })
              console.log('跳转成功')
              return true
            } catch (error) {
              console.error('路由跳转失败:', error)
              ElMessage.error('跳转到编辑页面失败')
              throw error
            }
          } else if (status === '识别中') {
            await new Promise(resolve => setTimeout(resolve, 1000))
            return pollRecognitionStatus()
          } else {
            throw new Error(`识别异常：${status}`)
          }
        }
        throw new Error(progress.message || '获取识别状态失败')
      }
      
      await pollRecognitionStatus()
    } else {
      throw new Error(response.message || '开始识别失败')
    }
  } catch (error) {
    console.error('识别请求失败:', error)
    ElMessage.error(error.message || '识别失败，请重试')
  }
}

// 重命名处理
const handleRename = async (file) => {
  try {
    const { value: newName } = await ElMessageBox.prompt(
      '请输入新的文件名',
      '重命名',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: formatDisplayName(file.name),
        inputValidator: (value) => {
          if (!value.trim()) {
            return '文件名不能为空'
          }
          if (value.includes('/') || value.includes('\\')) {
            return '文件名不能包含特殊字符'
          }
          return true
        }
      }
    )
    
    if (newName && newName !== file.name) {
      await fileStore.renameFile(file.id, newName)
      ElMessage.success('重命名成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Rename error:', error)
      ElMessage.error(error.message || '重命名失败')
    }
  }
}

// 导出文件
const handleExport = async (file) => {
  try {
    await fileStore.exportFile(file.id, file.name)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const getStatusType = (status) => {
  const statusMap = {
    '已上传': 'info',
    '待识别': 'warning',
    '识别中': 'primary',
    '已完成': 'success',
    '失败': 'danger'
  }
  return statusMap[status] || 'info'
}

// 文件路径相关功能
const handleCopyPath = async (file) => {
  try {
    const response = await asrApi.getFilePath(file.id)
    if (response.code === 200) {
      const path = response.data.path
      await navigator.clipboard.writeText(path)
      ElMessage.success('文件路径已复制到剪贴板')
    } else {
      throw new Error(response.message || '获取文件路径失败')
    }
  } catch (error) {
    console.error('Copy path error:', error)
    ElMessage.error(error.message || '复制文件路径失败')
  }
}

const handleShowPath = async (file) => {
  try {
    const response = await asrApi.getFilePath(file.id)
    if (response.code === 200) {
      const path = response.data.path
      // 使用 electron 的 shell.showItemInFolder
      window.electron?.showItemInFolder(path)
    } else {
      throw new Error(response.message || '获取文件路径失败')
    }
  } catch (error) {
    console.error('Show path error:', error)
    ElMessage.error(error.message || '打开文件位置失败')
  }
}

// 表格视图中的行内重命名功能
const handleRenameStart = (file) => {
  file.isRenaming = true
  file.newName = formatDisplayName(file.name)
}

const handleRenameConfirm = async (file) => {
  try {
    if (!file.newName?.trim()) {
      ElMessage.warning('文件名不能为空')
      return
    }
    if (file.newName === formatDisplayName(file.name)) {
      file.isRenaming = false
      return
    }

    loadingStates.rename = true
    await fileStore.renameFile(file.id, file.newName)
    ElMessage.success('重命名成功')
  } catch (error) {
    console.error('Rename error:', error)
    ElMessage.error(error.message || '重命名失败')
  } finally {
    file.isRenaming = false
    loadingStates.rename = false
  }
}

const handleRenameCancel = (file) => {
  file.isRenaming = false
  file.newName = formatDisplayName(file.name)
}

// 初始化
onMounted(() => {
  debouncedFetchFiles()
})
</script>

<style scoped>
.home-view {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.toolbar-left {
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
}

.search-input {
  width: 300px;
  max-width: 100%;
}

.file-list {
  flex: 1;
  overflow: auto;
  min-height: 0;
}

.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  padding: 16px;
}

.file-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
}

.file-icon {
  margin-bottom: 8px;
}

.file-name {
  margin: 8px 0;
  text-align: center;
  word-break: break-word;
}

.file-info {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.file-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.file-card:hover .file-actions {
  opacity: 1;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .grid-view {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rename-input {
  flex: 1;
  margin-right: 8px;
}

.filename {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.filename:hover {
  color: var(--el-color-primary);
  background-color: var(--el-fill-color-light);
}
</style>
