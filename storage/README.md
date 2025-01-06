# 存储目录说明

本目录用于存储系统所有文件，包括音频文件、转写文本、历史版本等。

## 目录结构

```
storage/
├── uploads/                    # 上传文件存储
│   └── audio/                 # 音频文件存储
│       └── YYYYMMDD/         # 按日期分类
│           └── {fileId}/     # 每个文件独立目录
│               ├── original/  # 原始文件
│               └── converted/ # 转换后的文件
│
├── transcripts/               # 转写文本相关
│   ├── raw/                  # 原始转写结果
│   │   └── YYYYMMDD/        # 按日期分类
│   │       └── {fileId}.json # 包含时间戳、说话人等信息
│   │
│   ├── autosave/             # 自动保存的版本
│   │   └── YYYYMMDD/        # 按日期分类
│   │       └── {fileId}/    # 每个文件的自动保存历史
│   │           ├── {timestamp}_1.json
│   │           ├── {timestamp}_2.json
│   │           └── latest.json
│   │
│   ├── versions/             # 用户手动保存的版本
│   │   └── YYYYMMDD/        # 按日期分类
│   │       └── {fileId}/    # 每个文件的版本历史
│   │           ├── v1.json  # 包含版本说明
│   │           └── v2.json
│   │
│   └── exports/             # 导出文件（系统默认位置）
│       ├── txt/            # 纯文本格式
│       ├── docx/           # Word文档格式
│       ├── pdf/            # PDF格式
│       └── srt/            # 字幕文件格式
│
├── trash/                    # 回收站目录
│   └── YYYYMMDD/           # 按删除日期分类
│       └── {fileId}/       # 被删除的文件
│           ├── audio/      # 音频文件
│           └── transcripts/ # 相关的转写文本
│
└── temp/                    # 临时文件目录
    └── YYYYMMDD/           # 按日期分类
```

## 目录说明

### uploads/audio/
- 存储用户上传的音频文件
- 按日期和文件ID组织目录结构
- original/ 保存原始文件
- converted/ 存放转换后的标准格式文件
- 支持格式：WAV、MP3、FLAC、OGG
- 单个文件大小限制：50MB

### transcripts/raw/
- 存储语音识别的原始结果
- JSON格式，包含：
  * 时间戳信息
  * 说话人识别结果
  * 文本内容
  * 置信度
- 作为所有后续编辑的基准版本

### transcripts/autosave/
- 编辑过程中的自动保存版本
- 每5分钟自动保存一次
- 保留最近10个版本
- latest.json 始终指向最新版本
- 超过30天的自动保存版本会被自动清理

### transcripts/versions/
- 用户手动保存的版本点
- 每个版本包含：
  * 版本号
  * 保存时间
  * 修改说明
  * 修改人
  * 完整的文本内容
- 支持版本回退和比较

### transcripts/exports/
- 系统默认的导出文件存储位置
- 按格式分类存储
- 支持批量导出
- 导出文件保留7天后自动清理
- 支持的格式：
  * TXT：纯文本格式
  * DOCX：Word文档
  * PDF：PDF文件
  * SRT：字幕文件

### trash/
- 存储被删除的文件
- 保留原始目录结构
- 保留期限：30天
- 支持文件恢复
- 超期文件自动清理

### temp/
- 存储处理过程中的临时文件
- 用于文件转换和处理
- 每天自动清理
- 不需要备份

## 文件命名规则

1. 文件ID格式：32位UUID
2. 时间戳格式：YYYYMMDD_HHMMSS
3. 版本号格式：v1, v2, v3...
4. 自动保存格式：{timestamp}_序号.json
5. 导出文件格式：{原文件名}_{时间戳}.{扩展名}

## 清理策略

1. temp/：每天清理
2. autosave/：保留30天
3. exports/：保留7天
4. trash/：保留30天

## 备份策略

1. uploads/：每日增量备份
2. transcripts/：每日增量备份
3. temp/：不备份
4. trash/：不备份

## 注意事项

1. 文件操作建议使用异步方式
2. 大文件处理时注意内存使用
3. 定期检查磁盘空间
4. 保持目录结构完整性
5. 注意文件权限管理 