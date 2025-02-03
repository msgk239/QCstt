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
export const getFileList = async (params) => {
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
export const uploadFile = async (file, options) => {
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
export const deleteFile = async (fileId) => {
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
export const renameFile = async (fileId, newName) => {
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
export async function updateFile(fileId, data) {
  console.log('发送更新请求:', {
    fileId,
    url: `/api/v1/files/${fileId}`,
    method: 'put',
    dataSize: JSON.stringify(data).length,
    data
  })
  
  try {
    const response = await request({
      url: `/api/v1/files/${fileId}`,
      method: 'put',
      data,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    console.log('更新响应:', {
      status: response?.status,
      code: response?.code,
      message: response?.message,
      data: response?.data,
      fullResponse: response
    })
    
    // 检查响应格式
    if (!response || typeof response !== 'object') {
      throw new Error('响应格式错误')
    }
    
    return response
  } catch (error) {
    console.error('更新请求失败:', {
      error,
      message: error.message,
      response: error.response,
      stack: error.stack
    })
    throw error
  }
}

/**
 * 获取音频文件
 * @param {string} fileId - 文件ID
 * @returns {Promise<Blob>}
 */
export async function getAudioFile(fileId) {
  try {
    const blob = await request({
      url: `/api/v1/files/${fileId}/audio`,
      method: 'get',
      responseType: 'blob'
    })

    // 如果响应不是 Blob，说明出错了
    if (!(blob instanceof Blob)) {
      throw new Error('响应格式错误')
    }

    // 如果是 JSON 响应，检查是否是错误信息
    if (blob.type.includes('application/json')) {
      const text = await blob.text()
      const jsonResponse = JSON.parse(text)
      
      if (jsonResponse.code !== 200) {
        throw new Error(jsonResponse.message || '获取音频文件失败')
      }
      throw new Error('服务器返回了 JSON 而不是音频文件')
    }

    // 如果不是音频文件，抛出错误
    if (!blob.type.includes('audio/')) {
      throw new Error('服务器返回的不是音频文件')
    }

    return blob
  } catch (error) {
    console.error('获取音频文件失败:', error)
    throw error
  }
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
  
  if (!data) {
    return {
      id: '',
      name: '',
      duration: 0,
      duration_str: '0:00',
      date: new Date().toLocaleDateString(),
      status: '未识别',
      segments: [],
      speakers: [],
      fullText: '',
      metadata: {
        has_timestamp: false,
        has_speaker: false,
        has_emotion: false
      },
      extension: '',
      size: 0,
      options: {
        language: 'auto',
        action: 'upload'
      },
      version_count: 0
    }
  }

  return {
    id: data.file_id || data.id,
    name: data.display_name || data.original_name,
    duration: data.duration || 0,
    duration_str: data.duration_str || '0:00',
    date: new Date(data.created_at || data.date).toLocaleDateString(),
    status: data.status || '未识别',
    segments: data.segments || [],
    speakers: data.speakers || [],
    fullText: data.full_text || '',
    metadata: {
      has_timestamp: data.metadata?.has_timestamp || false,
      has_speaker: data.metadata?.has_speaker || false,
      has_emotion: data.metadata?.has_emotion || false
    },
    extension: data.extension || '',
    size: data.size || 0,
    options: data.options || {
      language: 'auto',
      action: 'upload'
    },
    version_count: data.version_count || 0
  }
}

/**
 * 批量删除文件
 * @param {Array<string>} fileIds - 文件ID数组
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function batchDeleteFiles(fileIds) {
  return request({
    url: '/api/v1/files/batch-delete',
    method: 'post',
    data: { file_ids: fileIds }
  })
}

/**
 * 获取转写结果
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     transcripts: {
 *       original: Object,
 *       metadata: Object
 *     }
 *   }
 * }>}
 */
export function getTranscript(fileId) {
  return request({
    url: `/api/v1/files/${fileId}/transcript`,
    method: 'get'
  })
}

/**
 * 更新转写结果
 * @param {string} fileId - 文件ID
 * @param {Object} data - 转写数据
 * @returns {Promise<{
 *   code: number,
 *   message: string
 * }>}
 */
export function updateTranscript(fileId, data) {
  return request({
    url: `/api/v1/files/${fileId}/transcript`,
    method: 'put',
    data
  })
}

/**
 * 保存文件版本
 * @param {string} fileId - 文件ID
 * @param {Object} data - 版本数据，包含content、type和note
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     timestamp: string,
 *     content: Object,
 *     type: string,
 *     note: string
 *   }
 * }>}
 */
export function saveVersion(fileId, data) {
  console.log('发送版本保存请求:', {
    fileId,
    url: `/api/v1/files/${fileId}/versions`,
    method: 'post',
    dataSize: JSON.stringify(data).length,
    data
  })
  
  return request({
    url: `/api/v1/files/${fileId}/versions`,
    method: 'post',
    data,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

/**
 * 获取文件版本列表
 * @param {string} fileId - 文件ID
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: Array<{
 *     id: string,
 *     timestamp: string,
 *     content: Object
 *   }>
 * }>}
 */
export function getVersions(fileId) {
  return request({
    url: `/api/v1/files/${fileId}/versions`,
    method: 'get'
  })
}

/**
 * 获取指定版本的内容
 * @param {string} fileId - 文件ID
 * @param {string} versionId - 版本ID
 * @returns {Promise<{
 *   code: number,
 *   message: string,
 *   data: {
 *     id: string,
 *     timestamp: string,
 *     content: Object
 *   }
 * }>}
 */
export function getVersion(fileId, versionId) {
  return request({
    url: `/api/v1/files/${fileId}/versions/${versionId}`,
    method: 'get'
  })
}

export const fileApi = {
  upload: uploadFile,
  getList: getFileList,
  delete: deleteFile,
  rename: renameFile,
  getDetail: getFileDetail,
  getProgress: getFileProgress,
  update: updateFile,
  getAudio: getAudioFile,
  export: exportFile,
  batchDelete: batchDeleteFiles,
  getTranscript,
  updateTranscript,
  formatData: formatFileData,
  saveVersion,
  getVersions,
  getVersion
}