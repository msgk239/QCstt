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

## 功能特点

1. 基础功能：
   - 多语言识别：中文、英文、粤语、日语、韩语
   - 多格式支持：wav、mp3、flac、ogg
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

### 1. 模型服务层 (model_service.py)
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

### 2. API 服务层 (api_service.py)
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

## 界面设计说明

### 1. 上传/历史页面设计
主页面最上面写上潜催语音转文字系统
```
+--------+---------------------------------------+
| 导航   |              上传区域                  |
|--------|---------------------------------------|
| [主页] | 视图: [列表] [网格]  [搜索...] [筛选▼]|
|        |---------------------------------------|
|[回收站]| 文件名称    时长   状态    日期  操作 |
|        |---------------------------------------|
|        | 会议记录.mp3                          |
|        | 2小时15分   已完成   2024-03-10      |
|        | [打开] [删除] [导出] [重命名]         |
|        |---------------------------------------|
|        | 访谈录音.wav                          |
|        | 45分钟     处理中   2024-03-09       |
|        | [打开] [删除] [导出] [重命名]         |
+--------+---------------------------------------+
```

当点击左侧的[回收站]时，右侧内容区域切换为：
```
+--------+---------------------------------------+
| 导航   |     回收站                   [清空]   |
|--------|---------------------------------------|
| [主页] | 文件名称    删除时间          操作    |
|        |---------------------------------------|
|[回收站]| 会议记录.mp3                          |
|        | 2024-03-08  [恢复] [永久删除]        |
|        |---------------------------------------|
|        | 访谈录音.wav                          |
|        | 2024-03-07  [恢复] [永久删除]        |
+--------+---------------------------------------+
```

搜索和筛选功能：
```
+------------------------------------------+
| 筛选条件：                               |
| 时间范围：[开始日期] 至 [结束日期]       |
| 文件状态：[✓] 已完成 [✓] 处理中         |
| 文件大小：[最小] 至 [最大]               |
| 排序方式：[最近修改 ▼]                   |
+------------------------------------------+
```

上传确认界面：
```
+------------------------------------------+
|     文件上传确认                 [关闭]   |
+------------------------------------------+
| 待处理文件：                             |
| • 会议记录.mp3  (2小时15分钟)           |
| • 访谈录音.wav  (45分钟)                |
|------------------------------------------|
| 总计时长：3小时                          |
| 预计完成时间：约15分钟                   |
|------------------------------------------|
| 识别选项：                               |
| 语言：[自动检测 ▼]                      |
| 热词库：[默认热词库 ▼]                   |
|------------------------------------------|
| [开始转写] [取消]                        |
+------------------------------------------+
```

转写进度显示（右下角悬浮窗）：
```
+------------------------------------------+
|     正在转写 (2个文件)          [-] [×]  |
+------------------------------------------+
| 会议记录.mp3                             |
| [==========] 50%  还需 7:30             |
|------------------------------------------|
| 访谈录音.wav                             |
| [====------] 40%  还需 4:00             |
|------------------------------------------|
| [展开详情] [暂停] [取消]                 |
+------------------------------------------+
```

展开详情后：
```
+------------------------------------------+
|     正在转写 (2个文件)          [-] [×]  |
+------------------------------------------+
| 会议记录.mp3                             |
| [==========] 50%  预计还需 7分30秒       |
| • 正在处理：01:05:30 - 01:10:00         |
| • 文件大小：120MB                        |
|------------------------------------------|
| 访谈录音.wav                             |
| [====------] 40%  预计还需 4分钟         |
| • 正在处理：00:15:00 - 00:20:00         |
| • 文件大小：45MB                         |
|------------------------------------------|
| 总体进度：45%  预计还需 11分30秒         |
|------------------------------------------|
| [收起详情] [暂停] [取消]                 |
| 完成后：[✓] 自动打开编辑器               |
+------------------------------------------+
```

主要特点：
1. 上传确认界面：
   - 显示待处理文件列表
   - 显示总时长和预估时间
   - 可选择识别语言和热词库
   - 提供开始和取消选项

2. 转写进度界面：
   - 显示每个文件的进度条
   - 显示当前处理的时间段
   - 显示预计剩余时间
   - 支持暂停和取消
   - 可选择完成后的操作

### 2. 编辑/播放页面设计
```
+------------------------------------------+
| ← 返回    会议记录.mp3                   |
|          2小时15分钟  2024-03-10 转换    |
+------------------------------------------+
| [保存] [自动保存✓] [导出▼] [分享▼]       |
| • 5秒前已自动保存                        |
| [历史版本▼] [撤销] [重做]                |
+------------------------------------------+
|          波形图 + 播放头指示器            |
|     ====|===============================  |
|         ↓                                |
+------------------------------------------+
| 文本编辑工具栏：                         |
| [字体▼] [大小▼] [颜色▼] [背景色▼]       |
| [B] [I] [U] [删除线] [高亮]             |
| [添加注释] [插入时间戳]  

|                                          |
|   说话人1  12:05                         |
|   +----------------------------------+   |
|   |  这是转录的文本内容...           |   |
|   |  【当前播放位置的文本高亮显示】   |   |
|   +----------------------------------+   |
|                                          |
|   说话人2  12:06                         |
|   +----------------------------------+   |
|   |  另一段文本内容...               |   |
|   |  支持点击跳转     
|   |  这是加粗的文本                  |   |
|   |  这是带背景色的重点内容            |   |
|   +----------------------------------+   |
|                                          |
+------------------------------------------+
|     ◀◀  ▶  ▶▶    0.8x ▼   00:15:30    |
+------------------------------------------+

导出选项：
+------------------+
| [✓] Word文档     |
| [  ] PDF文件     |
| [  ] 纯文本      |
| [  ] Markdown    |
| [  ] SRT字幕     |
+------------------+

分享选项：
+------------------+
| 分享到微信       |
| • Word文档       |
| • PDF文件        |
|                  |
| [生成分享文件]   |
+------------------+
```

自动保存设置：
+-------------------------+
| [✓] 启用自动保存        |
| 保存间隔：[5分钟 ▼]     |
| 最大保存版本：[10 ▼]    |
+-------------------------+

历史版本面板：
+-------------------------+
|     历史版本            |
+-------------------------+
| • 当前版本              |
| • 10分钟前的版本        |
| • 1小时前的版本         |
| • 转换完成时的版本      |
|                        |
| [预览] [还原到此版本]   |
+-------------------------+
```
字体设置面板：
+-------------------------+
| 字体：                  |
| [✓] 微软雅黑           |
| [ ] 宋体               |
| [ ] 黑体               |
| 大小：[14px ▼]         |
+-------------------------+
颜色面板：
| 文字颜色：              |
| [■] [■] [■] [■] [■]   |
| 背景颜色：              |
| [■] [■] [■] [■] [■]   |
| [自定义颜色...]         |
+-------------------------+

主要功能：
1. 文本样式：
   - 字体选择和大小调整
   - 加粗、斜体、下划线
   - 文字颜色和背景色
   - 删除线和高亮标记

2. 注释功能：
   - 添加多类型注释
   - 支持不同图标标记
   - 注释可见性控制
   - 注释快速跳转

3. 编辑增强：
   - 选中文本快速样式
   - 格式刷功能
   - 样式模板保存
   - 快捷键支持

4. 其他功能：
   - 撤销/重做
   - 格式清除
   - 文本对齐
   - 缩进调整


```
+-------------------------+
|     说话人管理          |
+-------------------------+
| 原名称    →   新名称    |
| 说话人1  →   小明      |
| 说话人2  →   老师      |
|                        |
| [批量替换] [重置]      |
+-------------------------+
```

文本替换面板
```
+-------------------------+
|     文本替换            |
+-------------------------+
| 查找内容：             |
| [____________]         |
| 替换为：               |
| [____________]         |
|                        |
| [替换] [全部替换]      |
| 匹配到 5 处           |
+-------------------------+
```

热词管理系统
```
+----------------------------------------+
|     热词库管理                          |
+----------------------------------------+
| 当前启用的热词库：                      |
| [✓] 默认热词库                         |
| [✓] 医疗术语库                         |
| [  ] IT术语库                          |
| [  ] 金融术语库                        |
|----------------------------------------|
| [新建热词库] [导入] [导出]              |
|----------------------------------------|
| 热词列表（已合并所有启用的热词库）：     |
| +----------------+  +-----------------+ |
| | 专业术语       |  | 人名地名        | |
| | • OpenAI      |  | • 张三          | |
| | • ChatGPT     |  | • 北京          | |
| | [编辑] [删除]  |  | [编辑] [删除]   | |
| +----------------+  +-----------------+ |
|                                        |
| 优先级：默认热词库 > 医疗术语库         |
| [调整优先级] [添加热词] [批量导入]      |
+----------------------------------------+
``` 

## 项目结构
后端用py，前端是js也就是vue，后端不用管，已经配置好。
项目采用以下目录结构:

```
frontend/src/
├── api/                    // API 接口
│   ├── index.ts           // API 统一导出
│   ├── request.ts         // Axios 配置
│   └── modules/           
│       ├── file.ts        // 文件相关接口
│       └── asr.ts         // 语音识别接口
│
├── components/            // 组件
│   ├── layout/           // 布局组件
│   │   ├── AppHeader.vue    // 顶部标题栏
│   │   └── AppSidebar.vue   // 左侧导航栏
│   │
│   ├── file/             // 文件相关组件
│   │   ├── FileList.vue     // 列表视图
│   │   ├── FileGrid.vue     // 网格视图
│   │   ├── FileUpload.vue   // 文件上传
│   │   └── FileActions.vue  // 文件操作按钮组
│   │
│   └── common/           // 通用组件
│       ├── SearchBar.vue    // 搜索框
│       └── FilterPanel.vue  // 筛选面板
│
├── views/                // 页面
│   ├── HomeView.vue     // 主页(文件列表)
│   ├── TrashView.vue    // 回收站
│   └── EditorView.vue   // 编辑器页面
│
├── stores/              // 状态管理
│   └── fileStore.ts     // 文件相关状态
│
├── router/              // 路由
│   └── index.ts         // 路由配置
│
└── App.vue             // 根组件
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

