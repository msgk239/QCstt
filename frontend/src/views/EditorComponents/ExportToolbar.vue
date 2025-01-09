<template>
  <div class="export-toolbar">
    <el-dropdown trigger="click">
      <el-button type="primary">
        导出<el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item>
            <el-checkbox v-model="formats.word">Word文档</el-checkbox>
          </el-dropdown-item>
          <el-dropdown-item>
            <el-checkbox v-model="formats.pdf">PDF文件</el-checkbox>
          </el-dropdown-item>
          <el-dropdown-item>
            <el-checkbox v-model="formats.txt">纯文本</el-checkbox>
          </el-dropdown-item>
          <el-dropdown-item>
            <el-checkbox v-model="formats.md">Markdown</el-checkbox>
          </el-dropdown-item>
          <el-dropdown-item>
            <el-checkbox v-model="formats.srt">SRT字幕</el-checkbox>
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

const handleExport = () => {
  const selectedFormats = Object.entries(formats.value)
    .filter(([_, selected]) => selected)
    .map(([format]) => format)
  
  if (selectedFormats.length > 0) {
    emit('export', selectedFormats)
  }
}
</script>

<style scoped>
.export-toolbar {
  display: flex;
  align-items: center;
}
</style> 