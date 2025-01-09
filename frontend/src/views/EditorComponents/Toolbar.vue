<template>
  <div class="toolbar">
    <!-- 第一行 -->
    <div class="toolbar-header">
      <div class="toolbar-left">
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <div class="file-info">
          <h2 class="file-name">{{ file?.name }}</h2>
          <span class="file-meta">{{ formatDuration(file?.duration) }} · {{ file?.date }} 转换</span>
        </div>
      </div>
    </div>
    <!-- 其他工具栏内容 -->
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// 路由
const router = useRouter()

// 状态
const file = ref(null)

// 方法
const formatDuration = (duration) => {
  // 格式化持续时间的函数
}
</script>

<style scoped>
.toolbar {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.file-info {
  display: flex;
  flex-direction: column;
}

.file-name {
  margin: 0;
  font-size: 18px;
}

.file-meta {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}
</style> 