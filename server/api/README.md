# API 模块说明

## 核心模块关系

1. `utils.py` 作为基础工具层，提供纯函数工具集，不依赖其他模块，负责文件路径处理、JSON操作等底层功能。

2. `speech/storage.py` 作为存储层，依赖 utils.py，专注于转写结果的存储和读取，返回原始数据。

3. `files/service.py` 作为业务层，依赖 storage.py 和 utils.py，处理业务逻辑并提供标准的 API 响应格式。

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
- 标准格式：`{timestamp}_{language}.{ext}`
- 示例：`20250109_191840_zh.wav`

## 注意事项
1. 所有文件操作通过 `FileService` 进行
2. 文件ID使用完整文件名
3. 状态变更自动更新元数据 