import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as fileApi from '@/api/modules/file'
import { ElMessage } from 'element-plus'

export const useFileStore = defineStore('file', () => {
  // 状态
  const files = ref([])
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const loading = ref(false)
  const searchQuery = ref('')
  const sortBy = ref('date')
  const sortOrder = ref('desc')
  const viewMode = ref('list')

  // 计算属性
  const filteredFiles = computed(() => {
    return files.value.filter(file =>
      file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  })

  // 方法
  const fetchFiles = async () => {
    loading.value = true
    try {
      const res = await fileApi.getFileList({
        page: currentPage.value,
        pageSize: pageSize.value,
        query: searchQuery.value,
        sortBy: sortBy.value,
        sortOrder: sortOrder.value
      })
      files.value = res.items
      total.value = res.total
    } catch (error) {
      console.error('Failed to fetch files:', error)
      ElMessage.error('获取文件列表失败')
    } finally {
      loading.value = false
    }
  }

  const deleteFile = async (id) => {
    try {
      await fileApi.deleteFile(id)
      ElMessage.success('文件已移至回收站')
      await fetchFiles()
    } catch (error) {
      console.error('Failed to delete file:', error)
      ElMessage.error('删除文件失败')
    }
  }

  const updateFile = async (id, data) => {
    try {
      await fileApi.updateFile(id, data)
      ElMessage.success('文件信息已更新')
      await fetchFiles()
    } catch (error) {
      console.error('Failed to update file:', error)
      ElMessage.error('更新文件失败')
    }
  }

  const exportFile = async (id, format) => {
    try {
      const blob = await fileApi.exportFile(id, format)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'export.' + format
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('文件导出成功')
    } catch (error) {
      console.error('Failed to export file:', error)
      ElMessage.error('文件导出失败')
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
    files,
    currentPage,
    pageSize,
    total,
    loading,
    searchQuery,
    sortBy,
    sortOrder,
    viewMode,
    // 计算属性
    filteredFiles,
    // 方法
    fetchFiles,
    deleteFile,
    updateFile,
    exportFile,
    saveViewMode
  }
}) 