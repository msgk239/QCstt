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
      <div 
        ref="editorRef" 
        class="editor" 
        :class="{ 'is-loading': hotwordStore.loading }"
      ></div>
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useHotwordStore } from '@/stores/hotwordStore'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { EditorState } from '@codemirror/state'
import { EditorView, lineNumbers, keymap } from '@codemirror/view'
import { defaultKeymap } from '@codemirror/commands'

const hotwordStore = useHotwordStore()
const { content: storeContent } = storeToRefs(hotwordStore)
const editorRef = ref(null)
let editorView = null

// 创建编辑器实例
const createEditor = (content = '') => {
  const startState = EditorState.create({
    doc: content,
    extensions: [
      lineNumbers(),
      EditorView.lineWrapping,
      keymap.of(defaultKeymap),
      EditorView.updateListener.of(update => {
        if (update.docChanged) {
          handleContentChange(update.state.doc.toString())
        }
      })
    ]
  })

  editorView = new EditorView({
    state: startState,
    parent: editorRef.value
  })
}

// 内容变化时进行验证
const handleContentChange = async (value) => {
  try {
    console.debug('内容变化，当前值:', value)
    await hotwordStore.validateContent(value)
  } catch (error) {
    console.error('验证失败:', error)
  }
}

// 保存内容
const handleSave = async () => {
  try {
    const content = editorView.state.doc.toString()
    console.debug('准备保存的内容:', content)
    console.info('开始保存热词内容...')
    await hotwordStore.saveContent(content)
    console.info('热词内容保存成功')
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error(`保存失败: ${error.message || '未知错误'}`)
  }
}

onMounted(async () => {
  try {
    console.info('开始加载热词内容...')
    await hotwordStore.fetchContent()
    createEditor(storeContent.value)
    console.debug('初始化的内容:', storeContent.value)
    console.info('热词内容加载成功')
  } catch (error) {
    console.error('获取内容失败:', error)
    ElMessage.error(`加载失败: ${error.message || '未知错误'}`)
  }
})

onBeforeUnmount(() => {
  if (editorView) {
    editorView.destroy()
  }
})
</script>

<style scoped>
.hotwords-container {
  padding: 20px;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background-color: #fff;
  z-index: 1;
  padding: 10px 0;
}

.header h2 {
  margin: 0;
}

.editor-container {
  flex: 1;
  height: 100%;
  display: flex;
}

.editor {
  width: 100%;
  height: 100%;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}

.editor.is-loading {
  opacity: 0.7;
  cursor: not-allowed;
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

:deep(.cm-editor) {
  height: 100%;
}

:deep(.cm-editor.cm-focused) {
  outline: 2px solid var(--el-color-primary-light-8);
}

:deep(.cm-scroller) {
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style> 