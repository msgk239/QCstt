<template>
  <el-dialog
    v-model="dialogVisible"
    title="热词管理"
    width="800px"
  >
    <div class="hotword-manager">
      <!-- 热词库列表 -->
      <div class="library-section">
        <div class="section-header">
          <h3>当前启用的热词库</h3>
          <div class="header-actions">
            <el-button type="primary" plain size="small" @click="handleCreateLibrary">
              <el-icon><Plus /></el-icon>新建热词库
            </el-button>
            <el-upload
              class="upload-btn"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept=".json,.txt"
              @change="handleImportLibrary"
            >
              <el-button plain size="small">
                <el-icon><Upload /></el-icon>导入
              </el-button>
            </el-upload>
            <el-button plain size="small" @click="handleExportLibrary">
              <el-icon><Download /></el-icon>导出
            </el-button>
          </div>
        </div>

        <div class="library-list">
          <el-checkbox-group v-model="enabledLibraries">
            <el-checkbox
              v-for="lib in libraries"
              :key="lib.id"
              :label="lib.id"
              border
            >
              {{ lib.name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>

        <el-alert
          v-if="enabledLibraries.length > 1"
          type="info"
          show-icon
        >
          优先级：{{ priorityText }}
        </el-alert>
      </div>

      <!-- 热词列表 -->
      <div class="hotwords-section">
        <div class="section-header">
          <h3>热词列表（已合并所有启用的热词库）</h3>
          <div class="header-actions">
            <el-button type="primary" plain size="small" @click="handleAddHotword">
              <el-icon><Plus /></el-icon>添加热词
            </el-button>
            <el-upload
              class="upload-btn"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept=".txt,.csv"
              @change="handleBatchImport"
            >
              <el-button plain size="small">
                <el-icon><Upload /></el-icon>批量导入
              </el-button>
            </el-upload>
          </div>
        </div>

        <div class="hotwords-grid">
          <el-card
            v-for="category in categories"
            :key="category.id"
            class="category-card"
            shadow="hover"
          >
            <template #header>
              <div class="card-header">
                <span>{{ category.name }}</span>
                <div class="header-actions">
                  <el-button type="primary" link @click="handleEditCategory(category)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="danger" link @click="handleDeleteCategory(category)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
            <div class="hotword-list">
              <div
                v-for="word in category.words"
                :key="word.id"
                class="hotword-item"
              >
                <span>• {{ word.text }}</span>
                <div class="item-actions">
                  <el-button type="primary" link @click="handleEditHotword(word)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="danger" link @click="handleDeleteHotword(word)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 新建/编辑热词库对话框 -->
    <el-dialog
      v-model="libraryDialogVisible"
      :title="libraryDialogTitle"
      width="400px"
      append-to-body
    >
      <el-form>
        <el-form-item label="热词库名称">
          <el-input v-model="editingLibrary.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="libraryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveLibrary">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新建/编辑热词对话框 -->
    <el-dialog
      v-model="hotwordDialogVisible"
      :title="hotwordDialogTitle"
      width="400px"
      append-to-body
    >
      <el-form>
        <el-form-item label="所属分类">
          <el-select v-model="editingHotword.categoryId">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="热词">
          <el-input v-model="editingHotword.text" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="hotwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveHotword">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Edit, Delete } from '@element-plus/icons-vue'
import {
  getHotwordLibraries,
  createHotwordLibrary,
  importHotwordLibrary,
  exportHotwordLibrary,
  deleteHotwordLibrary,
  getHotwords,
  addHotword,
  deleteHotword,
  batchAddHotwords
} from '@/api/modules/hotword'

// Props 和 Emits
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible'])

// 加载状态管理
const loadingStates = reactive({
  libraries: false,
  hotwords: false,
  creating: false,
  importing: false,
  exporting: false,
  deleting: false,
  adding: false,
  batchImporting: false
})

// 基础状态
const dialogVisible = ref(false)
const libraryDialogVisible = ref(false)
const hotwordDialogVisible = ref(false)
const libraries = ref([])
const enabledLibraries = ref([])
const categories = ref([])

// 初始化数据
const initData = async () => {
  try {
    loadingStates.libraries = true
    const res = await getHotwordLibraries()
    if (res.code === 200) {
      libraries.value = res.data
    } else {
      throw new Error(res.message || '获取热词库列表失败')
    }
  } catch (error) {
    console.error('Failed to fetch libraries:', error)
    ElMessage.error(error.message || '获取热词库列表失败')
  } finally {
    loadingStates.libraries = false
  }
}

// 创建热词库
const handleCreateLibrary = async () => {
  if (!editingLibrary.value.name.trim()) {
    ElMessage.warning('请输入热词库名称')
    return
  }

  try {
    loadingStates.creating = true
    const data = {
      name: editingLibrary.value.name,
      description: editingLibrary.value.description || ''
    }
    const res = await createHotwordLibrary(data)
    if (res.code === 200) {
      ElMessage.success('创建成功')
      libraryDialogVisible.value = false
      await initData()
    } else {
      throw new Error(res.message || '创建热词库失败')
    }
  } catch (error) {
    console.error('Failed to create library:', error)
    ElMessage.error(error.message || '创建热词库失败')
  } finally {
    loadingStates.creating = false
  }
}

// 导入热词库
const handleImportLibrary = async (file) => {
  // 文件类型检查
  const allowedTypes = ['.json', '.txt']
  const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  if (!allowedTypes.includes(fileExt)) {
    ElMessage.error(`仅支持 ${allowedTypes.join('/')} 格式文件`)
    return
  }

  try {
    loadingStates.importing = true
    const res = await importHotwordLibrary(file.raw)
    if (res.code === 200) {
      ElMessage.success(`导入成功，共 ${res.data.word_count} 个热词`)
      await initData()
    } else {
      throw new Error(res.message || '导入热词库失败')
    }
  } catch (error) {
    console.error('Failed to import library:', error)
    ElMessage.error(error.message || '导入热词库失败')
  } finally {
    loadingStates.importing = false
  }
}

// 删除热词库
const handleDeleteLibrary = async (libraryId) => {
  try {
    await ElMessageBox.confirm('确定要删除该热词库吗？', '提示', {
      type: 'warning'
    })
    
    loadingStates.deleting = true
    const res = await deleteHotwordLibrary(libraryId)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      // 如果删除的是当前启用的热词库，清空选择
      if (enabledLibraries.value.includes(libraryId)) {
        enabledLibraries.value = enabledLibraries.value.filter(id => id !== libraryId)
      }
      await initData()
    } else {
      throw new Error(res.message || '删除热词库失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete library:', error)
      ElMessage.error(error.message || '删除热词库失败')
    }
  } finally {
    loadingStates.deleting = false
  }
}

// 获取热词列表
const fetchHotwords = async (libraryId) => {
  try {
    loadingStates.hotwords = true
    const res = await getHotwords(libraryId)
    if (res.code === 200) {
      // 按分类组织热词
      const wordsByCategory = {}
      res.data.forEach(word => {
        if (!wordsByCategory[word.category]) {
          wordsByCategory[word.category] = []
        }
        wordsByCategory[word.category].push(word)
      })
      
      categories.value = Object.entries(wordsByCategory).map(([name, words]) => ({
        id: name,
        name,
        words: words.sort((a, b) => a.text.localeCompare(b.text))
      })).sort((a, b) => a.name.localeCompare(b.name))
    } else {
      throw new Error(res.message || '获取热词列表失败')
    }
  } catch (error) {
    console.error('Failed to fetch hotwords:', error)
    ElMessage.error(error.message || '获取热词列表失败')
  } finally {
    loadingStates.hotwords = false
  }
}

// 添加热词
const handleAddHotword = async () => {
  if (!editingHotword.value.text.trim()) {
    ElMessage.warning('请输入热词')
    return
  }
  if (!editingHotword.value.categoryId) {
    ElMessage.warning('请选择分类')
    return
  }
  if (!enabledLibraries.value.length) {
    ElMessage.warning('请先选择热词库')
    return
  }

  try {
    loadingStates.adding = true
    const libraryId = enabledLibraries.value[0]
    const data = {
      text: editingHotword.value.text.trim(),
      category: editingHotword.value.categoryId
    }
    const res = await addHotword(libraryId, data)
    if (res.code === 200) {
      ElMessage.success('添加成功')
      hotwordDialogVisible.value = false
      await fetchHotwords(libraryId)
    } else {
      throw new Error(res.message || '添加热词失败')
    }
  } catch (error) {
    console.error('Failed to add hotword:', error)
    ElMessage.error(error.message || '添加热词失败')
  } finally {
    loadingStates.adding = false
  }
}

// 删除热词
const handleDeleteHotword = async (wordId) => {
  try {
    await ElMessageBox.confirm('确定要删除该热词吗？', '提示', {
      type: 'warning'
    })
    
    loadingStates.deleting = true
    const res = await deleteHotword(wordId)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      if (enabledLibraries.value.length) {
        await fetchHotwords(enabledLibraries.value[0])
      }
    } else {
      throw new Error(res.message || '删除热词失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete hotword:', error)
      ElMessage.error(error.message || '删除热词失败')
    }
  } finally {
    loadingStates.deleting = false
  }
}

// 批量导入热词
const handleBatchImport = async (file) => {
  // 文件类型检查
  if (!file.name.endsWith('.txt')) {
    ElMessage.error('请上传 txt 文件')
    return
  }
  if (!enabledLibraries.value.length) {
    ElMessage.warning('请先选择热词库')
    return
  }

  try {
    loadingStates.batchImporting = true
    const text = await file.text()
    const words = text.split('\n')
      .map(line => line.trim())
      .filter(line => line)
      .map(text => ({
        text,
        category: '导入'
      }))

    if (words.length === 0) {
      ElMessage.warning('文件内容为空')
      return
    }

    const libraryId = enabledLibraries.value[0]
    const res = await batchAddHotwords(libraryId, words)
    if (res.code === 200) {
      ElMessage.success(`导入成功，成功 ${res.data.success_count} 个，失败 ${res.data.fail_count} 个`)
      await fetchHotwords(libraryId)
    } else {
      throw new Error(res.message || '批量导入失败')
    }
  } catch (error) {
    console.error('Failed to batch import:', error)
    ElMessage.error(error.message || '批量导入失败')
  } finally {
    loadingStates.batchImporting = false
  }
}

// 监听对话框显示
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    initData()
  }
})

// 监听选中的热词库变化
watch(enabledLibraries, (val) => {
  if (val.length) {
    fetchHotwords(val[0])
  } else {
    categories.value = []
  }
})

// 编辑状态
const editingLibrary = ref({ name: '', description: '' })
const editingHotword = ref({ categoryId: null, text: '' })

// 计算属性
const libraryDialogTitle = computed(() => {
  return editingLibrary.value.id ? '编辑热词库' : '新建热词库'
})

const hotwordDialogTitle = computed(() => {
  return editingHotword.value.id ? '编辑热词' : '添加热词'
})

const priorityText = computed(() => {
  return enabledLibraries.value
    .map(id => libraries.value.find(lib => lib.id === id)?.name)
    .filter(Boolean)
    .join(' > ')
})

// 分类相关方法
const handleEditCategory = (category) => {
  // TODO: 实现编辑分类逻辑
}

const handleDeleteCategory = (category) => {
  // TODO: 实现删除分类逻辑
  ElMessage.success('删除成功')
}
</script>

<style scoped>
.hotword-manager {
  height: 600px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.library-list {
  margin: 16px 0;
}

.library-list .el-checkbox {
  margin-right: 16px;
  margin-bottom: 16px;
}

.hotwords-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.category-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hotword-list {
  max-height: 200px;
  overflow-y: auto;
}

.hotword-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.item-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.hotword-item:hover .item-actions {
  opacity: 1;
}

:deep(.el-upload) {
  display: block;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style> 