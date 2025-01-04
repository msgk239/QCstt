import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 获取支持的语言列表
export const getLanguages = () => {
  return api.get('/languages')
}

// 语音识别
export const recognizeAudio = (files, keys, language = 'auto') => {
  const formData = new FormData()
  
  // 处理多文件上传
  if (Array.isArray(files)) {
    files.forEach(file => {
      formData.append('files', file)
    })
  } else {
    formData.append('files', files)
  }
  
  formData.append('keys', keys)
  formData.append('lang', language)

  return api.post('/api/v1/asr', formData)
}

// 健康检查
export const checkHealth = () => {
  return api.get('/health')
} 