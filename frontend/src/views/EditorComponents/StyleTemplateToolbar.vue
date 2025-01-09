<template>
  <div class="style-template-toolbar">
    <el-dropdown trigger="click">
      <el-button>
        样式模板<el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item v-for="template in templates" 
                          :key="template.name"
                          @click="applyTemplate(template)">
            {{ template.name }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const templates = ref([
  {
    name: '重点标记',
    style: {
      backgroundColor: '#FFE599',
      fontWeight: 'bold'
    }
  },
  {
    name: '注释文本',
    style: {
      color: '#666666',
      fontSize: '0.9em',
      fontStyle: 'italic'
    }
  }
])

const emit = defineEmits(['apply-template'])

const applyTemplate = (template) => {
  emit('apply-template', template)
}
</script>

<style scoped>
.style-template-toolbar {
  display: flex;
  align-items: center;
}
</style> 