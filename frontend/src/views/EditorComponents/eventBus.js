import mitt from 'mitt'

export const editorBus = mitt()

// 事件类型常量
export const EVENT_TYPES = {
  SAVE: 'save',
  SAVE_VERSION: 'save:version',      // 手动保存版本
  LOAD_VERSION: 'load:version',      // 加载指定版本
  VERSION_SAVED: 'version:saved',    // 版本保存完成
  VERSION_LOADED: 'version:loaded',  // 版本加载完成
  AUDIO_PLAY: 'audio:play',
  AUDIO_PAUSE: 'audio:pause',
  AUDIO_SEEK: 'audio:seek',
  SEGMENT_UPDATE: 'segment:update',
  SPEAKER_UPDATE: 'speaker:update',
  FORMAT_APPLY: 'format:apply'
} 