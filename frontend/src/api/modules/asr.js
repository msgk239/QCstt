import request from '../request'

// 上传音频文件
export function uploadAudio(file, options = {}) {
  const formData = new FormData()
  formData.append('file', file.raw)
  
  // 添加选项
  const uploadOptions = {
    action: options.action || 'upload',
    language: options.language || 'auto'
  }
  formData.append('options', JSON.stringify(uploadOptions))

  return request({
    url: '/api/files/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: options.onProgress,
    timeout: 600000
  })
}

// 获取文件列表
export function getFileList(params) {
  return request({
    url: '/api/files',
    method: 'get',
    params
  })
}

// 获取支持的语言列表
export function getSupportedLanguages() {
  return request({
    url: '/api/languages',
    method: 'get'
  })
}

// 获取文件进度
export function getFileProgress(fileId) {
  return request({
    url: `/api/files/${fileId}/progress`,
    method: 'get'
  })
}

// 获取识别进度
export function getRecognizeProgress(taskId) {
  return request({
    url: `/api/files/${taskId}/progress`,
    method: 'get'
  })
}

// 获取热词库列表
export function getHotwordLibraries() {
  return request({
    url: '/api/v1/asr/hotwords/libraries',
    method: 'get'
  })
}

// 创建热词库
export function createHotwordLibrary(data) {
  return request({
    url: '/api/v1/asr/hotwords/libraries',
    method: 'post',
    data
  })
}

// 更新热词库
export function updateHotwordLibrary(id, data) {
  return request({
    url: '/api/v1/asr/hotwords/libraries/' + id,
    method: 'put',
    data
  })
}

// 删除热词库
export function deleteHotwordLibrary(id) {
  return request({
    url: '/api/v1/asr/hotwords/libraries/' + id,
    method: 'delete'
  })
}

// 导入热词库
export function importHotwordLibrary(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/api/v1/asr/hotwords/libraries/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 导出热词库
export function exportHotwordLibrary(id) {
  return request({
    url: '/api/v1/asr/hotwords/libraries/' + id + '/export',
    method: 'get',
    responseType: 'blob'
  })
}

// 获取热词列表
export function getHotwords(libraryId) {
  return request({
    url: '/api/v1/asr/hotwords',
    method: 'get',
    params: { libraryId }
  })
}

// 添加热词
export function addHotword(data) {
  return request({
    url: '/api/v1/asr/hotwords',
    method: 'post',
    data
  })
}

// 更新热词
export function updateHotword(id, data) {
  return request({
    url: '/api/v1/asr/hotwords/' + id,
    method: 'put',
    data
  })
}

// 删除热词
export function deleteHotword(id) {
  return request({
    url: '/api/v1/asr/hotwords/' + id,
    method: 'delete'
  })
}

// 批量导入热词
export function batchImportHotwords(libraryId, file) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('libraryId', libraryId)

  return request({
    url: '/api/v1/asr/hotwords/batch-import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除文件
export function deleteFile(fileId) {
  return request({
    url: `/api/files/${fileId}`,
    method: 'delete'
  })
} 