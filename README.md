# SenseVoice ASR 系统

基于 FastAPI 和 Vue 3 开发的语音识别系统，支持多语言识别和多种音频格式。
本系统完全保护用户隐私，所有处理均在本地完成。
计划使用 PyInstaller 打包成单个可执行文件，后续可能使用 WebView2（Windows 自带的浏览器组件）增强文件系统访问能力。





需要改py中的FunASR\funasr\auto\auto_model.py
D:\python3.12.8\Lib\site-packages\funasr\auto\auto_model.py




## 功能特点

1. 基础功能：
   - 多语言识别：中文、英文、粤语、日语、韩语
   - 多格式支持：全部格式
   - 完全离线：所有处理在本地完成

2. 说话人分离功能：
   - 自动区分不同说话人
   - 精确时间戳标注
   - 分段展示对话内容
   - 类似飞书妙记的展示效果

3. 高级编辑功能：
   - 说话人管理：
     * 支持批量修改说话人名称
     * 统一替换所有相同说话人
     * 说话人颜色自定义
   
   - 文本编辑：
     * Word式查找替换功能
     * 支持全文批量替换
     * 支持撤销/重做操作
   
   - 热词系统：
     * 支持多个热词库管理
     * 默认通用热词库
     * 支持导入/导出热词库
     * 支持新建自定义热词库
     * 分类管理热词
     * 批量导入热词功能

4. 交互功能：
   - 音频与文本联动：
     * 点击文本跳转对应音频位置
     * 点击音频时间轴定位文本
     * 播放时文本自动跟随高亮
   
   - 视图切换：
     * 支持列表/网格两种历史记录视图
     * 记住用户视图偏好设置

5. 数据管理：
   - 本地历史记录管理
   - 识别结果本地保存
   - 支持导出多种格式
   - 支持批量处理音频文件

## 系统架构
后端端口8010
系统分为三层架构：

### 1. 模型服务层 ()
- 负责模型调用和基础处理
- 集成 FunASR 语音识别
- 支持 VAD 语音活动检测
- 集成 CAMPPlus 说话人识别

关于说话人分离的重要说明：
1. 初始化参数设置：
   - spk_mode 必须在 AutoModel 初始化时设置，而不是在 generate 调用时
   - 正确设置：spk_mode="vad_segment"（使用 VAD 分割的说话人识别模式）

2. 聚类参数配置：
   - ClusterBackend 的参数名为 merge_thr 而不是 threshold
   - 示例配置：
     ```python
     spk_kwargs={
         "cb_kwargs": {
             "merge_thr": 0.5  # 控制说话人聚类的合并阈值
         },
         "return_spk_res": True
     }
     ```

3. 性能优化：
   - ncpu：设置 PyTorch 的线程数（建议为 CPU 核心数的 1/4 到 1/2）
   - batch_size：CPU 模式下建议保持为 1

4. 调试要点：
   - 检查 VAD 分割结果是否正确
   - 确认说话人嵌入向量的提取
   - 验证聚类结果的合理性
   - 观察时间戳的连续性

### 2. API 服务层 ()
- 基于 FastAPI 框架
- 处理音频文件上传
- 结果格式化处理
- 说话人分离数据处理

### 3. 前端展示层 (frontend/)
- 基于 Vue 3 + Element Plus
- 对话式展示界面
- 说话人分色显示
- 时间轴定位功能

## 环境要求

### 服务端要求
- Python 3.6+
- CUDA 或cpu（用于模型推理）
- 依赖包：
  - fastapi
  - uvicorn
  - torchaudio
  - funasr
  - python-multipart等

### 前端要求
- Node.js 14+
- npm 或 yarn

### 模型缓存说明

程序会自动处理模型文件的下载和缓存：

1. 默认情况（普通用户）：
   - 首次运行时，会在项目根目录创建 `.cache` 文件夹
   - 模型文件会下载到：
     * `.cache/modelscope` - ModelScope的模型文件
     * `.cache/huggingface` - Hugging Face的模型文件
   - 完全自动化，无需任何配置

2. 高级设置（可选）：
   - 可以通过环境变量自定义缓存位置：
     * `MODELSCOPE_CACHE` - ModelScope模型缓存路径
     * `HF_HOME` - Hugging Face模型缓存路径
   - 如果设置了环境变量，程序会优先使用指定的路径
   - 适合需要统一管理模型缓存的用户

3. 注意事项：
   - 首次运行需要下载模型文件（约500MB）
   - 请确保有足够的磁盘空间
   - 下载完成后会重复使用缓存的模型
   - 可以手动删除 `.cache` 文件夹释放空间

## 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd [项目目录]
```

2. 安装服务端依赖
```bash
cd SenseVoice
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

## 运行方法

1. 启动服务端
```bash
python -m server.api.app
```
服务端将在 http://localhost:8010 启动

2. 启动前端（开发模式）
```bash
cd frontend
npm run dev
```
前端将在 http://localhost:5173 启动（或其他可用端口）

## API 接口说明

### 获取支持的语言列表
```
GET /languages
```

### 音频识别
```
POST /api/v1/asr
Content-Type: multipart/form-data

参数：
- files: 音频文件（支持多文件）
- language: 识别语言（可选，默认自动检测）
```



## 注意事项

1. 建议使用16KHz采样率的音频文件
2. 单个文件大小限制：50MB
3. 服务端默认使用 CUDA 进行模型推理，可通过环境变量配置：
   ```bash
   export SENSEVOICE_DEVICE=cuda:0  # 使用第一个GPU
   ```

## 性能说明

1. CPU模式（4核心以上）：
   - 模型加载时间：约37秒
   - 音频处理速度：RTF约0.076（处理1秒音频需要0.076秒）
   - 2小时音频处理时间：约10分钟

2. GPU模式（NVIDIA显卡）：
   - 处理速度约为CPU模式的3-5倍
   - 2小时音频处理时间：约2-4分钟

## 打包说明

本项目支持打包成Windows可执行文件（exe），方便分发和使用。

### 打包步骤

1. 前端打包
```bash
cd frontend
npm run build
```

2. 安装打包工具
```bash
pip install pyinstaller
```

3. 打包命令
```bash
pyinstaller --name SenseVoice --add-data "frontend/dist;frontend/dist" --add-data "models;models" --hidden-import=tqdm --onefile app.py
```

### 打包注意事项

1. 文件大小：
   - 最终exe文件约500MB-1GB
   - 包含所有依赖和模型文件
   - 模型文件已内置（无需额外下载）：
     * SenseVoiceSmall语音识别模型
     * VAD语音活动检测模型
     * 多语言支持文件

2. 运行要求：
   - Windows 10/11 64位系统
   - 4GB以上内存
   - 不需要安装Python和Node.js
   - 不需要安装任何依赖
   - 不需要联网下载模型

3. 使用方法：
   - 双击exe文件运行
   - 自动启动服务和浏览器
   - 界面与开发版本完全相同
   - 完全傻瓜式操作：
     * 选择运行模式（自动/CPU/GPU）
     * 拖入音频文件
     * 选择语言（可选）
     * 点击识别
     * 获得文本结果

4. 性能说明：
   - 首次启动较慢（需要解压资源）
   - 运行性能与Python版本相同
   - 支持三种运行模式：
     * 自动模式：自动检测并使用最佳设备
     * GPU模式：强制使用GPU（需要NVIDIA显卡）
     * CPU模式：强制使用CPU（适用于所有设备）
   - GPU模式性能说明：
     * RTX系列：处理速度最快
     * GTX系列：性能适中
     * 其他NVIDIA显卡：性能因卡而异
   - CPU模式性能说明：
     * 推荐4核心以上CPU
     * 内存建议8GB以上
     * 适用于所有电脑



## 设备选择建议

1. 有NVIDIA显卡的用户：
   - 建议使用自动模式或GPU模式
   - 可获得最佳性能
   - 处理大文件更快

2. 无独立显卡的用户：
   - 自动使用CPU模式
   - 性能完全够用
   - 稳定可靠

3. 特殊情况：
   - 显卡内存不足：建议使用CPU模式
   - 显卡被其他程序占用：可切换到CPU模式
   - 需要同时处理多个任务：可根据需要切换模式 



## 项目结构
后端用 Python FastAPI，前端是 Vue 3。项目采用以下目录结构:

```
y2w/                           # 项目根目录
├── server/                    # 后端服务
│   └── api/                  # API 模块
│       ├── __init__.py       # 包标识（空文件）
│       ├── app.py            # FastAPI 应用主文件
│       ├── files/            # 文件处理模块
│       │   ├── __init__.py   # 包标识（空文件）
│       │   └── service.py    # 文件服务实现
│       ├── speech/           # 语音处理模块
│       │   ├── __init__.py   # 包标识（空文件）
│       │   ├── models.py     # 模型定义
│       │   └── recognize.py  # 语音识别实现
│       └── trash/            # 回收站模块
│           └── __init__.py   # 包标识（空文件）
├── storage/                  # 存储目录
│   ├── uploads/             # 上传文件目录
│   │   └── audio/          # 音频文件目录
│   └── trash/              # 回收站目录
└── frontend/                # 前端项目
    └── src/
        ├── api/            # API 接口
        ├── components/     # 组件
        ├── views/         # 页面
        └── stores/        # 状态管理
```

### 导入规范
同包内模块使用相对导入（如 `from .files import service`），外部包使用绝对导入（如 `import os`）。

### 运行方式

1. 开发环境运行（推荐）：
```bash
# 在项目根目录下运行
uvicorn server.api.app:app --host 0.0.0.0 --port 8010 --reload
```

2. 或者使用 Python 模块方式：
```bash
# 在项目根目录下运行
python -m server.api.app
```

注意：不要直接运行 Python 文件，这会导致相对导入错误：
```bash
# ❌ 错误：不要直接运行 Python 文件
python server/api/app.py
```

### 路径处理
所有文件路径操作都使用 `os.path` 处理，确保跨平台兼容：
```python
# ✅ 推荐：使用 os.path.join 拼接路径
file_path = os.path.join(self.audio_dir, filename)

# ❌ 不推荐：直接拼接字符串
file_path = self.audio_dir + "/" + filename
```

### 目录说明

1. api/: 接口相关
   - 处理请求配置和响应处理
   - 模块化组织不同功能的接口

2. components/: 组件
   - layout/: 布局相关组件
   - file/: 文件处理相关组件
   - common/: 通用组件

3. views/: 页面
   - 对应不同的路由页面
   - 组合各个组件形成完整页面

4. stores/: 状态管理
   - 管理全局状态
   - 处理组件间的数据共享

5. router/: 路由
   - 配置页面路由
   - 处理页面跳转逻辑

## 模块说明

### 1. API 模块 (`api/`)
- 主要职责：提供 HTTP API 接口
- 核心文件：`__init__.py`
  * FastAPI 应用初始化
  * CORS 配置
  * 路由定义
  * 请求处理

### 2. 文件管理模块 (`api/files/`)
- 主要职责：处理文件的上传、存储、删除等操作
- 核心功能：
  * 文件上传和保存
  * 文件列表管理
  * 文件删除（移到回收站）
  * 文件路径管理
- 关键文件：`service.py`
  * 实现 `FileService` 类
  * 处理所有文件相关操作

### 3. 语音识别模块 (`api/speech/`)
- 主要职责：处理语音识别相关功能
- 核心功能：
  * 语音模型管理
  * 语音识别处理
  * 说话人分离
  * 语言支持
- 关键文件：
  * `models.py`: 语音模型服务
  * `recognize.py`: 语音识别服务
  * `test_recognize.py`: 测试用例

### 4. 回收站模块 (`api/trash/`)
- 主要职责：管理已删除的文件
- 核心功能：
  * 回收站文件列表
  * 文件恢复
  * 永久删除
  * 清空回收站

## 主要功能流程

1. 文件上传流程：
   - 接收文件 → 生成时间戳文件名 → 保存到 audio 目录
   - 支持可选的自动识别

2. 语音识别流程：
   - 读取音频 → 模型识别 → 说话人分离 → 返回结果
   - 支持多种语言和自动语言检测

3. 文件删除流程：
   - 移动到回收站 → 保持原文件名 → 可恢复或永久删除

4. 回收站管理：
   - 查看已删除文件
   - 支持恢复或永久删除
   - 支持清空回收站

## 注意事项

1. 文件命名规则：
   - 格式：`YYYYMMDD_HHMMSS_原始文件名`
   - 示例：`20250106_151627_test.wav`

2. 目录结构：
   - 音频文件：`storage/uploads/audio/`
   - 回收站：`storage/trash/`

3. 预留功能：
   - 异步任务处理
   - 批量操作
   - 高级搜索

