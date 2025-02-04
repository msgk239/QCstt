import mitt from 'mitt'

export const EVENT_TYPES = {
  CONTENT_CHANGE: 'content_change',
  SPEAKER_CHANGE: 'speaker_change',
  TIME_UPDATE: 'time_update',
  SEGMENT_SELECT: 'segment_select'
}

export const editorBus = mitt() 