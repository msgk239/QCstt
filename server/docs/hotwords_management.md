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

## 数据同步机制

### 1. 自动备份
- 位置：与 keywords 同目录
- 文件名：keywords.backup
- 触发时机：每次成功更新后

### 2. 冲突处理
- 检测文件修改时间
- 提示用户是否覆盖
- 显示差异对比

### 3. 实时验证
- 编辑时实时检查格式
- 保存前完整验证
- 错误提示和位置定位

## 开发步骤

1. 后端开发
   - [ ] 创建 hotwords.py
   - [ ] 实现验证功能
   - [ ] 添加 API 路由
   - [ ] 实现备份机制

2. 前端开发
   - [ ] 添加导航入口
   - [ ] 创建编辑器页面
   - [ ] 实现格式检查
   - [ ] 添加操作功能

3. 测试和优化
   - [ ] 单元测试
   - [ ] 集成测试
   - [ ] 性能优化
   - [ ] 用户体验优化

## 注意事项

1. 数据安全
   - 必须有备份机制
   - 防止误操作
   - 权限控制

2. 格式规范
   - 严格遵循 keywords 文件格式
   - 实时验证
   - 清晰的错误提示

3. 用户体验
   - 操作简单直观
   - 响应及时
   - 错误提示友好

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

现在我要干新事情了，就是前端适配后端的纠正文字系统，需要一个地方，放和@keywords 一摸一样的页面，然后同步的，前端改后端变，后端改前端变，前端页面有格式检查，不能改错了，比如重复了会提示错误，格式不对，不如空格多了等，反正就是要求不能错了。然后最后可以导出备份功能，和自动备份到和keywords一个目录中的一个新文件中，每次覆盖这个文件内容就行。这样就万无一失了。
先建立一个文档吧，来说明接下来要干的事情。目前后端已经搞定，可以开始适配前端了。就是先建立一个接口吧，app.py中，然后新建一个py文件来专门搞这个事情，然后是上前端的api中哪个文件中改，应该是hotword.js，然后看看还改什么适配，最后建议页面，在主页面的左边，就是回收站下面建立，AppSidebar.vue文件中加一个叫热词管理，然后就是新建一个文件写热词的页面，在frontend\src\views这里新建一个文件写。以前的热词页面不用，不用管。
先新建个文档说明我要做的事情吧

## 测试方案

### 1. 后端单元测试
```python
# test_hotwords_manager.py
class TestHotwordsManager:
    def test_read_content(self):
        # 测试文件读取
        
    def test_update_content(self):
        # 测试内容更新
        
    def test_validate_content(self):
        # 测试格式验证
        - 空格检查
        - 括号匹配
        - 重复目标词
        - 阈值格式
        - 上下文词格式
        
    def test_backup_mechanism(self):
        # 测试备份机制
```

### 2. API 接口测试
```bash
# 使用 curl 测试
# 1. 获取内容
curl -X GET http://localhost:8010/api/v1/hotwords

# 2. 更新内容
curl -X POST http://localhost:8010/api/v1/hotwords \
  -H "Content-Type: application/json" \
  -d '{"content": "...", "lastModified": 1234567890}'

# 3. 验证内容
curl -X POST http://localhost:8010/api/v1/hotwords/validate \
  -H "Content-Type: application/json" \
  -d '{"content": "..."}'
```

### 3. 前端功能测试
1. 编辑器功能
   - 内容加载和显示
   - 实时格式验证
   - 错误信息提示
   - 保存功能验证

2. 并发控制
   - 文件修改时间检查
   - 保存冲突处理
   - 自动备份确认

3. 错误处理
   - 网络错误提示
   - 格式错误展示
   - 权限错误处理

### 4. 集成测试
1. 完整流程测试
   - 页面加载
   - 内容编辑
   - 格式验证
   - 文件保存
   - 备份确认

2. 异常场景测试
   - 网络断开情况
   - 文件占用情况
   - 权限不足情况
   - 内容过大情况

### 5. 性能测试
1. 响应时间
   - 页面加载时间 < 1s
   - 保存响应时间 < 2s
   - 验证响应时间 < 500ms

2. 并发处理
   - 多用户同时编辑
   - 频繁保存操作
   - 大文件处理

## 测试步骤

1. 单元测试
   - [ ] 编写测试用例
   - [ ] 运行后端单元测试
   - [ ] 检查测试覆盖率

2. 接口测试
   - [ ] 准备测试数据
   - [ ] 执行接口测试
   - [ ] 验证响应结果

3. 功能测试
   - [ ] 测试编辑器功能
   - [ ] 测试并发控制
   - [ ] 测试错误处理

4. 集成测试
   - [ ] 测试完整流程
   - [ ] 测试异常场景
   - [ ] 测试性能指标

## 测试环境

1. 开发环境
   - Node.js >= 14
   - Python >= 3.8
   - Vue 3.x
   - Element Plus

2. 测试工具
   - Python: pytest
   - API: curl/Postman
   - 前端: Vue Test Utils
   - 性能: Apache Bench

## 预期结果

1. 功能完整性
   - 所有基础功能正常工作
   - 错误处理机制完善
   - 数据同步正确

2. 性能指标
   - 页面响应及时
   - 资源占用合理
   - 并发处理正常

3. 用户体验
   - 操作流程顺畅
   - 错误提示清晰
   - 界面反馈及时