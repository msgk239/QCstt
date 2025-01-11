<template>
  <el-menu
    class="sidebar-menu"
    :default-active="activeMenu"
    :collapse="isCollapse"
    router
  >
    <el-menu-item index="/">
      <el-icon><Document /></el-icon>
      <template #title>
        文件列表
        <el-badge 
          v-if="fileCount > 0" 
          :value="fileCount" 
          :max="99"
          class="file-count"
        />
      </template>
    </el-menu-item>
    <el-menu-item index="/trash">
      <el-icon><Delete /></el-icon>
      <template #title>
        回收站
        <el-badge 
          v-if="trashCount > 0" 
          :value="trashCount" 
          type="warning"
          :max="99"
          class="trash-count"
        />
      </template>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Delete } from '@element-plus/icons-vue'
import { useFileStore } from '@/stores/fileStore'

const props = defineProps({
  collapse: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const fileStore = useFileStore()

// 根据当前路由设置激活菜单
const activeMenu = computed(() => route.path)
const isCollapse = computed(() => props.collapse)

// 文件数量统计
const fileCount = computed(() => fileStore.totalFiles)

// 回收站文件数量
const trashCount = computed(() => {
  return fileStore.fileList.filter(file => file.status === 'deleted').length
})
</script>

<style scoped>
.sidebar-menu {
  height: 100%;
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

/* 激活菜单项样式 */
:deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary-light-9);
}

/* 菜单项悬停样式 */
:deep(.el-menu-item:hover) {
  background-color: var(--el-color-primary-light-8);
}

/* 图标样式 */
:deep(.el-menu-item .el-icon) {
  font-size: 18px;
}

/* 添加新样式 */
.file-count {
  margin-left: 8px;
}

.trash-count {
  margin-left: 8px;
}

:deep(.el-badge__content) {
  font-size: 12px;
  height: 16px;
  line-height: 16px;
  padding: 0 4px;
}
</style> 