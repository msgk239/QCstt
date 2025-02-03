<template>
  <div class="version-history-toolbar">
    <!-- 手动保存按钮 -->
    <el-button type="primary" @click="handleManualSave" :loading="saving">
      <el-icon><Document /></el-icon>保存版本
    </el-button>

    <el-dropdown trigger="click">
      <el-button>
        历史版本<el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item>
            <div class="version-item">
              <div class="version-info">
                <span class="version-time">当前版本</span>
                <span class="version-meta">{{ formatDateTime(new Date()) }}</span>
              </div>
              <div class="version-actions">
                <el-button size="small">预览</el-button>
              </div>
            </div>
          </el-dropdown-item>
          <el-dropdown-item v-for="version in versions" :key="version.id">
            <div class="version-item">
              <div class="version-info">
                <span class="version-time">{{ formatTimeAgo(version.timestamp) }}</span>
                <span class="version-meta">{{ formatDateTime(version.timestamp) }}</span>
              </div>
              <div class="version-actions">
                <el-button size="small" @click="handlePreview(version)">预览</el-button>
                <el-button size="small" type="primary" @click="handleRestore(version)">还原</el-button>
              </div>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document, ArrowDown } from '@element-plus/icons-vue'
import { editorBus, EVENT_TYPES } from './eventBus'
import { fileApi } from '@/api/modules/file'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const saving = ref(false)
const versions = ref([])

// 加载版本列表
const loadVersions = async () => {
  try {
    const response = await fileApi.getVersions(route.params.id)
    if (response.code === 200 && response.data) {
      versions.value = response.data.map(version => ({
        ...version,
        timestamp: new Date(version.timestamp)
      }))
    }
  } catch (error) {
    console.error('加载版本列表失败:', error)
    ElMessage.error('加载版本列表失败')
  }
}

// 监听版本保存完成事件
editorBus.on(EVENT_TYPES.VERSION_SAVED, async (savedVersion) => {
  if (savedVersion) {
    await loadVersions() // 重新加载版本列表
  }
})

// 手动保存
const handleManualSave = async () => {
  if (saving.value) return
  
  saving.value = true
  let savedHandler = null
  let timeoutId = null

  try {
    // 触发保存事件，让编辑器组件处理保存逻辑
    editorBus.emit(EVENT_TYPES.SAVE_VERSION, {
      type: 'manual',
      timestamp: new Date()
    })
    
    // 等待保存完成
    await new Promise((resolve, reject) => {
      savedHandler = (savedVersion) => {
        if (timeoutId) {
          clearTimeout(timeoutId)
        }
        resolve(savedVersion)
      }

      timeoutId = setTimeout(() => {
        reject(new Error('保存超时'))
      }, 30000) // 30秒超时

      editorBus.on(EVENT_TYPES.VERSION_SAVED, savedHandler)
    })

    await loadVersions() // 重新加载版本列表
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    if (savedHandler) {
      editorBus.off(EVENT_TYPES.VERSION_SAVED, savedHandler)
    }
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    saving.value = false
  }
}

const handlePreview = async (version) => {
  try {
    const response = await fileApi.getVersion(route.params.id, version.id)
    if (response.code === 200 && response.data) {
      editorBus.emit(EVENT_TYPES.LOAD_VERSION, {
        ...response.data,
        mode: 'preview'
      })
    }
  } catch (error) {
    console.error('加载版本失败:', error)
    ElMessage.error('加载版本失败')
  }
}

const handleRestore = async (version) => {
  try {
    const response = await fileApi.getVersion(route.params.id, version.id)
    if (response.code === 200 && response.data) {
      editorBus.emit(EVENT_TYPES.LOAD_VERSION, {
        ...response.data,
        mode: 'restore'
      })
    }
  } catch (error) {
    console.error('还原版本失败:', error)
    ElMessage.error('还原版本失败')
  }
}

// 在组件挂载时加载版本列表
onMounted(() => {
  loadVersions()
})

// 格式化时间为"x分钟前"的形式
const formatTimeAgo = (timestamp) => {
  const now = new Date()
  const diff = now - new Date(timestamp)
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}

// 格式化日期时间
const formatDateTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.version-history-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 4px 0;
  min-width: 400px;
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.version-time {
  font-weight: 500;
}

.version-meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.version-actions {
  display: flex;
  gap: 8px;
}
</style> 