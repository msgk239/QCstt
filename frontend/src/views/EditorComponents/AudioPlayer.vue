<template>
  <div class="audio-player">
    <!-- 左侧控制区 -->
    <div class="controls">
      <!-- 播放按钮增大点击区域 -->
      <div class="play-button-wrapper">
        <el-button 
          class="play-button"
          :icon="playing ? 'Pause' : 'VideoPlay'"
          circle
          type="primary"
          @click="$emit('play')"
        />
      </div>
      
      <!-- 播放速度 -->
      <el-dropdown @command="handleSpeedChange" trigger="click">
        <el-button class="speed-button">
          {{ playbackRate }}x
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item 
              v-for="speed in [0.5, 0.8, 1, 1.2, 1.5, 2]" 
              :key="speed"
              :command="speed"
            >
              {{ speed }}x
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 进度条 - 增加可点击区域 -->
    <div class="progress">
      <div class="slider-wrapper" 
        @mousemove="handleMouseMove" 
        @mouseleave="handleMouseLeave"
      >
        <el-slider
          v-model="sliderValue"
          :max="duration"
          :step="0.1"
          :format-tooltip="formatTooltipTime"
          :tooltip-class="'custom-tooltip'"
          show-tooltip="always"
          @change="handleSeek"
          @input="handleSliderInput"
        />
        <!-- 自定义时间提示 -->
        <div class="time-tooltip" 
          v-show="showTooltip"
          :style="{ left: tooltipLeft + 'px' }"
        >
          {{ formatTime(hoverTime) }}
        </div>
      </div>
      <div class="time">
        <span>{{ formatTime(currentTime) }}</span>
        <span>/</span>
        <span>{{ formatTime(duration) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audio-player {
  display: flex;
  align-items: center;
  gap: 20px;
  height: 56px;
  padding: 0 16px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 播放按钮包装器 - 增加点击区域 */
.play-button-wrapper {
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 美化播放按钮 */
.play-button {
  width: 44px !important;
  height: 44px !important;
  font-size: 20px !important;
}

/* 简化速度按钮 */
.speed-button {
  height: 32px;
  padding: 0 12px;
  font-size: 14px;
}

.progress {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 8px;
}

/* 进度条包装器 - 增加点击区域 */
.slider-wrapper {
  padding: 12px 0;
  margin: -12px 0;
  cursor: pointer;
  position: relative;  /* 为自定义提示定位 */
}

/* 美化进度条 */
:deep(.el-slider) {
  margin: 0;
  --el-slider-button-size: 14px;  /* 增大滑块尺寸 */
  --el-slider-height: 6px;      /* 增大进度条高度 */
}

:deep(.el-slider__runway) {
  margin: 8px 0;
}

:deep(.el-slider__button) {
  border: 2px solid var(--el-color-primary);
  width: 16px;  /* 增大滑块 */
  height: 16px;
  cursor: pointer;
}

:deep(.el-slider__button-wrapper) {
  width: 32px;  /* 增大滑块热区 */
  height: 32px;
  top: -14px;
}

:deep(.el-slider__bar) {
  background-color: var(--el-color-primary);
  height: 6px;  /* 增大进度条 */
}

.time {
  display: flex;
  gap: 4px;
  color: #666;
  font-size: 12px;
  justify-content: flex-end;
}

/* 让时间提示始终显示 */
:deep(.always-visible-tooltip) {
  display: block !important;
  opacity: 0;
  transition: opacity 0.2s;
}

:deep(.el-slider:hover .always-visible-tooltip) {
  opacity: 1;
}

/* 美化时间提示 */
:deep(.el-slider__tooltip) {
  padding: 4px 8px;
  min-width: 35px;
  height: 24px;
  line-height: 16px;
  font-size: 12px;
  font-family: monospace;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  color: #fff;
  pointer-events: none;  /* 防止提示框影响鼠标事件 */
}

:deep(.el-slider__tooltip.is-dark) {
  padding: 4px 8px;
}

:deep(.el-slider__tooltip__pointer) {
  display: none;
}

/* 自定义时间提示 */
.time-tooltip {
  position: absolute;
  top: -30px;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
  pointer-events: none;
  z-index: 100;
}

/* 隐藏原始提示 */
:deep(.el-slider__tooltip) {
  display: none;
}
</style>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  currentTime: Number,
  duration: Number,
  playing: Boolean,
  playbackRate: Number
})

const emit = defineEmits(['play', 'seek', 'speed-change'])

// 进度条值
const sliderValue = computed({
  get: () => props.currentTime,
  set: (value) => emit('seek', value)
})

// 处理进度条拖动
const handleSliderInput = (value) => {
  emit('seek', value)
}

const handleSeek = (value) => {
  emit('seek', value)
}

const handleSpeedChange = (speed) => {
  emit('speed-change', speed)
}

const formatTime = (seconds) => {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 格式化悬浮提示的时间
const formatTooltipTime = (val) => {
  return formatTime(val)
}

// 添加提示相关的状态
const showTooltip = ref(false)
const tooltipLeft = ref(0)
const hoverTime = ref(0)

// 处理鼠标移动
const handleMouseMove = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const offsetX = e.clientX - rect.left
  const percent = offsetX / rect.width
  
  tooltipLeft.value = offsetX
  hoverTime.value = props.duration * percent
  showTooltip.value = true
}

const handleMouseLeave = () => {
  showTooltip.value = false
}
</script> 