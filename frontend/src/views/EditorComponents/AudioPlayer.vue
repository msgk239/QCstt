<template>
  <div class="audio-player">
    <div class="waveform" ref="waveformRef"></div>
    <div class="player-controls">
      <el-button-group>
        <el-button :icon="PlaybackSpeed" @click="toggleSpeedMenu">
          {{ playbackRate }}x
        </el-button>
        <el-button :icon="Previous" @click="skipBackward" />
        <el-button :icon="playing ? Pause : Play" @click="togglePlay" />
        <el-button :icon="Next" @click="skipForward" />
      </el-button-group>
      <span class="time-display">
        {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 音频播放器
const waveformRef = ref(null)
const playing = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1)

// 方法
const togglePlay = () => {
  // 播放/暂停逻辑
}

const skipBackward = () => {
  // 后退逻辑
}

const skipForward = () => {
  // 前进逻辑
}

const toggleSpeedMenu = () => {
  // 切换速度菜单逻辑
}

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  return `${h > 0 ? h + ':' : ''}${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.audio-player {
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.player-controls {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.time-display {
  font-family: monospace;
  color: var(--el-text-color-regular);
}
</style> 