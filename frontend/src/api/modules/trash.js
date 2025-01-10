import request from '../request'

/**
 * 获取回收站文件列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     items: Array<{
 *       id: string,
 *       name: string,
 *       size: number,
 *       date: string,
 *       status: string
 *     }>,
 *     total: number,
 *     page: number,
 *     page_size: number
 *   }
 * }>}
 */
export function getTrashList(params) {
  return request({
    url: '/api/v1/trash',
    method: 'get',
    params
  })
}

/**
 * 从回收站恢复文件
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function restoreFile(fileId) {
  return request({
    url: `/api/v1/trash/${fileId}/restore`,
    method: 'post'
  })
}

/**
 * 永久删除文件
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function permanentlyDeleteFile(fileId) {
  return request({
    url: `/api/v1/trash/${fileId}`,
    method: 'delete'
  })
}

/**
 * 清空回收站
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function clearTrash() {
  return request({
    url: '/api/v1/trash',
    method: 'delete'
  })
} 