import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'
import { fileApi } from '@/api/modules/file'
import { ElMessage } from 'element-plus'
import { handleStoreAction } from '@/utils/storeHelpers'
import * as asrApi from '@/api/modules/asr'
import { uploadFile } from '@/api/modules/file'

export const useFileStore = defineStore('file', () => {
  // 状态
  const fileList = ref([])
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalFiles = ref(0)
  const loading = ref(false)
  const searchQuery = ref('')
  const sortBy = ref('date')
  const sortOrder = ref('desc')
  const viewMode = ref('list')
  const currentFile = ref(null)
  const saving = ref(false)
  const lastSaveTime = ref(null)
  const selectedFiles = ref([])
  const batchOperating = ref(false)
  const uploadDialogVisible = ref(false)
  const operationStates = reactive({
    delete: false,
    rename: false,
    recognize: false,
    export: false
  })
  const uploadProgress = ref({})
  const uploadStatus = ref({})

  // 计算属性
  const filteredFiles = computed(() => {
    if (!searchQuery.value) return fileList.value
    const query = searchQuery.value.toLowerCase()
    return fileList.value.filter(file => 
      file.name.toLowerCase().includes(query) || 
      file.type.toLowerCase().includes(query)
    )
  })

  const sortedFiles = computed(() => {
    const files = [...filteredFiles.value]
    return files.sort((a, b) => {
      if (sortBy.value === 'date') {
        return sortOrder.value === 'desc' 
          ? new Date(b.date) - new Date(a.date)
          : new Date(a.date) - new Date(b.date)
      }
      // 其他排序逻辑...
      return 0
    })
  })

  // 方法
  const fetchFileList = async (params = {}) => {
    loading.value = true
    try {
      const response = await fileApi.getList({
        page: params.page || currentPage.value,
        page_size: params.page_size || pageSize.value,
        query: params.query || searchQuery.value,
        sort_by: params.sort_by || sortBy.value,
        sort_order: params.sort_order || sortOrder.value
      })
      
      fileList.value = response.data.items
      totalFiles.value = response.data.total
      currentPage.value = params.page || currentPage.value
      pageSize.value = params.page_size || pageSize.value
    } catch (error) {
      console.error('获取文件列表失败:', error)
      ElMessage.error('获取文件列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteFile = async (id) => {
    return handleStoreAction(
      () => fileApi.delete(id),
      '删除文件失败'
    )
  }

  const renameFile = async (id, newName) => {
    return handleStoreAction(
      () => fileApi.renameFile(id, newName),
      '重命名文件失败'
    )
  }

  const saveFile = async (fileId, data) => {
    saving.value = true
    lastSaveTime.value = new Date()
    
    try {
      console.log('开始保存文件:', {
        fileId,
        dataSize: JSON.stringify(data).length,
        data: data // 打印完整数据用于调试
      })
      
      const response = await fileApi.update(fileId, data)
      console.log('保存响应:', {
        code: response?.code,
        message: response?.message,
        data: response?.data,
        fullResponse: response
      })
      
      // 检查响应是否为空或无效
      if (!response) {
        throw new Error('服务器返回空响应')
      }
      
      // 检查响应格式
      if (typeof response !== 'object') {
        throw new Error(`响应格式错误: ${typeof response}`)
      }
      
      // 检查响应状态 - 现在同时检查 code 和 status
      if (response.code === 200 || (response.code === undefined && response.status === 200)) {
        ElMessage.success('保存成功')
        return response
      }
      
      // 处理非 200 状态码
      console.error('保存失败，响应详情:', {
        code: response.code,
        status: response.status,
        message: response.message,
        data: response.data
      })
      
      throw new Error(response.message || '保存失败')
    } catch (error) {
      console.error('保存出错:', {
        error,
        message: error.message,
        stack: error.stack,
        response: error.response
      })
      
      ElMessage.error(error.message || '保存失败')
      throw error
    } finally {
      saving.value = false
    }
  }

  // 视图模式持久化
  const loadViewMode = () => {
    const saved = localStorage.getItem('viewMode')
    if (saved === 'list' || saved === 'grid') {
      viewMode.value = saved
    }
  }

  const saveViewMode = () => {
    localStorage.setItem('viewMode', viewMode.value)
  }

  // 初始化
  loadViewMode()

  const batchDeleteFiles = async (ids) => {
    batchOperating.value = true
    try {
      await handleStoreAction(
        () => fileApi.batchDeleteFiles(ids),
        '批量删除文件失败'
      )
    } finally {
      batchOperating.value = false
    }
  }

  const toggleFileSelection = (fileId) => {
    const index = selectedFiles.value.indexOf(fileId)
    if (index === -1) {
      selectedFiles.value.push(fileId)
    } else {
      selectedFiles.value.splice(index, 1)
    }
  }

  const clearSelection = () => {
    selectedFiles.value = []
  }

  const fileStatusCount = computed(() => {
    return fileList.value.reduce((acc, file) => {
      acc[file.status] = (acc[file.status] || 0) + 1
      return acc
    }, {})
  })

  const startRecognition = async (fileId) => {
    operationStates.recognize = true
    try {
      const response = await asrApi.startRecognition(fileId)
      // ... 处理逻辑
      return response
    } finally {
      operationStates.recognize = false
    }
  }

  const exportFile = async (fileId, fileName) => {
    operationStates.export = true
    try {
      const response = await fetch(`/api/v1/files/${fileId}/audio`)
      if (!response.ok) {
        throw new Error('导出失败')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      setTimeout(() => {
        window.URL.revokeObjectURL(url)
      }, 100)
    } finally {
      operationStates.export = false
    }
  }

  const uploadFiles = async (files, options) => {
    try {
      const results = await Promise.all(
        files.map(file => uploadSingleFile(file, options))
      )
      await fetchFileList()
      return results
    } catch (error) {
      console.error('Upload files error:', error)
      throw error
    }
  }

  const uploadSingleFile = async (file, options) => {
    try {
      uploadStatus.value[file.uid] = 'uploading'
      uploadProgress.value[file.uid] = 0

      const response = await uploadFile(file, {
        ...options,
        onProgress: (event) => {
          if (event.total) {
            uploadProgress.value[file.uid] = Math.round(
              (event.loaded * 100) / event.total
            )
          }
        }
      })

      if (response.code === 200) {
        uploadStatus.value[file.uid] = 'success'
        uploadProgress.value[file.uid] = 100
        return response.data
      } else {
        throw new Error(response.message || '上传失败')
      }
    } catch (error) {
      uploadStatus.value[file.uid] = 'error'
      throw error
    }
  }

  return {
    // 状态
    fileList,
    currentPage,
    pageSize,
    totalFiles,
    loading,
    searchQuery,
    sortBy,
    sortOrder,
    viewMode,
    currentFile,
    saving,
    lastSaveTime,
    selectedFiles,
    batchOperating,
    uploadDialogVisible,
    operationStates,
    // 计算属性
    filteredFiles,
    sortedFiles,
    fileStatusCount,
    // 方法
    fetchFileList,
    deleteFile,
    renameFile,
    saveFile,
    saveViewMode,
    batchDeleteFiles,
    toggleFileSelection,
    clearSelection,
    startRecognition,
    exportFile,
    uploadFiles,
    uploadProgress,
    uploadStatus
  }
}) 