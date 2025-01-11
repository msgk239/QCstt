import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8010',
  timeout: 600000, // 10分钟超时
  headers: {
    'Content-Type': 'application/json'
  },
  // 允许跨域携带cookie
  withCredentials: true
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 如果是上传文件，不设置 Content-Type，让浏览器自动设置
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    // 检查请求方法是否正确
    if (!config.method) {
      config.method = 'get'  // 默认使用 GET 方法
    }
    
    // 添加详细的请求日志
    console.log('Request config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: config.data
    })
    
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 如果是二进制数据（如文件下载），直接返回
    if (response.config.responseType === 'blob') {
      return response
    }

    const res = response.data
    if (res.code !== 200) {
      // 返回错误响应而不是抛出错误，让调用方处理具体的错误信息
      return res
    }
    return res
  },
  error => {
    const errorCodes = {
      400: '请求参数错误',
      401: '未授权访问',
      403: '禁止访问',
      404: '资源不存在',
      422: '请求验证错误',
      500: '服务器内部错误'
    }
    
    let message = errorCodes[error.response?.status] || '网络错误'
    // 详细的错误信息处理
    if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status
      const data = error.response.data
      message = (data && data.message) || `请求失败(${status})`
    } else if (error.request) {
      // 请求发出但没有收到响应
      message = '服务器无响应'
    } else {
      // 请求配置出错
      message = error.message
    }
    
    // 让调用方处理错误消息的显示
    return Promise.reject({
      code: error.response?.status || 500,
      message: message
    })
  }
)

/**
 * 统一处理业务错误
 * @param {Object} response - API响应
 * @param {string} customMessage - 自定义错误消息
 * @returns {boolean} 是否有错误
 */
export function handleBusinessError(response, customMessage = '') {
  if (response.code !== 200) {
    ElMessage.error(customMessage || response.message)
    return true
  }
  return false
}

/**
 * 统一处理网络错误
 * @param {Error} error - 错误对象
 * @param {string} customMessage - 自定义错误消息
 */
export function handleNetworkError(error, customMessage = '') {
  ElMessage.error(customMessage || error.message || '网络请求失败')
}

export default service 