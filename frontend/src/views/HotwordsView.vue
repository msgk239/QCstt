<template>
  <div class="hotwords-container">
    <div class="header">
      <h2>热词管理</h2>
      <div class="actions">
        <el-button 
          type="primary" 
          :loading="hotwordStore.saving"
          :disabled="!hotwordStore.isValid"
          @click="handleSave"
        >
          保存
        </el-button>
      </div>
    </div>

    <div class="editor-container">
      <el-input
        v-model="content"
        type="textarea"
        :rows="20"
        :loading="hotwordStore.loading"
        @input="handleContentChange"
        placeholder="请输入热词配置，每行一个"
      />
    </div>

    <div v-if="hotwordStore.errors.length" class="error-list">
      <h3>格式错误：</h3>
      <el-alert
        v-for="error in hotwordStore.errors"
        :key="error.line"
        :title="`第 ${error.line} 行: ${error.message}`"
        :description="error.content"
        type="error"
        show-icon
        :closable="false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useHotwordStore } from '@/stores/hotwordStore'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'

const hotwordStore = useHotwordStore()
const { content: storeContent } = storeToRefs(hotwordStore)
const content = ref('')

// 内容变化时进行验证
const handleContentChange = async (value) => {
  try {
    await hotwordStore.validateContent(value)
  } catch (error) {
    console.error('验证失败:', error)
  }
}

// 保存内容
const handleSave = async () => {
  try {
    await hotwordStore.saveContent(content.value)
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
  }
}

// 组件加载时获取内容
onMounted(async () => {
  try {
    await hotwordStore.fetchContent()
    content.value = storeContent.value
  } catch (error) {
    console.error('获取内容失败:', error)
  }
})
</script>

<style scoped>
.hotwords-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 {
  margin: 0;
}

.editor-container {
  flex: 1;
}

.error-list {
  margin-top: 20px;
}

.error-list h3 {
  margin-bottom: 10px;
  color: var(--el-color-danger);
}

:deep(.el-alert) {
  margin-bottom: 8px;
}

:deep(.el-textarea__inner) {
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style> 