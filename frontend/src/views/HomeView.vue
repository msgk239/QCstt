<template>
  <div class="home-view">
    <!-- 上传区域 -->
    <el-card class="upload-area" v-show="!fileList.length">
      <el-upload
        class="upload-dragger"
        drag
        action="#"
        :auto-upload="false"
        :show-file-list="false"
        @change="handleFileChange"
      >
        <el-icon class="upload-icon"><Upload /></el-icon>
        <div class="upload-text">
          <h3>将文件拖到此处或点击上传</h3>
          <p>支持 WAV、MP3、FLAC、OGG 格式</p>
        </div>
      </el-upload>
    </el-card>

    <!-- 文件列表 -->
    <div class="file-list" v-show="fileList.length">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-radio-group v-model="viewMode" size="large">
            <el-radio-button label="list">
              <el-icon><List /></el-icon>
            </el-radio-button>
            <el-radio-button label="grid">
              <el-icon><Grid /></el-icon>
            </el-radio-button>
          </el-radio-group>

          <el-input
            v-model="searchQuery"
            placeholder="搜索文件..."
            prefix-icon="Search"
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
      >
        <el-table-column prop="name" label="文件名" min-width="200">
          <template #default="{ row }">
            <el-icon><Document /></el-icon>
            <span class="filename">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已完成' ? 'success' : 'warning'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="修改日期" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link>
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="primary" link>
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button type="danger" link>
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
            <span>{{ file.duration }}</span>
            <el-tag size="small" :type="file.status === '已完成' ? 'success' : 'warning'">
              {{ file.status }}
            </el-tag>
          </div>
          <div class="file-actions">
            <el-button-group>
              <el-button type="primary" link>
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="primary" link>
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button type="danger" link>
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
import { ref, computed } from 'vue'
import FileUpload from '@/components/file/FileUpload.vue'
import {
  Upload,
  Document,
  Edit,
  Download,
  Delete,
  Plus,
  Search,
  Filter,
  List,
  Grid
} from '@element-plus/icons-vue'

// 视图模式
const viewMode = ref('list')

// 搜索和筛选
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 模拟数据
const fileList = ref([
  {
    id: 1,
    name: '会议记录.mp3',
    duration: '2小时15分',
    status: '已完成',
    date: '2024-03-10 14:30'
  },
  {
    id: 2,
    name: '访谈录音.wav',
    duration: '45分钟',
    status: '处理中',
    date: '2024-03-09 16:20'
  }
])

// 计算属性
const filteredFiles = computed(() => {
  return fileList.value.filter(file =>
    file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const totalFiles = computed(() => filteredFiles.value.length)

// 方法
const handleFileChange = (file) => {
  console.log('File selected:', file)
}

// 上传对话框
const uploadDialogVisible = ref(false)

const showUploadDialog = () => {
  uploadDialogVisible.value = true
}

const handleUploadSuccess = (files) => {
  // TODO: 处理上传成功的文件
  console.log('Upload success:', files)
}

const handleUploadError = (error) => {
  console.error('Upload error:', error)
}
</script>

<style scoped>
.home-view {
  padding: 20px;
  height: 100%;
}

.upload-area {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-dragger {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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
</style>
