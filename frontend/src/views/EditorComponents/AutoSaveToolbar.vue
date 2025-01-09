<template>
  <div class="auto-save-toolbar">
    <el-dropdown trigger="click">
      <el-button>
        <el-icon><Setting /></el-icon>自动保存
        <el-icon><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item>
            <el-switch v-model="autoSave" active-text="启用自动保存" />
          </el-dropdown-item>
          <el-dropdown-item>
            <span>保存间隔：</span>
            <el-select v-model="saveInterval" size="small">
              <el-option v-for="t in [1,5,10,15,30]" :key="t" :label="`${t}分钟`" :value="t" />
            </el-select>
          </el-dropdown-item>
          <el-dropdown-item>
            <span>最大保存版本：</span>
            <el-select v-model="maxVersions" size="small">
              <el-option v-for="n in [5,10,20,50]" :key="n" :label="n" :value="n" />
            </el-select>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <div class="auto-save-status" v-if="lastSaveTime">
      • {{ lastSaveTime }}前已自动保存
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const autoSave = ref(true)
const saveInterval = ref(5)
const maxVersions = ref(10)
const lastSaveTime = ref(null)

// 定义事件
const emit = defineEmits(['update:autoSave', 'update:saveInterval', 'update:maxVersions'])

watch([autoSave, saveInterval, maxVersions], ([newAutoSave, newInterval, newMaxVersions]) => {
  emit('update:autoSave', newAutoSave)
  emit('update:saveInterval', newInterval)
  emit('update:maxVersions', newMaxVersions)
})

// 更新最后保存时间的显示
const updateLastSaveTime = () => {
  // 实现时间更新逻辑
}
</script>

<style scoped>
.auto-save-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.auto-save-status {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}
</style> 