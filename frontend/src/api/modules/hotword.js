import request from '../request'

/**
 * 获取热词库列表
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: Array<{
 *     id: string,
 *     name: string,
 *     description: string,
 *     word_count: number,
 *     created_at: string,
 *     updated_at: string
 *   }>
 * }>}
 */
export function getHotwordLibraries() {
  return request({
    url: '/api/v1/asr/hotword-libraries',
    method: 'get'
  })
}

/**
 * 创建热词库
 * @param {Object} data - 热词库数据
 * @param {string} data.name - 热词库名称
 * @param {string} data.description - 热词库描述
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     name: string,
 *     description: string
 *   }
 * }>}
 */
export function createHotwordLibrary(data) {
  return request({
    url: '/api/v1/asr/hotword-libraries',
    method: 'post',
    data
  })
}

/**
 * 导入热词库
 * @param {File} file - 热词库文件
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     name: string,
 *     word_count: number
 *   }
 * }>}
 */
export function importHotwordLibrary(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/api/v1/asr/hotword-libraries/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出热词库
 * @param {string} libraryId - 热词库ID
 * @returns {Promise<Blob>}
 */
export function exportHotwordLibrary(libraryId) {
  return request({
    url: `/api/v1/asr/hotword-libraries/${libraryId}/export`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除热词库
 * @param {string} libraryId - 热词库ID
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function deleteHotwordLibrary(libraryId) {
  return request({
    url: `/api/v1/asr/hotword-libraries/${libraryId}`,
    method: 'delete'
  })
}

/**
 * 更新热词库
 * @param {string} libraryId - 热词库ID
 * @param {Object} data - 更新数据
 * @param {string} data.name - 热词库名称
 * @param {string} data.description - 热词库描述
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     name: string,
 *     description: string
 *   }
 * }>}
 */
export function updateHotwordLibrary(libraryId, data) {
  return request({
    url: `/api/v1/asr/hotword-libraries/${libraryId}`,
    method: 'put',
    data
  })
}

/**
 * 获取热词列表
 * @param {string} libraryId - 热词库ID
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: Array<{
 *     id: string,
 *     text: string,
 *     category: string,
 *     created_at: string
 *   }>
 * }>}
 */
export function getHotwords(libraryId) {
  return request({
    url: `/api/v1/asr/hotword-libraries/${libraryId}/words`,
    method: 'get'
  })
}

/**
 * 添加热词
 * @param {string} libraryId - 热词库ID
 * @param {Object} data - 热词数据
 * @param {string} data.text - 热词文本
 * @param {string} data.category - 分类
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     text: string,
 *     category: string
 *   }
 * }>}
 */
export function addHotword(libraryId, data) {
  return request({
    url: `/api/v1/asr/hotword-libraries/${libraryId}/words`,
    method: 'post',
    data
  })
}

/**
 * 删除热词
 * @param {string} libraryId - 热词库ID
 * @param {string} wordId - 热词ID
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function deleteHotword(libraryId, wordId) {
  return request({
    url: `/api/v1/asr/hotwords/${wordId}`,
    method: 'delete'
  })
}

/**
 * 批量添加热词
 * @param {string} libraryId - 热词库ID
 * @param {Array<{text: string, category: string}>} words - 热词列表
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     success_count: number,
 *     fail_count: number
 *   }
 * }>}
 */
export function batchAddHotwords(libraryId, words) {
  return request({
    url: `/api/v1/asr/hotwords/batch-import`,
    method: 'post',
    data: words
  })
}

/**
 * 更新热词
 * @param {string} libraryId - 热词库ID
 * @param {string} wordId - 热词ID
 * @param {Object} data - 更新数据
 * @param {string} data.text - 热词文本
 * @param {string} data.category - 分类
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     text: string,
 *     category: string
 *   }
 * }>}
 */
export function updateHotword(libraryId, wordId, data) {
  return request({
    url: `/api/v1/asr/hotwords/${wordId}`,
    method: 'put',
    data
  })
} 