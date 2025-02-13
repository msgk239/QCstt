# API 路径规范文档

> **注意**: 本文档为API设计规范指南。实际API接口定义请参考FastAPI自动生成的OpenAPI文档：
> - 开发环境：http://localhost:8010/docs 
> - OpenAPI JSON：http://localhost:8010/openapi.json

> **补充说明**: 以下功能在OpenAPI规范之外：
> - WebSocket接口 (/api/v1/ws/asr/progress/{file_id})
> - 认证方式 (Bearer Token)
> - 速率限制 (100次/分钟)
> - 批量删除接口 (POST /api/v1/files/batch-delete)

## API 设计原则
1. 统一使用 `/api/v1` 作为基础路径
2. 使用复数形式表示资源集合
3. 使用连字符 `-` 连接多个单词
4. 使用小写字母
5. 避免在路径中使用动词，用 HTTP 方法表达动作

## 响应格式

### 1. 基础响应格式
所有 JSON 响应都包含 code 和 message：
```json
{
    "code": 200,
    "message": "success"
}
```

### 2. 文件信息响应
文件相关接口返回带 data 的响应：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "20250109_191840_测试文件.wav",
        "original_name": "原始文件.wav",
        "display_name": "测试文件",
        "display_full_name": "测试文件.wav",
        "storage_name": "20250109_191840_测试文件.wav",
        "extension": ".wav",
        "size": 1024000,
        "date": "2025-01-09T19:18:40Z",
        "status": "已上传",
        "path": "/storage/audio/20250109_191840_测试文件.wav",
        "duration": 150.5,
        "duration_str": "2:30",
        "options": {
            "action": "upload",
            "language": "zh"
        }
    }
}
```

### 3. 分页列表响应
列表接口返回统一的分页格式：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20
    }
}
```

### 4. 识别进度响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "progress": 75,
        "status": "processing",
        "message": "正在识别..."
    }
}
```

## 1. 文件管理 (`/api/v1/files`)
### 基础操作
```
GET    /api/v1/files              # 获取文件列表
参数:
- page: 页码 (默认: 1, 最小: 1)
- page_size: 每页数量 (默认: 20, 最小: 1, 最大: 100)
- query: 搜索关键词

POST   /api/v1/files/upload       # 上传文件
请求体 (multipart/form-data):
- file: 文件二进制数据 (必填)
- options: JSON字符串 (可选)

GET    /api/v1/files/{file_id}    # 获取文件详情
DELETE /api/v1/files/{file_id}    # 删除文件
PUT    /api/v1/files/{file_id}    # 更新文件信息
```

### 文件资源
```
GET    /api/v1/files/{file_id}/audio       # 获取音频文件
GET    /api/v1/files/{file_id}/path        # 获取文件路径
PUT    /api/v1/files/{file_id}/rename      # 重命名文件
请求体 (application/x-www-form-urlencoded):
- new_name: 新文件名 (必填)

GET    /api/v1/files/{file_id}/transcript  # 获取转写结果
PUT    /api/v1/files/{file_id}/transcript  # 更新转写结果
请求体 (application/json)

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
参数:
- page: 页码 (默认: 1, 最小: 1)
- page_size: 每页数量 (默认: 20, 最小: 1, 最大: 100)
- query: 搜索关键词

POST   /api/v1/trash/{file_id}/restore    # 恢复文件
DELETE /api/v1/trash/{file_id}            # 永久删除文件
DELETE /api/v1/trash                      # 清空回收站
```

## 4. 系统设置 (`/api/v1/system`)
```
GET    /api/v1/system/languages           # 获取支持的语言列表
GET    /api/v1/system/status              # 获取系统状态
```

## 错误响应
```json
{
    "detail": [
        {
            "loc": ["path", "file_id"],  // 错误位置
            "msg": "file not found",     // 错误信息
            "type": "value_error"        // 错误类型
        }
    ]
}
```

### 常见状态码
- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 禁止访问
- 404: 资源不存在
- 422: 请求验证错误
- 500: 服务器内部错误

## 版本控制
1. 在 URL 中使用 `v1` 表示当前版本
2. 未来版本更新使用 `v2`, `v3` 等
3. 保持向后兼容性

## 注意事项
1. 所有时间戳使用 ISO 8601 格式 (例如: 2025-01-09T19:18:40Z)
2. 文件ID使用标准格式：`{timestamp}_{name}.{ext}`
3. 分页参数统一使用 `page` 和 `page_size`
4. 查询参数统一使用 `query`
5. 所有 JSON 响应都包含 code 和 message 字段
6. 复杂响应使用 data 字段包装数据