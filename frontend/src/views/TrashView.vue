<template>
  <div class="trash-view">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="danger" :disabled="!selectedFiles.length" @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>永久删除
        </el-button>
        <el-button type="primary" :disabled="!selectedFiles.length" @click="handleBatchRestore">
          <el-icon><RefreshLeft /></el-icon>恢复文件
        </el-button>
        
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件..."
          clearable
          @input="handleSearch"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="toolbar-right">
        <el-button type="danger" @click="handleClearTrash">
          清空回收站
        </el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="files"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="文件名" min-width="200">
        <template #default="{ row }">
          <el-icon><Document /></el-icon>
          <span class="filename">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="时长" width="120" />
      <el-table-column prop="date" label="删除日期" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button type="primary" link @click="handleRestore(row)">
              <el-icon><RefreshLeft /></el-icon>
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 确认对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="400px"
    >
      <span>{{ dialogMessage }}</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleDialogConfirm">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document, Delete, RefreshLeft, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as trashApi from '@/api/modules/trash'

// 状态
const loading = ref(false)
const files = ref([])
const selectedFiles = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchQuery = ref('')

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')
const dialogCallback = ref(null)

// 方法
const fetchFiles = async () => {
  loading.value = true
  try {
    console.log('Fetching trash files with params:', {
      page: currentPage.value,
      page_size: pageSize.value,
      query: searchQuery.value
    })
    
    const res = await trashApi.getTrashList({
      page: currentPage.value,
      page_size: pageSize.value,
      query: searchQuery.value || undefined
    })
    
    console.log('Trash API response:', res)
    console.log('Response data structure:', {
      code: res.code,
      message: res.message,
      data: res.data
    })
    
    if (res.code === 200) {
      console.log('Trash items before mapping:', res.data.items)
      files.value = res.data.items.map(file => ({
        ...file,
        duration: '计算中...'
      }))
      console.log('Trash items after mapping:', files.value)
      total.value = res.data.total
      console.log('Total files:', total.value)
    } else {
      console.error('API error:', res)
      ElMessage.error(res.message || '获取文件列表失败')
    }
  } catch (error) {
    console.error('Failed to fetch files:', error)
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedFiles.value = selection
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchFiles()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchFiles()
}

const showConfirmDialog = (title, message, callback) => {
  dialogTitle.value = title
  dialogMessage.value = message
  dialogCallback.value = callback
  dialogVisible.value = true
}

const handleDialogConfirm = async () => {
  dialogVisible.value = false
  if (dialogCallback.value) {
    await dialogCallback.value()
  }
}

const handleRestore = (file) => {
  showConfirmDialog(
    '恢复文件',
    `确定要恢复文件 "${file.name}" 吗？`,
    async () => {
      try {
        const res = await trashApi.restoreFile(file.id)
        if (res.code === 200) {
          ElMessage.success('文件已恢复')
          fetchFiles()
        } else {
          ElMessage.error(res.message || '恢复文件失败')
        }
      } catch (error) {
        console.error('Failed to restore file:', error)
        ElMessage.error('恢复文件失败')
      }
    }
  )
}

const handleDelete = (file) => {
  showConfirmDialog(
    '永久删除',
    `文件 "${file.name}" 将被永久删除，无法恢复，是否继续？`,
    async () => {
      try {
        const res = await trashApi.permanentlyDeleteFile(file.id)
        if (res.code === 200) {
          ElMessage.success('文件已永久删除')
          fetchFiles()
        } else {
          ElMessage.error(res.message || '删除文件失败')
        }
      } catch (error) {
        console.error('Failed to delete file:', error)
        ElMessage.error('删除文件失败')
      }
    }
  )
}

const handleBatchRestore = () => {
  if (!selectedFiles.value.length) return
  
  showConfirmDialog(
    '批量恢复',
    `确定要恢复选中的 ${selectedFiles.value.length} 个文件吗？`,
    async () => {
      try {
        const promises = selectedFiles.value.map(file => trashApi.restoreFile(file.id))
        const results = await Promise.all(promises)
        if (results.every(res => res.code === 200)) {
          ElMessage.success('文件已恢复')
          fetchFiles()
        } else {
          ElMessage.warning('部分文件恢复失败')
        }
      } catch (error) {
        console.error('Failed to restore files:', error)
        ElMessage.error('恢复文件失败')
      }
    }
  )
}

const handleBatchDelete = () => {
  if (!selectedFiles.value.length) return

  showConfirmDialog(
    '批量删除',
    `选中的 ${selectedFiles.value.length} 个文件将被永久删除，无法恢复，是否继续？`,
    async () => {
      try {
        const promises = selectedFiles.value.map(file => trashApi.permanentlyDeleteFile(file.id))
        const results = await Promise.all(promises)
        if (results.every(res => res.code === 200)) {
          ElMessage.success('文件已永久删除')
          fetchFiles()
        } else {
          ElMessage.warning('部分文件删除失败')
        }
      } catch (error) {
        console.error('Failed to delete files:', error)
        ElMessage.error('删除文件失败')
      }
    }
  )
}

const handleClearTrash = () => {
  if (!files.value.length) return

  showConfirmDialog(
    '清空回收站',
    '回收站中的所有文件将被永久删除，无法恢复，是否继续？',
    async () => {
      try {
        const res = await trashApi.clearTrash()
        if (res.code === 200) {
          ElMessage.success('回收站已清空')
          fetchFiles()
        } else {
          ElMessage.error(res.message || '清空回收站失败')
        }
      } catch (error) {
        console.error('Failed to clear trash:', error)
        ElMessage.error('清空回收站失败')
      }
    }
  )
}

const handleSearch = () => {
  currentPage.value = 1
  fetchFiles()
}

// 生命周期
onMounted(() => {
  fetchFiles()
})
</script>

<style scoped>
.trash-view {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input {
  width: 300px;
  margin-left: 16px;
}

.filename {
  margin-left: 8px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* 工具栏按钮图标间距 */
.el-button .el-icon {
  margin-right: 4px;
}
</style>
