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
  try {
    const response = await action()
    
    // 使用 request.js 的业务错误处理
    if (handleBusinessError(response, errorMessage)) {
      throw new Error(response.message || errorMessage)
    }
    
    // 成功时可以显示成功提示
    if (options.showSuccess) {
      ElMessage.success(options.successMessage || '操作成功')
    }
    
    return response.data
  } catch (error) {
    // 使用 request.js 的网络错误处理
    handleNetworkError(error, errorMessage)
    throw error
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