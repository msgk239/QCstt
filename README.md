# QCstt
潜催语音转文字系统 (QianCui Speech-to-Text)

基于 FastAPI 和 Vue 3 开发的语音识别系统，支持多语言识别和多种音频格式。
本系统完全保护用户隐私，所有处理均在本地完成。

## 功能特点

- 可以本地无网处理，保护隐私
- 支持热词纠正，热词可以自定义
- 支持多种音频格式转换为文本
- 界面上可以批量改说话人名词
- 点击文本可以出声，点击音频可以高亮滚动
- 可以直接在上面修改错别字
- 目前只支持导出word

## 系统要求
- Windows 11 系统
- FFmpeg（用于音频处理）
- Miniconda（Python虚拟环境管理工具）


## 安装步骤

### 1. 下载本项目
```bash
# 浅克隆（shallow clone）下载最新的提交
git clone --depth=1 https://github.com/msgk239/QCstt.git

# 或者完整克隆
git clone https://github.com/msgk239/QCstt.git
```

### 2. 安装必要工具
```bash
# 安装FFmpeg
winget install Gyan.FFmpeg

# 安装Miniconda
winget install Anaconda.Miniconda3
```

### 3. 安装后端的依赖
```bash
# 在项目根目录创建Python 3.9.21环境
# conda create: 创建一个新的conda虚拟环境
# --prefix ./.conda: 指定环境创建在当前项目根目录下的.conda文件夹中
# python=3.9.21: 指定Python版本为3.9.21
# -y: 自动确认所有提示，不需要手动确认
conda create --prefix ./.conda python=3.9.21 -y

# 激活项目本地环境
# 注意：使用--prefix创建的环境需要使用完整路径激活
conda activate ./.conda

# 临时修复：替换funasr文件
# 注意：这是临时解决方案，当funasr更新后将不再需要此步骤
# 将项目根目录下的auto_model.py文件复制到本地conda环境的funasr包目录中，覆盖原有文件
# 如果提示是否覆盖，请选择Y(是)
copy /Y auto_model.py ./.conda/Lib/site-packages/funasr/auto/auto_model.py

# 进入服务器目录
cd server

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动后端服务
```bash
# 启动API服务
python -m server.api.app
```
服务端将在 http://localhost:8010 启动

### 5. 启动前端（开发模式）
```bash
# 进入前端目录
cd frontend

# 安装前端依赖
npm install

# 开发模式启动
npm run dev
# 前端将在 http://localhost:5173 启动

# 到这里就可以到浏览器访问 http://localhost:5173 查看效果了

# 下面是构建和预览模式启动
# 构建前端项目
npm run build
# 预览模式启动
npm run preview
# 前端将在 http://localhost:4173 启动

#访问 http://localhost:4173 查看效果，没问题就可以按照下面的运行方式选择
```
## 运行方式说明

后端使用 Python FastAPI，前端使用 Vue 3。

### 不同运行模式

```bash
# 在项目根目录下运行

# 调试模式
python -m server.api.app
# 前端访问地址: http://localhost:5173 或 http://localhost:4173

# 生产环境调试
python -m server.api.QCstt
# 前端访问地址: http://localhost:8010

# 无任何日志的纯生产环境
python -m server.api.package
# 前端访问地址: http://localhost:8010
```

> 注意: 日志级别可通过修改 logger.py 来控制，支持 debug、info、warning、error 等级别

## 注意事项
- 界面有些功能没有实现，如果点击没反应说明还没有做
- 只支持中文，只支持音频，不支持视频
- 建议备份热词文件在server\api\speech\keywords
- 第一次下载模型需要联网，后面可以本地运行
- 有些文档不是最新的，请以代码为准
## 版权声明
Copyright © 2025 msgk - QCstt (潜催语音转文字系统)

本项目代码遵循 MIT 许可证。

本项目使用了 FunASR (https://github.com/modelscope/FunASR?tab=readme-ov-file#license)，其代码遵循 MIT 许可证，模型遵循 FunASR 模型开源许可证 (Version 1.1)。