import { ElMessage } from 'element-plus'
import { handleBusinessError, handleNetworkError } from '@/api/request'

/**
 * 处理 store action 的统一封装
 * @param {Function} action - 要执行的异步操作
 * @param {string} errorMessage - 错误提示信息
 * @param {Object} options - 额外选项
 * @returns {Promise<any>} 处理结果
 */
export const handleStoreAction = async (action, errorMessage, options = {}) => {
  const {
    showSuccess = false,
    successMessage = '操作成功',
    throwOnError = true,
    validateResponse = (response) => response.code === 200
  } = options

  try {
    const response = await action()
    
    // 使用自定义的响应验证
    if (!validateResponse(response)) {
      const error = new Error(response.message || errorMessage)
      error.response = response
      throw error
    }
    
    // 成功时可以显示成功提示
    if (showSuccess) {
      ElMessage.success(successMessage)
    }
    
    return response
  } catch (error) {
    // 使用 request.js 的网络错误处理
    handleNetworkError(error, errorMessage)
    
    if (throwOnError) {
      throw error
    }
    
    return {
      code: error.response?.code || 500,
      message: error.message || errorMessage,
      data: null
    }
  }
}

/**
 * 处理批量操作的封装
 * @param {Function} action - 批量操作函数
 * @param {Array} items - 要处理的项目数组
 * @param {string} errorMessage - 错误提示信息
 * @returns {Promise<Array>} 处理结果
 */
export const handleBatchAction = async (action, items, errorMessage) => {
  const results = []
  const errors = []

  for (const item of items) {
    try {
      const result = await handleStoreAction(
        () => action(item),
        errorMessage,
        { showSuccess: false }
      )
      results.push(result)
    } catch (error) {
      errors.push({ item, error })
    }
  }

  // 汇总处理结果
  if (errors.length > 0) {
    ElMessage.warning(`完成 ${results.length} 项，失败 ${errors.length} 项`)
  } else {
    ElMessage.success('批量操作成功')
  }

  return { results, errors }
} 