# SenseVoice ASR 系统

基于 FastAPI 和 Vue 3 开发的语音识别系统，支持多语言识别和多种音频格式。
本系统完全保护用户隐私，所有处理均在本地完成。

## 隐私保护说明

1. 本地处理：
   - 所有音频识别在用户本地完成
   - 不会上传到任何服务器
   - 不需要网络连接
   - 开发者无法访问用户数据

2. 数据安全：
   - 音频文件仅在内存中处理
   - 处理完成后自动清除
   - 不保存任何音频文件
   - 识别结果只保存在用户本地

3. 技术实现：
   - 独立可执行文件
   - 本地服务运行在 localhost
   - 不包含任何远程调用
   - 无数据收集功能

4. 用户控制：
   - 用户可以随时关闭程序
   - 可以手动删除结果文件
   - 完全离线运行
   - 不需要注册或登录

## 系统架构

系统分为服务端和前端两部分：

### 服务端 (SenseVoice/)
- 基于 FastAPI 框架
- 支持多种音频格式：wav、mp3、flac、ogg
- 支持多语言识别：中文、英文、粤语、日语、韩语
- RESTful API 接口

### 前端 (frontend/)
- 基于 Vue 3 + Element Plus
- 支持文件拖拽上传
- 支持语言选择
- 识别结果展示和复制

## 环境要求

### 服务端要求
- Python 3.6+
- CUDA 支持（用于模型推理）
- 依赖包：
  - fastapi
  - uvicorn
  - torchaudio
  - funasr
  - python-multipart

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
cd SenseVoice
python api2.py
```
服务端将在 http://localhost:8000 启动

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

### Base64音频识别
```
POST /api/v1/asr/base64

请求体：
{
    "audio": "base64编码的音频数据",
    "language": "语言代码（可选）"
}
```

## 使用说明

1. 访问前端页面
2. 选择要识别的语言（可选，默认自动检测）
3. 拖拽音频文件或点击上传
4. 点击"开始识别"按钮
5. 等待识别完成，查看结果
6. 可以复制识别结果文本

## 注意事项

1. 支持的音频格式：wav、mp3、flac、ogg
2. 建议使用16KHz采样率的音频文件
3. 单个文件大小限制：50MB
4. 服务端默认使用 CUDA 进行模型推理，可通过环境变量配置：
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

## 许可证

[许可证类型] 

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