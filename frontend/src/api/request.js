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
    console.log('收到响应:', {
      url: response.config.url,
      method: response.config.method,
      status: response.status,
      headers: response.headers,
      data: response.data
    })
    
    // 处理空响应
    if (response.data === null || response.data === '') {
      // 如果状态码是 200，认为操作成功
      if (response.status === 200) {
        return {
          code: 200,
          message: 'success',
          data: null
        }
      }
      
      return {
        code: response.status,
        message: '服务器返回空响应',
        data: null
      }
    }
    
    // 处理二进制响应
    if (response.config.responseType === 'blob') {
      console.log('Blob response:', {
        type: response.data.type,
        size: response.data.size,
        headers: response.headers
      })
      return response.data
    }

    // 检查响应格式
    const responseData = response.data
    if (typeof responseData !== 'object') {
      console.error('响应格式错误:', responseData)
      return {
        code: 500,
        message: '响应格式错误',
        data: null
      }
    }

    // 如果响应没有 code 字段，但状态码是 200，则认为成功
    if (responseData.code === undefined && response.status === 200) {
      return {
        code: 200,
        message: 'success',
        data: responseData
      }
    }

    return responseData
  },
  error => {
    // 修改错误处理部分
    const errorResponse = error.response || {}
    const status = errorResponse.status || 500
    const responseData = errorResponse.data || {}

    console.error('请求错误:', {
      status,
      url: error.config?.url,
      method: error.config?.method,
      response: errorResponse,
      data: responseData,
      error
    })

    // 统一使用安全访问
    const errorMessages = {
      400: responseData?.code ? `参数错误 (${responseData.code})` : '无效请求参数',
      401: '未授权访问',
      403: '禁止访问',
      404: '资源不存在',
      422: '请求验证错误',
      500: '服务器内部错误'
    }

    let message = errorMessages[status] || '网络错误'
    
    // 优先使用服务器返回的错误信息
    if (responseData.message) {
      message = responseData.message
    }

    // 特殊网络错误处理
    if (!error.response) {
      message = error.request ? '服务器无响应' : error.message
    }
    
    return Promise.reject({
      code: status,
      message: message,
      data: responseData,
      raw: error  // 保留原始错误对象
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