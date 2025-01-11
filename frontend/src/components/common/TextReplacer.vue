<template>
  <el-dialog
    v-model="dialogVisible"
    title="文本替换"
    width="400px"
  >
    <div class="text-replacer">
      <el-form>
        <el-form-item label="查找内容">
          <el-input
            v-model="searchText"
            placeholder="请输入要查找的文本"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="替换为">
          <el-input
            v-model="replaceText"
            placeholder="请输入要替换的文本"
            clearable
          />
        </el-form-item>
      </el-form>

      <div class="match-info" v-if="matchCount > 0">
        匹配到 {{ matchCount }} 处
      </div>

      <div class="button-group">
        <el-button @click="handleReplace" :disabled="!searchText">
          替换
        </el-button>
        <el-button type="primary" @click="handleReplaceAll" :disabled="!searchText">
          全部替换
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useFileStore } from '@/stores/fileStore'

// 获取 store
const fileStore = useFileStore()

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  content: {
    type: String,
    required: true
  }
})

// 移除不需要的 emit
const emit = defineEmits(['update:visible'])

// 状态
const dialogVisible = ref(false)
const searchText = ref('')
const replaceText = ref('')
const matchCount = ref(0)

// 监听对话框可见性
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    searchText.value = ''
    replaceText.value = ''
    matchCount.value = 0
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 计算匹配数量
watch(searchText, (val) => {
  if (!val) {
    matchCount.value = 0
    return
  }
  const regex = new RegExp(escapeRegExp(val), 'g')
  const matches = props.content.match(regex)
  matchCount.value = matches ? matches.length : 0
})

// 工具函数
const escapeRegExp = (string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// 方法
const handleSearch = () => {
  if (!searchText.value) {
    ElMessage.warning('请输入要查找的文本')
    return
  }
}

const handleReplace = async () => {
  if (!searchText.value || !fileStore.currentFile) return
  
  const newContent = props.content.replace(
    new RegExp(escapeRegExp(searchText.value)), 
    replaceText.value
  )
  
  try {
    await fileStore.saveFile(fileStore.currentFile.id, {
      content: newContent
    })
    ElMessage.success('替换成功')
  } catch (error) {
    ElMessage.error('替换失败')
  }
}

const handleReplaceAll = async () => {
  if (!searchText.value || !fileStore.currentFile) return

  const newContent = props.content.replaceAll(
    new RegExp(escapeRegExp(searchText.value), 'g'),
    replaceText.value
  )
  
  try {
    await fileStore.saveFile(fileStore.currentFile.id, {
      content: newContent
    })
    ElMessage.success(`成功替换 ${matchCount.value} 处`)
  } catch (error) {
    ElMessage.error('替换失败')
  }
}
</script>

<style scoped>
.text-replacer {
  padding: 0 20px;
}

.match-info {
  margin: 16px 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style> 