<template>
  <div class="edit-toolbar">
    <el-button-group>
      <el-dropdown trigger="click">
        <el-button>字体<el-icon><ArrowDown /></el-icon></el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-for="font in fonts" :key="font">{{ font }}</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      
      <el-dropdown trigger="click">
        <el-button>大小<el-icon><ArrowDown /></el-icon></el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-for="size in fontSizes" :key="size">{{ size }}px</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      
      <el-color-picker v-model="textColor" size="small" />
      <el-color-picker v-model="backgroundColor" size="small" />
    </el-button-group>

    <el-button-group>
      <el-button @click="applyFormat('bold')">
        <el-icon><BoldIcon /></el-icon>
      </el-button>
      <el-button @click="applyFormat('italic')">
        <el-icon><ItalicIcon /></el-icon>
      </el-button>
      <el-button @click="applyFormat('underline')">
        <el-icon><UnderlineIcon /></el-icon>
      </el-button>
      <el-button @click="applyFormat('strikethrough')">删除线</el-button>
      <el-button @click="applyFormat('highlight')">高亮</el-button>
    </el-button-group>

    <el-button-group>
      <el-button @click="addNote"><el-icon><ChatDotRound /></el-icon>添加注释</el-button>
      <el-button @click="insertTimestamp"><el-icon><Timer /></el-icon>插入时间戳</el-button>
    </el-button-group>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 状态
const textColor = ref('#000000')
const backgroundColor = ref('')
const fonts = ['微软雅黑', '宋体', '黑体']
const fontSizes = [12, 14, 16, 18, 20, 24]

// 方法
const applyFormat = (type) => {
  const selection = window.getSelection()
  if (!selection.rangeCount) return

  const range = selection.getRangeAt(0)
  const span = document.createElement('span')
  
  switch(type) {
    case 'bold':
      span.style.fontWeight = 'bold'
      break
    case 'italic':
      span.style.fontStyle = 'italic'
      break
    case 'underline':
      span.style.textDecoration = 'underline'
      break
    case 'strikethrough':
      span.style.textDecoration = 'line-through'
      break
    case 'highlight':
      span.style.backgroundColor = 'yellow'
      break
  }

  range.surroundContents(span)
}

const addNote = () => {
  // 添加注释逻辑
}

const insertTimestamp = () => {
  // 插入时间戳逻辑
}
</script>

<style scoped>
.edit-toolbar {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-toolbar .el-button-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style> 