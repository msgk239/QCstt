/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的大小
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

/**
 * 格式化音频时长
 * @param {number} seconds 秒数
 * @returns {string} 格式化后的时长
 */
export function formatDuration(seconds) {
  if (!seconds || isNaN(seconds)) return '00:00'
  
  // 将秒数向下取整，避免出现小数
  seconds = Math.floor(seconds)
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  // 确保分钟和秒都是两位数格式
  const formattedMinutes = String(minutes).padStart(2, '0')
  const formattedSeconds = String(remainingSeconds).padStart(2, '0')
  
  return `${formattedMinutes}:${formattedSeconds}`
}

/**
 * 格式化文件状态
 * @param {string} status 状态码
 * @returns {Object} 格式化后的状态对象
 */
export function formatFileStatus(status) {
  const statusMap = {
    ready: { text: '待处理', type: 'info' },
    processing: { text: '处理中', type: 'warning' },
    success: { text: '已完成', type: 'success' },
    error: { text: '失败', type: 'danger' },
    deleted: { text: '已删除', type: 'info' }
  }
  return statusMap[status] || { text: '未知', type: 'info' }
}

/**
 * 格式化日期时间
 * @param {string|number|Date} date 日期
 * @param {boolean} [withTime=true] 是否包含时间
 * @returns {string} 格式化后的日期时间
 */
export function formatDateTime(date, withTime = true) {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  
  if (!withTime) return `${yyyy}-${mm}-${dd}`
  
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`
}

/**
 * 格式化文件名
 * @param {string} name 文件名
 * @param {number} [maxLength=20] 最大长度
 * @returns {string} 格式化后的文件名
 */
export function formatFileName(name, maxLength = 20) {
  if (!name) return ''
  if (name.length <= maxLength) return name
  
  const ext = name.split('.').pop()
  const nameWithoutExt = name.slice(0, -(ext.length + 1))
  const truncated = nameWithoutExt.slice(0, maxLength - 3) + '...'
  
  return ext ? `${truncated}.${ext}` : truncated
}

export const formatDisplayName = (fullName) => {
  if (!fullName) return ''
  const match = fullName.match(/\d{8}_\d{6}_(.+)/)
  return match ? match[1] : fullName
} 