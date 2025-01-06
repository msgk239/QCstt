import request from '../request'

// 获取回收站文件列表
export function getTrashList(params) {
  return request({
    url: '/api/trash',
    method: 'get',
    params
  })
}

// 从回收站恢复文件
export function restoreFile(fileId) {
  return request({
    url: `/api/trash/${fileId}/restore`,
    method: 'post'
  })
}

// 永久删除文件
export function permanentlyDeleteFile(fileId) {
  return request({
    url: `/api/trash/${fileId}`,
    method: 'delete'
  })
}

// 清空回收站
export function clearTrash() {
  return request({
    url: '/api/trash',
    method: 'delete'
  })
} 