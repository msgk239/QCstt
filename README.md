# SenseVoice ASR 系统
这是开发用的文档

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

使用 Python 模块方式：
```bash
# 在项目根目录下运行
python -m server.api.app
```

```

### 路径处理
所有文件路径操作都使用 `os.path` 处理，确保跨平台兼容：
```python
# ✅ 推荐：使用 os.path.join 拼接路径
file_path = os.path.join(self.audio_dir, filename)

# ❌ 不推荐：直接拼接字符串
file_path = self.audio_dir + "/" + filename
```


## 注意事项

1. 文件命名规则：
   - 格式：`YYYYMMDD_HHMMSS_原始文件名`
   - 示例：`20250106_151627_test.wav`


2. 预留功能：
   - 异步任务处理
   - 批量操作
   - 高级搜索

