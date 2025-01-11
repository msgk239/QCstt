import request from '../request'

/**
 * 开始识别
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     taskId: string
 *   }
 * }>}
 */
export function startRecognition(fileId) {
  return request({
    url: `/api/v1/asr/recognize/${fileId}`,
    method: 'post'
  })
}

/**
 * 获取识别进度
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     progress: number,
 *     status: string
 *   }
 * }>}
 */
export function getRecognizeProgress(fileId) {
  return request({
    url: `/api/v1/asr/progress/${fileId}`,
    method: 'get'
  })
}

export function createProgressWebSocket(fileId) {
  const wsUrl = `${import.meta.env.VITE_WS_URL}/api/v1/ws/asr/progress/${fileId}`
  return new WebSocket(wsUrl)
} 