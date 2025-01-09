import { defineStore } from 'pinia'
import { ref } from 'vue'
import { updateFile } from '@/api/modules/file'

export const useFileStore = defineStore('file', () => {
  // 状态
  const currentFile = ref(null)
  const saving = ref(false)
  const lastSaveTime = ref(null)

  // 方法
  const saveFile = async (fileId, data) => {
    saving.value = true
    try {
      const result = await updateFile(fileId, data)
      if (result.code === 200) {
        lastSaveTime.value = new Date()
        return result
      }
      throw new Error(result.message)
    } finally {
      saving.value = false
    }
  }

  return {
    currentFile,
    saving,
    lastSaveTime,
    saveFile
  }
})