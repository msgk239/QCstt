import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getKeywordsContent, updateKeywordsContent, validateKeywordsContent } from '@/api/modules/hotword'

export const useHotwordStore = defineStore('hotword', () => {
  // 状态
  const content = ref('')
  const lastModified = ref(null)
  const loading = ref(false)
  const saving = ref(false)
  const errors = ref([])
  const isValid = ref(true)

  // 方法
  const fetchContent = async () => {
    loading.value = true
    try {
      const response = await getKeywordsContent()
      if (response.code === 0) {
        content.value = response.data.content
        lastModified.value = response.data.lastModified
      } else {
        throw new Error(response.message || '获取内容失败')
      }
    } catch (error) {
      console.error('获取热词内容失败:', error)
      ElMessage.error('获取热词内容失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const saveContent = async (newContent) => {
    saving.value = true
    try {
      const response = await updateKeywordsContent({
        content: newContent,
        lastModified: lastModified.value
      })
      
      if (response.code === 0) {
        content.value = newContent
        lastModified.value = Date.now()
        ElMessage.success('保存成功')
      } else {
        throw new Error(response.message || '保存失败')
      }
    } catch (error) {
      console.error('保存热词内容失败:', error)
      ElMessage.error(error.message || '保存失败')
      throw error
    } finally {
      saving.value = false
    }
  }

  const validateContent = async (newContent) => {
    try {
      const response = await validateKeywordsContent({
        content: newContent
      })
      
      if (response.code === 0) {
        errors.value = response.data.errors
        isValid.value = response.data.isValid
        return response.data
      } else {
        throw new Error(response.message || '验证失败')
      }
    } catch (error) {
      console.error('验证热词内容失败:', error)
      ElMessage.error('验证失败')
      throw error
    }
  }

  return {
    // 状态
    content,
    lastModified,
    loading,
    saving,
    errors,
    isValid,
    
    // 方法
    fetchContent,
    saveContent,
    validateContent
  }
}) 