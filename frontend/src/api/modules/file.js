import request from '../request'

// 获取文件列表
export function getFileList(params) {
  return request({
    url: '/api/v1/files',
    method: 'get',
    params
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

// 更新文件
export function updateFile(id, data) {
  return request({
    url: '/api/v1/files/' + id,
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