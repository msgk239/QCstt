import request from '../request'
/**
 * 获取热词内容
 * @returns {Promise<{
 *   code: number,
 *   data: {
 *     content: string,
 *     lastModified: number
 *   }
 * }>}
 */
export function getKeywordsContent() {
  return request({
    url: '/api/v1/hotwords',
    method: 'get'
  })
}

/**
 * 更新热词内容
 * @param {Object} data
 * @param {string} data.content - 文件内容
 * @param {number} data.lastModified - 最后修改时间
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function updateKeywordsContent(data) {
  return request({
    url: '/api/v1/hotwords',
    method: 'post',
    data
  })
}

/**
 * 验证热词内容格式
 * @param {Object} data
 * @param {string} data.content - 要验证的内容
 * @returns {Promise<{
 *   code: number,
 *   data: {
 *     isValid: boolean,
 *     errors: Array<{
 *       line: number,
 *       message: string,
 *       content: string
 *     }>
 *   }
 * }>}
 */
export function validateKeywordsContent(data) {
  return request({
    url: '/api/v1/hotwords/validate',
    method: 'post',
    data
  })
} 