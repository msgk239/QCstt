import mitt from 'mitt'

export const editorBus = mitt()

// 事件类型常量
export const EVENT_TYPES = {
  SAVE: 'save',
  AUDIO_PLAY: 'audio:play',
  AUDIO_PAUSE: 'audio:pause',
  AUDIO_SEEK: 'audio:seek',
  SEGMENT_UPDATE: 'segment:update',
  SPEAKER_UPDATE: 'speaker:update',
  FORMAT_APPLY: 'format:apply'
} 