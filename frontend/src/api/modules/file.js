import request from '../request'

// 获取文件列表
export function getFileList(params) {
  return request({
    url: '/api/v1/files',
    method: 'get',
    params
  })
}

// 获取单个文件详情
export function getFile(id) {
  return request({
    url: `/api/v1/files/${id}`,
    method: 'get'
  })
}

// 上传文件
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

// 获取文件详情
export function getFileDetail(id) {
  return request({
    url: '/api/v1/files/' + id,
    method: 'get'
  })
}

// 删除文件（移至回收站）
export function deleteFile(id) {
  return request({
    url: '/api/v1/files/' + id,
    method: 'delete'
  })
}

// 更新文件内容
export function updateFile(fileId, data) {
  return request({
    url: `/api/v1/files/${fileId}/transcript`,
    method: 'put',
    data
  })
}

// 恢复文件
export function restoreFile(id) {
  return request({
    url: '/api/v1/files/' + id + '/restore',
    method: 'post'
  })
}

// 永久删除文件
export function permanentlyDeleteFile(id) {
  return request({
    url: '/api/v1/files/' + id + '/permanently-delete',
    method: 'delete'
  })
}

// 导出文件
export function exportFile(id, format) {
  return request({
    url: '/api/v1/files/' + id + '/export',
    method: 'get',
    params: { format },
    responseType: 'blob'
  })
}

// 添加新方法：格式化文件数据
export function formatFileData(response) {
  const { data } = response
  console.log('Raw API data:', data)
  
  if (data.transcripts) {
    const { original, metadata } = data.transcripts
    
    // 从 original.json 中获取数据
    const recognitionData = original || {}
    
    return {
      id: data.id,
      name: data.name,
      duration: recognitionData.duration || 0,
      date: new Date(metadata?.created_at).toLocaleDateString(),
      status: metadata?.status || '未识别',
      segments: recognitionData.segments || [],  // 直接使用原始格式
      speakers: recognitionData.speakers || [],  // 直接使用原始格式
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

// 获取音频文件
export function getAudioFile(fileId) {
  return request({
    url: `/api/v1/files/${fileId}/audio`,
    method: 'get',
    responseType: 'blob'
  })
}

// 开始识别
export function startRecognition(fileId) {
  return request({
    url: `/api/v1/asr/recognize/${fileId}`,
    method: 'post'
  })
}

// 获取识别进度
export function getRecognitionProgress(fileId) {
  return request({
    url: `/api/v1/asr/progress/${fileId}`,
    method: 'get'
  })
}