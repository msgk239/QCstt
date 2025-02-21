<template>
  <div id="app">
    <!-- 头部导航 -->
    <AppHeader v-if="!isEditorPage" />
    <!-- 主要内容区域 -->
    <div class="content">
      <!-- 只在非编辑器页面显示侧边栏 -->
      <AppSidebar v-if="!isEditorPage" />
      <!-- 路由视图 -->
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const route = useRoute()
const isEditorPage = computed(() => route.name === 'editor')
</script>

<style>
#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
  display: flex;
}
</style>
