# API 模块说明

## 核心模块关系

1. `utils.py` 作为基础工具层，提供纯函数工具集，不依赖其他模块，负责文件路径处理、JSON操作等底层功能。

2. `speech/storage.py` 作为存储层，依赖 utils.py，专注于转写结果的存储和读取，返回原始数据。

3. `files/service.py` 作为业务层，依赖 storage.py 和 utils.py，处理业务逻辑并提供标准的 API 响应格式。

## 路由说明
所有API路由统一使用 `/api/v1` 前缀，详细路径定义见 `API.md`。

## 文件服务模块 (`files/`)

### 模块职责
- `config.py`: 配置管理，提供存储路径等基础配置
- `metadata.py`: 元数据管理，处理文件时长、状态等信息
- `operations.py`: 文件操作，提供基础的文件读写功能
- `service.py`: 业务服务，协调各模块工作，处理业务逻辑

### 依赖关系
```
config.py <-- metadata.py <-- operations.py <-- service.py
                                                    ^
                                                    |
                                              speech模块, utils
```

### 文件命名规范
- 存储格式：`{timestamp}_{name}.{ext}`
  - timestamp: 格式为 `YYYYMMDD_HHMMSS`
  - name: 经过清理的文件名（去除特殊字符）
  - ext: 原始文件扩展名
- 示例：`20250109_191840_测试文件.wav`

### 文件元数据说明
文件上传后会保存以下元数据信息：
- 基础信息：
  - `id`: 文件唯一标识（同存储文件名）
  - `original_name`: 原始上传的文件名
  - `display_name`: 清理后的显示名称（不带扩展名）
  - `display_full_name`: 清理后的完整文件名
  - `storage_name`: 实际存储的文件名
  - `extension`: 文件扩展名
  - `size`: 文件大小（字节）
  - `date`: 上传时间（格式：YYYY-MM-DD HH:mm:ss）
  - `status`: 文件状态（如：已上传、处理中等）
  - `path`: 文件在服务器上的完整路径

- 音频特有信息：
  - `duration`: 音频时长（秒）
  - `duration_str`: 格式化的时长字符串（如："2:30"）

- 其他信息：
  - `options`: 上传时的选项参数（如：语言设置等）

### 文件名相关信息
- target_filename: 完整的存储文件名（如：`20250109_191840_测试文件.wav`）
- cleaned_name: 清理后的显示名称（如：`测试文件`）
- cleaned_full_name: 清理后的完整文件名（如：`测试文件.wav`）
- extension: 文件扩展名（如：`.wav`）

## 注意事项
1. 所有文件操作通过 `FileService` 进行
2. 文件ID使用完整文件名
3. 状态变更自动更新元数据 