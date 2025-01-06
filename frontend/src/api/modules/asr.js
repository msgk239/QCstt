import request from '../request'

// 上传音频文件
export function uploadAudio(file, options = {}) {
  const formData = new FormData()
  formData.append('file', file)
  
  if (options.language) {
    formData.append('language', options.language)
  }

  if (options.hotwordLibraries) {
    formData.append('hotwordLibraries', JSON.stringify(options.hotwordLibraries))
  }

  const metadata = {
    originalName: file.name,
    size: file.size,
    type: file.type,
    lastModified: file.lastModified
  }
  formData.append('metadata', JSON.stringify(metadata))

  return request({
    url: '/api/v1/asr/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: options.onProgress
  })
}

// 获取转写进度
export function getProgress(taskId) {
  return request({
    url: '/api/v1/asr/progress/' + taskId,
    method: 'get'
  })
}

// 获取支持的语言列表
export function getSupportedLanguages() {
  return request({
    url: '/api/v1/asr/languages',
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