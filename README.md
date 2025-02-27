# QCstt
潜催语音转文字系统 (QianCui Speech-to-Text)

基于 FastAPI 和 Vue 3 开发的语音识别系统，支持多语言识别和多种音频格式。
本系统完全保护用户隐私，所有处理均在本地完成。

## 功能特点

- 可以本地无网处理，保护隐私
- 支持热词纠正，热词可以自定义
- 支持多种音频格式转换为文本
- 界面上可以批量改说话人名称
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
#### 2.1 安装 Scoop
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

#### 2.2 安装 FFmpeg
```bash
scoop install ffmpeg
```

#### 2.3 安装 Miniconda
```bash
scoop install miniconda3
```

### 3. 配置 Python 环境
#### 3.1 创建虚拟环境
```bash
# 在项目根目录创建 Python 3.9.21 环境
conda create --prefix ./.conda python=3.9.21 -y

# 激活项目本地环境
conda activate ./.conda
```

> 提示：也可以使用 VS Code 创建虚拟环境
> 1. 按 F1 打开命令面板
> 2. 输入并选择 "Python: Select Interpreter"
> 3. 选择创建新的虚拟环境，并选择 conda

#### 3.2 安装依赖
```bash
# 进入服务器目录
cd server

# 安装依赖
pip install -r requirements.txt
```

#### 3.3 临时修复
```bash
# 替换 funasr 文件（临时解决方案）
copy /Y auto_model.py ./.conda/Lib/site-packages/funasr/auto/auto_model.py
```

### 4. 启动服务
#### 4.1 启动后端
```bash
# 启动 API 服务
python -m server.api.app
```
服务端将在 http://localhost:8010 启动

#### 4.2 启动前端
```bash
# 进入前端目录
cd frontend

# 安装前端依赖
npm install

# 开发模式启动
npm run dev
```
前端将在 http://localhost:5173 启动

现在可以访问 http://localhost:5173 查看效果

#### 4.3 生产环境部署（可选）
```bash
# 构建前端项目
npm run build

# 预览模式启动
npm run preview
```
前端将在 http://localhost:4173 启动

## 运行方式说明

后端使用 Python FastAPI，前端使用 Vue 3。

### 不同运行模式

```bash
# 在项目根目录下运行

# 调试模式 (DEBUG)
python -m server.api.app
# 前端访问地址: http://localhost:5173 或 http://localhost:4173

# 生产环境调试 (INFO)
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

本项目使用了 FunASR (https://github.com/modelscope/FunASR?tab=readme-ov-file#license) ，其代码遵循 MIT 许可证，模型遵循 FunASR 模型开源许可证 (Version 1.1)。
