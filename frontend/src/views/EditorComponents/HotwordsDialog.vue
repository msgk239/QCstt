<template>
  <el-dialog
    v-model="visible"
    title="热词库管理"
    width="800px"
  >
    <div class="hotwords-manager">
      <div class="enabled-libraries">
        <h3>当前启用的热词库：</h3>
        <el-checkbox-group v-model="enabledLibraries">
          <el-checkbox v-for="lib in hotwordLibraries" 
                      :key="lib.id" 
                      :label="lib.id">
            {{ lib.name }}
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <div class="library-actions">
        <el-button-group>
          <el-button @click="createLibrary">新建热词库</el-button>
          <el-button @click="importLibrary">导入</el-button>
          <el-button @click="exportLibrary">导出</el-button>
        </el-button-group>
      </div>

      <div class="hotwords-list">
        <h3>热词列表：</h3>
        <div class="category-cards">
          <el-card v-for="category in hotwordCategories" 
                  :key="category.id" 
                  class="category-card">
            <template #header>
              <div class="card-header">
                <span>{{ category.name }}</span>
                <div class="card-actions">
                  <el-button link @click="editCategory(category)">编辑</el-button>
                  <el-button link type="danger" @click="deleteCategory(category)">删除</el-button>
                </div>
              </div>
            </template>
            <div class="hotword-items">
              <div v-for="word in category.words" 
                   :key="word.id" 
                   class="hotword-item">
                • {{ word.text }}
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const enabledLibraries = ref(['default', 'medical'])
const hotwordLibraries = ref([
  { id: 'default', name: '默认热词库' },
  { id: 'medical', name: '医疗术语库' },
  { id: 'it', name: 'IT术语库' },
  { id: 'finance', name: '金融术语库' }
])

const hotwordCategories = ref([
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

// 方法
const createLibrary = () => {
  // 创建热词库逻辑
}

const importLibrary = () => {
  // 导入热词库逻辑
}

const exportLibrary = () => {
  // 导出热词库逻辑
}

const editCategory = (category) => {
  // 编辑分类逻辑
}

const deleteCategory = (category) => {
  // 删除分类逻辑
}
</script>

<style scoped>
.hotwords-manager {
  padding: 16px;
}

.enabled-libraries {
  margin-bottom: 24px;
}

.library-actions {
  margin-bottom: 24px;
}

.category-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hotword-item {
  padding: 4px 0;
}
</style> 