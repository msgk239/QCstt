import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as fileApi from '@/api/modules/file'
import { ElMessage } from 'element-plus'

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

  // 计算属性
  const filteredFiles = computed(() => {
    return fileList.value.filter(file =>
      file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  })

  // 方法
  const fetchFileList = async (params = {}) => {
    loading.value = true
    try {
      const res = await fileApi.getFileList({
        page: params.page || currentPage.value,
        page_size: params.page_size || pageSize.value,
        query: params.query || searchQuery.value,
        sort_by: params.sort_by || sortBy.value,
        sort_order: params.sort_order || sortOrder.value
      })
      
      if (res.code === 200) {
        fileList.value = res.data.items
        totalFiles.value = res.data.total
        currentPage.value = params.page || currentPage.value
        pageSize.value = params.page_size || pageSize.value
      } else {
        throw new Error(res.message || '获取文件列表失败')
      }
    } catch (error) {
      console.error('Failed to fetch files:', error)
      ElMessage.error(error.message || '获取文件列表失败')
    } finally {
      loading.value = false
    }
  }

  const deleteFile = async (id) => {
    try {
      const res = await fileApi.deleteFile(id)
      if (res.code === 200) {
        await fetchFileList()
        return res
      }
      throw new Error(res.message || '删除文件失败')
    } catch (error) {
      console.error('Failed to delete file:', error)
      throw error
    }
  }

  const renameFile = async (id, newName) => {
    try {
      const res = await fileApi.renameFile(id, newName)
      if (res.code === 200) {
        await fetchFileList()
        return res
      }
      throw new Error(res.message || '重命名文件失败')
    } catch (error) {
      console.error('Failed to rename file:', error)
      throw error
    }
  }

  const saveFile = async (fileId, data) => {
    saving.value = true
    try {
      const result = await fileApi.updateFile(fileId, data)
      if (result.code === 200) {
        lastSaveTime.value = new Date()
        return result
      }
      throw new Error(result.message || '保存文件失败')
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
    // 计算属性
    filteredFiles,
    // 方法
    fetchFileList,
    deleteFile,
    renameFile,
    saveFile,
    saveViewMode
  }
}) 