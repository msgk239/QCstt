import request from '../request'

export const uploadMediaFile = async (file, options = {}) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('options', JSON.stringify(options))

  try {
    return request({
      url: '/api/v1/files/upload',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: options.onProgress
    })
  } catch (error) {
    console.error('Upload API error:', error.response?.data || error.message)
    throw error
  }
}

export const uploadApi = {
  uploadMedia: uploadMediaFile
} 