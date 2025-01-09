<template>
  <div class="version-history-toolbar">
    <el-dropdown trigger="click">
      <el-button>
        历史版本<el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item>
            <div class="version-item">
              <span>当前版本</span>
              <div class="version-actions">
                <el-button size="small">预览</el-button>
              </div>
            </div>
          </el-dropdown-item>
          <el-dropdown-item v-for="version in versions" :key="version.id">
            <div class="version-item">
              <span>{{ version.time }}</span>
              <div class="version-actions">
                <el-button size="small">预览</el-button>
                <el-button size="small" type="primary">还原</el-button>
              </div>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const versions = ref([
  { id: 1, time: '10分钟前的版本', content: null },
  { id: 2, time: '1小时前的版本', content: null },
  { id: 3, time: '转换完成时的版本', content: null }
])

// 定义事件
const emit = defineEmits(['preview', 'restore'])

const handlePreview = (version) => {
  emit('preview', version)
}

const handleRestore = (version) => {
  emit('restore', version)
}
</script>

<style scoped>
.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 4px 0;
}

.version-actions {
  display: flex;
  gap: 8px;
}
</style> 