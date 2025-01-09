<template>
  <div class="share-toolbar">
    <el-dropdown trigger="click">
      <el-button type="primary">
        分享<el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item>分享到微信</el-dropdown-item>
          <el-dropdown-item divided>
            <el-checkbox v-model="formats.word">Word文档</el-checkbox>
          </el-dropdown-item>
          <el-dropdown-item>
            <el-checkbox v-model="formats.pdf">PDF文件</el-checkbox>
          </el-dropdown-item>
          <el-dropdown-item divided>
            <el-button type="primary" @click="handleShare">生成分享文件</el-button>
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
  pdf: true
})

// 定义事件
const emit = defineEmits(['share'])

const handleShare = () => {
  const selectedFormats = Object.entries(formats.value)
    .filter(([_, selected]) => selected)
    .map(([format]) => format)
  
  if (selectedFormats.length > 0) {
    emit('share', selectedFormats)
  }
}
</script>

<style scoped>
.share-toolbar {
  display: flex;
  align-items: center;
}
</style> 