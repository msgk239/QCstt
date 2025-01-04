<template>
  <el-config-provider namespace="ep">
    <div class="app">
      <el-container>
        <el-header>
          <h1>SenseVoice ASR</h1>
        </el-header>
        <el-main>
          <audio-recognizer />
        </el-main>
        <el-footer>
          <p>© 2024 SenseVoice. All rights reserved.</p>
        </el-footer>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ElConfigProvider } from 'element-plus'
import AudioRecognizer from '@/components/AudioRecognizer.vue'
</script>

<style>
.app {
  min-height: 100vh;
}

.el-header {
  text-align: center;
  line-height: 60px;
  background-color: #409EFF;
  color: white;
}

.el-main {
  background-color: #f5f7fa;
}

.el-footer {
  text-align: center;
  color: #909399;
  padding: 20px;
}
</style> 