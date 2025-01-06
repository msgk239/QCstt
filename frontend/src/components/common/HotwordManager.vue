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
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Upload, Download, Edit, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible'])

// 状态
const dialogVisible = ref(false)
const libraryDialogVisible = ref(false)
const hotwordDialogVisible = ref(false)
const libraries = ref([
  { id: 1, name: '默认热词库' },
  { id: 2, name: '医疗术语库' },
  { id: 3, name: 'IT术语库' },
  { id: 4, name: '金融术语库' }
])
const enabledLibraries = ref([1, 2])
const categories = ref([
  {
    id: 1,
    name: '专业术语',
    words: [
      { id: 1, text: 'OpenAI' },
      { id: 2, text: 'ChatGPT' }
    ]
  },
  {
    id: 2,
    name: '人名地名',
    words: [
      { id: 3, text: '张三' },
      { id: 4, text: '北京' }
    ]
  }
])

// 编辑状态
const editingLibrary = ref({ name: '' })
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

// 监听对话框可见性
watch(() => props.visible, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 热词库相关方法
const handleCreateLibrary = () => {
  editingLibrary.value = { name: '' }
  libraryDialogVisible.value = true
}

const handleImportLibrary = (file) => {
  // TODO: 实现导入逻辑
  ElMessage.success('导入成功')
}

const handleExportLibrary = () => {
  // TODO: 实现导出逻辑
  ElMessage.success('导出成功')
}

const handleSaveLibrary = () => {
  if (!editingLibrary.value.name) {
    ElMessage.warning('请输入热词库名称')
    return
  }

  // TODO: 实现保存逻辑
  libraryDialogVisible.value = false
  ElMessage.success('保存成功')
}

// 热词相关方法
const handleAddHotword = () => {
  editingHotword.value = {
    categoryId: categories.value[0]?.id,
    text: ''
  }
  hotwordDialogVisible.value = true
}

const handleEditHotword = (word) => {
  const category = categories.value.find(c =>
    c.words.some(w => w.id === word.id)
  )
  editingHotword.value = {
    ...word,
    categoryId: category?.id
  }
  hotwordDialogVisible.value = true
}

const handleDeleteHotword = (word) => {
  // TODO: 实现删除逻辑
  ElMessage.success('删除成功')
}

const handleSaveHotword = () => {
  if (!editingHotword.value.categoryId || !editingHotword.value.text) {
    ElMessage.warning('请填写完整信息')
    return
  }

  // TODO: 实现保存逻辑
  hotwordDialogVisible.value = false
  ElMessage.success('保存成功')
}

const handleBatchImport = (file) => {
  // TODO: 实现批量导入逻辑
  ElMessage.success('导入成功')
}

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