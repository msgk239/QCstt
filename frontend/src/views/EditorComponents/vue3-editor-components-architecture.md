# 编辑器组件说明

## 主编辑器
`EditorView.vue`: 编辑器主组件，负责整体布局和功能协调
- 布局结构：
  - 顶部标题栏和工具栏
  - 编辑工具栏
  - 主要内容区
  - 底部音频播放器
- 核心功能：
  - 音频播放控制
  - 转写内容编辑
  - 自动保存
  - 说话人管理
  - 状态管理

## 音频相关
- `AudioPlayer.vue`: 音频播放器组件，支持播放/暂停、进度控制、速度调节
  - 播放/暂停控制
  - 进度条拖动
  - 时间显示
  - 播放速度调节
- `SpeedMenuDialog.vue`: 播放速度设置对话框

## 文本编辑
- `EditToolbar.vue`: 文本编辑工具栏，包含格式化、添加注释等功能
- `UndoRedoToolbar.vue`: 撤销/重做操作工具栏
- `NoteToolbar.vue`: 笔记工具栏，用于添加和管理笔记
- `StyleTemplateToolbar.vue`: 样式模板工具栏，用于应用预设格式

## 转写内容
- `Transcript.vue`: 转写内容显示和编辑组件
  - 分段显示
  - 说话人标记
  - 时间戳显示
  - 实时编辑
- `SpeakerManager.vue`: 说话人管理相关
- `ReplaceDialog.vue`: 查找替换对话框
- `HotwordsDialog.vue`: 热词管理对话框

## 文件操作
- `ExportToolbar.vue`: 导出功能工具栏，支持多种格式导出
- `ShareToolbar.vue`: 分享功能工具栏

## 辅助功能
- `KeyboardShortcuts.js`: 键盘快捷键配置
- `eventBus.js`: 组件间事件通信

## 数据流
1. 文件加载
   - 获取文件信息
   - 加载音频文件
   - 加载转写内容

2. 状态管理
   - 播放状态
   - 编辑状态
   - 保存状态
   - 说话人信息

3. 自动保存
   - 定时保存
   - 手动保存

4. 事件处理
   - 音频控制
   - 内容编辑
   - 说话人变更
   - 格式应用

## 工具栏组件
- `Toolbar.vue`: 基础工具栏组件，包含常用操作按钮
