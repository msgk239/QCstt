<template>
  <el-menu
    class="sidebar-menu"
    :default-active="activeMenu"
    :collapse="isCollapse"
    router
  >
    <el-menu-item index="/">
      <el-icon><Document /></el-icon>
      <template #title>文件列表</template>
    </el-menu-item>
    <el-menu-item index="/trash">
      <el-icon><Delete /></el-icon>
      <template #title>回收站</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  collapse: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()

// 根据当前路由设置激活菜单
const activeMenu = computed(() => route.path)
const isCollapse = computed(() => props.collapse)
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
</style> 