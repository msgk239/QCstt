<template>
  <el-dialog
    v-model="visible"
    title="播放速度"
    width="300px"
  >
    <div class="speed-list">
      <el-radio-group v-model="playbackRate" @change="handleSpeedChange">
        <el-radio-button v-for="speed in speeds" :key="speed" :value="speed">
          {{ speed }}x
        </el-radio-button>
      </el-radio-group>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const playbackRate = ref(1)
const speeds = [0.5, 0.75, 1, 1.25, 1.5, 2]

const handleSpeedChange = (speed) => {
  playbackRate.value = speed
  visible.value = false
  // 触发事件通知父组件
  emit('update:speed', speed)
}

// 定义事件
const emit = defineEmits(['update:speed'])
</script>

<style scoped>
.speed-list {
  display: flex;
  justify-content: center;
}
</style> 