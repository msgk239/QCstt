import request from '../request'

/**
 * 获取支持的语言列表
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: Array<{
 *     code: string,
 *     name: string
 *   }>
 * }>}
 */
export function getSupportedLanguages() {
  return request({
    url: '/api/v1/system/languages',
    method: 'get'
  })
}

/**
 * 获取系统状态
 */
export function getSystemStatus() {
  return request({
    url: '/api/v1/system/status',
    method: 'get'
  })
} 