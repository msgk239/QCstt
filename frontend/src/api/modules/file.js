import request from '../request'

/**
 * 获取文件列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.query - 搜索关键词
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     items: Array<{
 *       id: string,
 *       name: string,
 *       size: number,
 *       date: string,
 *       status: string,
 *       duration: string
 *     }>,
 *     total: number,
 *     page: number,
 *     page_size: number
 *   }
 * }>}
 */
export function getFileList(params) {
  return request({
    url: '/api/v1/files',
    method: 'get',
    params
  })
}

/**
 * 上传音频文件
 * @param {File} file - 文件对象
 * @param {Object} options - 上传选项
 * @param {string} options.action - 动作类型：'upload' | 'recognize'
 * @param {string} options.language - 识别语言：'auto' | 'zh' | 'en' | 'ja' | 'ko'
 * @param {Function} options.onProgress - 上传进度回调
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     original_name: string,
 *     display_name: string,
 *     display_full_name: string,
 *     storage_name: string,
 *     extension: string,
 *     size: number,
 *     date: string,
 *     status: string,
 *     path: string,
 *     duration: number,
 *     duration_str: string,
 *     options: Object
 *   }
 * }>}
 */
export function uploadFile(file, options = {}) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('options', JSON.stringify(options))

  return request({
    url: '/api/v1/files/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: options.onProgress
  })
}

/**
 * 获取文件详情
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     original_name: string,
 *     display_name: string,
 *     display_full_name: string,
 *     storage_name: string,
 *     extension: string,
 *     size: number,
 *     date: string,
 *     status: string,
 *     path: string,
 *     duration: number,
 *     duration_str: string,
 *     options: Object
 *   }
 * }>}
 */
export function getFileDetail(fileId) {
  return request({
    url: `/api/v1/files/${fileId}`,
    method: 'get'
  })
}

/**
 * 删除文件（移至回收站）
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function deleteFile(fileId) {
  return request({
    url: `/api/v1/files/${fileId}`,
    method: 'delete'
  })
}

/**
 * 重命名文件
 * @param {string} fileId - 文件ID
 * @param {string} newName - 新文件名（不含扩展名）
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     name: string
 *   }
 * }>}
 */
export function renameFile(fileId, newName) {
  return request({
    url: `/api/v1/files/${fileId}/rename`,
    method: 'put',
    data: {
      new_name: newName
    }
  })
}

/**
 * 获取文件进度
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
export function getFileProgress(fileId) {
  return request({
    url: `/api/v1/files/${fileId}/progress`,
    method: 'get'
  })
}

/**
 * 更新文件内容
 * @param {string} fileId - 文件ID
 * @param {Object} data - 更新数据
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: Object
 * }>}
 */
export function updateFile(fileId, data) {
  return request({
    url: `/api/v1/files/${fileId}/transcript`,
    method: 'put',
    data
  })
}

/**
 * 获取音频文件
 * @param {string} fileId - 文件ID
 * @returns {Promise<Blob>}
 */
export function getAudioFile(fileId) {
  return request({
    url: `/api/v1/files/${fileId}/audio`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 导出文件
 * @param {string} fileId - 文件ID
 * @param {string} format - 导出格式
 * @returns {Promise<Blob>}
 */
export function exportFile(fileId, format) {
  return request({
    url: `/api/v1/files/${fileId}/transcript`,
    method: 'get',
    params: { format },
    responseType: 'blob'
  })
}

/**
 * 格式化文件数据
 * @param {Object} response - API响应数据
 * @returns {{
 *   id: string,
 *   name: string,
 *   duration: number,
 *   date: string,
 *   status: string,
 *   segments: Array<Object>,
 *   speakers: Array<Object>,
 *   fullText: string
 * }}
 */
export function formatFileData(response) {
  const { data } = response
  
  if (data.transcripts) {
    const { original, metadata } = data.transcripts
    const recognitionData = original || {}
    
    return {
      id: data.id,
      name: data.name,
      duration: recognitionData.duration || 0,
      date: new Date(metadata?.created_at).toLocaleDateString(),
      status: metadata?.status || '未识别',
      segments: recognitionData.segments || [],
      speakers: recognitionData.speakers || [],
      fullText: recognitionData.full_text || ''
    }
  }
  
  return {
    id: data.id,
    name: data.name,
    duration: 0,
    date: new Date().toLocaleDateString(),
    status: '未识别',
    segments: [],
    speakers: [],
    fullText: ''
  }
}