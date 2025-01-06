<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <el-header height="60px">
          <app-header v-model:collapse="isCollapse" />
        </el-header>
        <el-container>
          <el-aside :width="isCollapse ? '64px' : '200px'">
            <app-sidebar :collapse="isCollapse" />
          </el-aside>
          <el-main>
            <router-view></router-view>
          </el-main>
        </el-container>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'

const isCollapse = ref(false)
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  height: 100%;
}

.el-container {
  height: 100%;
}

.el-header {
  border-bottom: 1px solid var(--el-border-color-light);
  background-color: #fff;
  padding: 0;
}

.el-aside {
  background-color: var(--el-bg-color-page);
  border-right: 1px solid var(--el-border-color-light);
  transition: width 0.3s;
}

.el-main {
  background-color: var(--el-bg-color);
  padding: 20px;
}
</style>
