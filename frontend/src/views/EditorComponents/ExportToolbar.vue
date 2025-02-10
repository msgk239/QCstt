<template>
  <div class="export-toolbar">
    <el-dropdown trigger="click">
      <el-button type="primary">
        导出<el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="handleExport('word')">
            Word文档
          </el-dropdown-item>
          <el-dropdown-item @click="handleExport('pdf')">
            PDF文件
          </el-dropdown-item>
          <el-dropdown-item @click="handleExport('txt')">
            纯文本
          </el-dropdown-item>
          <el-dropdown-item @click="handleExport('md')">
            Markdown
          </el-dropdown-item>
          <el-dropdown-item @click="handleExport('srt')">
            SRT字幕
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const formats = ref({
  word: true,
  pdf: false,
  txt: false,
  md: false,
  srt: false
})

// 定义事件
const emit = defineEmits(['export'])

const handleExport = (format) => {
  console.log('正在导出格式：', format)
  emit('export', [format])
}
</script>

<style scoped>
.export-toolbar {
  display: flex;
  align-items: center;
}
</style> 