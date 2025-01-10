# API 路径规范文档

## API 设计原则
1. 统一使用 `/api/v1` 作为基础路径
2. 使用复数形式表示资源集合
3. 使用连字符 `-` 连接多个单词
4. 使用小写字母
5. 避免在路径中使用动词，用 HTTP 方法表达动作

## 1. 文件管理 (`/api/v1/files`)
### 基础操作
```
GET    /api/v1/files              # 获取文件列表
POST   /api/v1/files/upload       # 上传文件
GET    /api/v1/files/{file_id}    # 获取文件详情
DELETE /api/v1/files/{file_id}    # 删除文件
PUT    /api/v1/files/{file_id}    # 更新文件信息
```

### 文件资源
```
GET    /api/v1/files/{file_id}/audio       # 获取音频文件
GET    /api/v1/files/{file_id}/path        # 获取文件路径
PUT    /api/v1/files/{file_id}/rename      # 重命名文件
GET    /api/v1/files/{file_id}/transcript  # 获取转写结果
PUT    /api/v1/files/{file_id}/transcript  # 更新转写结果
DELETE /api/v1/files/{file_id}/transcript  # 删除转写结果
```

## 2. 语音识别 (`/api/v1/asr`)
### 识别操作
```
POST   /api/v1/asr/recognize/{file_id}     # 开始识别
GET    /api/v1/asr/progress/{file_id}      # 获取识别进度
```

### 热词管理
```
GET    /api/v1/asr/hotwords               # 获取热词列表
POST   /api/v1/asr/hotwords               # 添加热词
PUT    /api/v1/asr/hotwords/{id}          # 更新热词
DELETE /api/v1/asr/hotwords/{id}          # 删除热词
POST   /api/v1/asr/hotwords/batch-import  # 批量导入热词
```

### 热词库管理
```
GET    /api/v1/asr/hotword-libraries              # 获取热词库列表
POST   /api/v1/asr/hotword-libraries              # 创建热词库
PUT    /api/v1/asr/hotword-libraries/{id}         # 更新热词库
DELETE /api/v1/asr/hotword-libraries/{id}         # 删除热词库
POST   /api/v1/asr/hotword-libraries/import       # 导入热词库
GET    /api/v1/asr/hotword-libraries/{id}/export  # 导出热词库
```

## 3. 回收站管理 (`/api/v1/trash`)
```
GET    /api/v1/trash                      # 获取回收站文件列表
POST   /api/v1/trash/{file_id}/restore    # 恢复文件
DELETE /api/v1/trash/{file_id}            # 永久删除文件
DELETE /api/v1/trash                      # 清空回收站
```

## 4. 系统设置 (`/api/v1/system`)
```
GET    /api/v1/system/languages           # 获取支持的语言列表
GET    /api/v1/system/status              # 获取系统状态
```

## 响应格式
所有 API 返回统一的 JSON 格式：
```json
{
    "code": 200,           // 状态码
    "message": "success",  // 状态信息
    "data": {             // 数据对象
        // 基础信息
        "id": "20250109_191840_测试文件.wav",  // 文件ID（完整存储文件名）
        "original_name": "原始文件.wav",       // 原始文件名
        "display_name": "测试文件",           // 清理后的显示名称（不带扩展名）
        "display_full_name": "测试文件.wav",  // 清理后的完整文件名
        "storage_name": "20250109_191840_测试文件.wav",  // 存储文件名
        "extension": ".wav",                  // 文件扩展名
        "size": 1024000,                     // 文件大小（字节）
        "date": "2025-01-09 19:18:40",       // 上传时间
        "status": "已上传",                   // 文件状态
        "path": "/storage/audio/20250109_191840_测试文件.wav",  // 文件路径

        // 音频特有信息
        "duration": 150.5,                    // 音频时长（秒）
        "duration_str": "2:30",               // 格式化的时长

        // 其他信息
        "options": {                          // 上传选项
            "action": "upload",               // 动作类型
            "language": "zh"                  // 识别语言
        }
    }
}
```

### 常见状态码
- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 禁止访问
- 404: 资源不存在
- 500: 服务器内部错误

## 版本控制
1. 在 URL 中使用 `v1` 表示当前版本
2. 未来版本更新使用 `v2`, `v3` 等
3. 保持向后兼容性

## 注意事项
1. 所有时间戳使用 ISO 8601 格式
2. 文件ID使用标准格式：`{timestamp}_{name}.{ext}`
3. 分页参数统一使用 `page` 和 `page_size`
4. 查询参数统一使用 `query` 