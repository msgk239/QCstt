<template>
  <div class="app-header">
    <div class="header-left">
      <el-button
        :icon="isCollapse ? Expand : Fold"
        @click="toggleCollapse"
      />
      <el-icon v-if="isLoading" class="loading-icon is-loading">
        <Loading />
      </el-icon>
    </div>
    <div class="header-center">
      <div class="title-container">
        <el-image
          class="app-logo"
          :src="logoUrl"
          fit="contain"
        >
          <template #error>
            <div class="image-slot">
              <el-icon><Document /></el-icon>
            </div>
          </template>
        </el-image>
        <h1 class="app-title">潜催语音转文字系统</h1>
      </div>
      <div v-if="fileStats.total > 0" class="file-stats">
        <el-tag size="small">总文件: {{ fileStats.total }}</el-tag>
        <el-tag 
          v-if="fileStats.processing > 0" 
          type="warning" 
          size="small"
        >
          处理中: {{ fileStats.processing }}
        </el-tag>
      </div>
    </div>
    <div class="header-right">
      <el-button-group>
        <el-button :icon="QuestionFilled" circle />
        <el-button :icon="Setting" circle />
      </el-button-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Expand, Fold, QuestionFilled, Setting, Loading } from '@element-plus/icons-vue'
import { useFileStore } from '@/stores/fileStore'
import logoUrl from '@/assets/logo.svg'

const fileStore = useFileStore()

const isCollapse = ref(false)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
  // 触发自定义事件，通知父组件折叠状态变化
  emit('update:collapse', isCollapse.value)
}

const emit = defineEmits(['update:collapse'])

const isLoading = computed(() => fileStore.loading)

const fileStats = computed(() => {
  return {
    total: fileStore.totalFiles,
    processing: fileStore.fileList.filter(f => f.status === 'processing').length
  }
})
</script>

<style scoped>
.app-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.header-left,
.header-right {
  flex: 1;
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
  align-items: center;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-logo {
  height: 32px;
  width: 32px;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.header-right {
  display: flex;
  justify-content: flex-end;
}

.loading-icon {
  margin-left: 8px;
  color: var(--el-color-primary);
}

.file-stats {
  display: flex;
  gap: 8px;
  margin-left: 16px;
}
</style> 