<template>
  <el-dialog
    v-model="visible"
    title="文本替换"
    width="400px"
  >
    <div class="replace-panel">
      <el-form>
        <el-form-item label="查找内容：">
          <el-input v-model="searchText" />
        </el-form-item>
        <el-form-item label="替换为：">
          <el-input v-model="replaceText" />
        </el-form-item>
      </el-form>
      <div class="match-count" v-if="matchCount > 0">
        匹配到 {{ matchCount }} 处
      </div>
      <div class="replace-actions">
        <el-button @click="handleReplace">替换</el-button>
        <el-button type="primary" @click="handleReplaceAll">全部替换</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const visible = ref(false)
const searchText = ref('')
const replaceText = ref('')
const matchCount = ref(0)
const currentMatchIndex = ref(0)
const matches = ref([])

const findMatches = () => {
  // 查找匹配逻辑
}

const handleReplace = () => {
  // 替换逻辑
}

const handleReplaceAll = () => {
  // 全部替换逻辑
}

watch(searchText, () => {
  if (searchText.value) {
    findMatches()
  } else {
    matchCount.value = 0
    matches.value = []
  }
})
</script>

<style scoped>
.replace-panel {
  padding: 16px;
}

.match-count {
  margin: 8px 0;
  color: var(--el-text-color-secondary);
}

.replace-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}
</style> 