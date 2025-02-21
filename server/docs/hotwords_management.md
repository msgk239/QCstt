# 热词管理系统开发文档

## 功能概述

开发一个与 keywords 文件同步的热词管理系统，实现前后端双向同步，并确保数据的正确性和安全性。

## 系统架构

### 后端文件结构

```
server/
├── api/
│   ├── speech/
│   │   ├── keywords              # 原始 keywords 文件
│   │   ├── keywords.backup       # 自动备份文件
│   │   ├── update_keywords.py    # 现有的更新脚本
│   │   └── hotwords.py          # 新增：热词管理接口处理
│   └── app.py                    # 新增热词管理相关路由
```

### 前端文件结构

```
frontend/src/
├── api/
│   └── hotword.js               # 热词管理 API 接口
├── views/
│   └── HotwordsManagement.vue   # 新增：热词管理页面
└── components/
    └── AppSidebar.vue           # 修改：添加导航入口
```

## API 接口设计

### 1. 获取热词列表

```python
@app.route('/api/hotwords', methods=['GET'])
def get_hotwords():
    return {
        'code': 0,
        'data': {
            'content': '文件内容',
            'lastModified': '最后修改时间'
        }
    }
```

### 2. 更新热词

```python
@app.route('/api/hotwords', methods=['POST'])
def update_hotwords():
    return {
        'code': 0,
        'message': '更新成功'
    }
```

### 3. 验证热词格式

```python
@app.route('/api/hotwords/validate', methods=['POST'])
def validate_hotwords():
    return {
        'code': 0,
        'data': {
            'isValid': True,
            'errors': []
        }
    }
```

## 前端页面功能

### 1. 编辑器功能

- 语法高亮
- 行号显示
- 实时格式检查
- 错误提示

### 2. 格式检查规则

- 重复目标词检查
- 格式规范检查：
  - 空格数量
  - 阈值格式 (0-1之间的数字)
  - 括号匹配
  - 逗号格式

### 3. 操作功能

- 保存
- 导出备份
- 撤销/重做
- 格式化


## 后续优化

1. 功能扩展

   - 批量导入
   - 智能纠错
   - 统计分析
2. 性能优化

   - 大文件处理
   - 缓存机制
   - 增量更新
3. 用户体验

   - 快捷键支持
   - 主题定制
   - 操作引导


## 测试方案

- 内容加载与保存
- 实时格式验证
- 页面加载 < 1s

