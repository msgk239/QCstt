<template>
  <div id="app">
    <!-- 只在非编辑器页面显示侧边栏 -->
    <AppSidebar v-if="!isEditorPage" />
    
    <!-- 路由视图 -->
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/layout/AppSidebar.vue'

const route = useRoute()
const isEditorPage = computed(() => route.name === 'editor')
</script>

<style>
#app {
  display: flex;
  height: 100vh;
}
</style>
