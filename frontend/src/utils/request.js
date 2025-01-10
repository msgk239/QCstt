// 添加响应拦截器
axios.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    // 统一错误处理
    let message = '';
    
    if (error.response) {
      // 服务器返回错误
      const status = error.response.status;
      switch (status) {
        case 400:
          message = '请求参数错误';
          break;
        case 401:
          message = '未授权访问';
          break;
        case 500:
          message = '服务器内部错误';
          break;
        default:
          message = `请求失败(${status})`;
      }
    } else if (error.request) {
      // 请求发出但没有响应
      message = '服务器无响应';
    } else {
      // 请求配置出错
      message = '请求配置错误';
    }

    // 使用 Element Plus 的消息提示
    ElMessage.error(message);
    
    // 返回 Promise.reject 便于后续处理
    return Promise.reject({
      code: error.response?.status || -1,
      message: message,
      detail: error.message
    });
  }
); 