# keywords文件及相关文件说明

## 文件关系图
```
keywords (源文件)
    │
    ├── custom_dict.txt (分词词典)
    │       └── 由_generate_custom_dict()生成
    │           - 包含目标词、错误词、上下文词
    │           - 按长度排序
    │           - 用于pkuseg分词器
    │           - 仅在keywords更新时重新生成
    │           - 自动去重并合并相同词条
    │
    ├── correction_config.yaml (配置缓存)
    │       └── 由load_config()生成
    │           - 缓存拼音计算结果
    │           - 存储阈值和上下文设置
    │           - 避免重复解析keywords
    │           - 仅在keywords更新时重新生成
    │           - 自动合并重复目标词配置
    │
    └── 内存数据结构
            ├── self.target_words
            │   - 格式: {word: (pinyin_list, context_words, threshold, orig_words)}
            │   - 用于相似度匹配
            │   - 合并后的去重配置
            │
            └── self.original_words_map
                - 格式: {orig_word: target_word}
                - 用于直接替换
                - 基于去重后的映射关系
```

## 核心文件说明

### 1. keywords文件
- **用途**：核心配置文件，定义所有纠正规则
- **格式**：
  ```
  目标词 [阈值] [原词列表] [(上下文词)]
  ```
- **示例**：
  ```
  灵体 0.8 林体,零体 (灵核,古零)
  灵体 0.7 灵替,零替 (灵核)  # 重复配置会被合并
  ```
- **字段说明**：
  - 目标词：要纠正到的目标词
  - 阈值：相似度匹配阈值，可选，默认0.8
  - 原词列表：直接替换的词列表，用逗号分隔
  - 上下文词：触发替换的上下文条件，用括号包围
- **重复处理**：
  - update_keywords.py：
    ```python
    def merge_configs(word: str, configs: List[Tuple[int, float, List[str], str]]) -> Tuple[float, List[str]]:
        # 收集所有非None的阈值
        thresholds = [t for _, t, _, _ in configs if t is not None]
        # 合并所有原词列表
        all_original_words = set()
        for _, _, orig_words, _ in configs:
            all_original_words.update(orig_words)
        # 使用最严格的（最大的）阈值
        final_threshold = max(thresholds) if thresholds else 0.9
        return (final_threshold, list(all_original_words))
    ```
  - text_correction.py：
    ```python
    # 检查是否是重复的目标词
    if word in keywords:
        if word not in duplicate_words:
            duplicate_words[word] = []
            # 记录第一次出现位置
            first_line = next(i for i, l in enumerate(lines, 1) 
                            if l.strip().split(maxsplit=1)[0] == word)
            duplicate_words[word].append((first_line, lines[first_line-1].strip()))
        duplicate_words[word].append((line_number, line))
        # 使用最大的阈值
        if threshold > thresholds[word]:
            thresholds[word] = threshold
        # 合并原词列表和上下文词
        original_words[word].update(orig_words)
        context_words[word].update(context_list)
    ```

### 2. custom_dict.txt
- **用途**：分词器的自定义词典
- **生成时机**：
  - 首次运行时（文件不存在）
  - keywords文件更新时（修改时间比dict新）
- **更新检查**：
  ```python
  def _should_update_dict(self) -> bool:
      # 检查文件是否存在
      if not os.path.exists(dict_path):
          return True
      # 比较修改时间
      return keywords_mtime > dict_mtime
  ```
- **生成逻辑**：
  1. 提取所有中文词（长度>1）
  2. 按长度降序排序
  3. 按优先级写入：目标词 > 错误词 > 上下文词
- **作用**：
  - 指导pkuseg分词器识别专业术语
  - 避免错误分词影响纠正效果

### 3. correction_config.yaml
- **用途**：配置缓存文件
- **内容**：
  ```yaml
  target_words:
    灵体:  # 合并后的配置
      pinyin: [ling2, ti3]
      context_words: [灵核, 古零]  # 合并后的上下文词
      similarity_threshold: 0.8    # 最大阈值
      original_words: [林体, 零体, 灵替, 零替]  # 合并后的原词列表
  ```
- **更新时机**：
  - 首次运行时（文件不存在）
  - keywords文件更新时（修改时间比config新）
- **更新检查**：
  ```python
  def _should_update_config(self) -> bool:
      # 检查文件是否存在
      if not os.path.exists(config_file):
          return True
      # 比较修改时间
      return keywords_mtime > config_mtime
  ```
- **作用**：
  - 缓存拼音计算结果
  - 避免重复解析keywords文件
  - 提高启动和运行效率

## 内存数据结构

### 1. self.target_words
- **用途**：存储目标词的完整信息
- **格式**：
  ```python
  {
    "灵体": (
      ["ling2", "ti3"],  # 拼音列表
      ["灵核", "古零"],   # 上下文词列表
      0.8,               # 相似度阈值
      ["林体", "零体"]    # 原词列表
    )
  }
  ```
- **使用场景**：
  - 相似度匹配
  - 上下文判断
  - 阈值检查

### 2. self.original_words_map
- **用途**：存储原词到目标词的直接映射
- **格式**：
  ```python
  {
    "林体": "灵体",
    "零体": "灵体"
  }
  ```
- **使用场景**：
  - 直接替换已知的错误词
  - 优先级高于相似度匹配

## 文件更新流程

1. 修改keywords文件
2. 程序检测到keywords更新：
   - 检查custom_dict.txt是否需要更新
     - 不存在或keywords更新时重新生成
     - 生成时自动去重合并
   - 检查correction_config.yaml是否需要更新
     - 不存在或keywords更新时重新生成
     - 更新时自动合并重复配置
   - 刷新内存数据结构
     - 使用合并后的配置初始化

## 重复配置处理流程

1. 发现重复目标词时：
   - 记录所有出现位置和原始行内容
   - 输出警告日志，显示重复位置
   - 自动合并配置：
     - 使用最大（最严格）的阈值
     - 合并所有原词列表（去重）
     - 合并所有上下文词（去重）
   - 输出合并结果日志：
     - 选择的阈值
     - 合并后的原词数量
     - 合并后的上下文词数量

2. 当前合并策略：
   - update_keywords.py：
     - 读取时收集所有配置
     - 使用merge_configs合并
     - 写入时使用合并后的配置
     - 会更新keywords文件内容
     - 不处理上下文词
   - text_correction.py：
     - 读取时直接合并
     - 生成配置时使用合并结果
     - 内存中只保留合并后的配置
     - 不会修改keywords文件
     - 会处理上下文词

3. 建议统一的处理逻辑：

   A. 抽取共用的合并逻辑：
   ```python
   def merge_configs(configs: List[Tuple[int, float, List[str], List[str], str]]) -> Tuple[float, List[str], List[str]]:
       """合并配置
       Args:
           configs: [(行号, 阈值, 原词列表, 上下文词列表, 原始行)]
       Returns:
           (合并后阈值, 合并后原词列表, 合并后上下文词列表)
       """
       # 收集所有非None的阈值
       thresholds = [t for _, t, _, _, _ in configs if t is not None]
       # 合并所有原词列表
       all_original_words = set()
       # 合并所有上下文词
       all_context_words = set()
       
       for _, _, orig_words, context_words, _ in configs:
           all_original_words.update(orig_words)
           all_context_words.update(context_words)
           
       # 使用最严格的阈值
       final_threshold = max(thresholds) if thresholds else 0.9
       return (final_threshold, list(all_original_words), list(all_context_words))
   ```

   B. 统一处理流程：
   1. 在 update_keywords.py 中：
      - 使用新的merge_configs处理所有配置
      - 保存完整的合并结果到keywords文件
      - 格式：`目标词 阈值 原词列表 (上下文词列表)`
      - 作为配置的规范化工具

   2. 在 text_correction.py 中：
      - 直接使用相同的merge_configs函数
      - 读取时合并配置到内存
      - 生成yaml缓存时使用合并结果
      - 专注于运行时的文本纠正

   C. 工作流程：
   1. 使用update_keywords.py规范化配置：
      - 合并重复配置
      - 规范化格式
      - 保存到keywords文件
   2. text_correction.py使用规范化后的配置：
      - 读取配置
      - 缓存到yaml
      - 用于文本纠正

   D. 优势：
   - 统一的合并逻辑
   - 清晰的职责分工
   - 避免配置不一致
   - 更好的可维护性

4. 实施建议：
   1. 先修改update_keywords.py：
      - 实现新的合并逻辑
      - 添加上下文词处理
      - 规范化输出格式
   2. 更新text_correction.py：
      - 使用相同的合并函数
      - 简化重复配置处理
   3. 更新现有配置：
      - 运行update_keywords.py清理配置
      - 检查合并结果
      - 确认功能正常

## 注意事项

1. keywords文件修改建议：
   - 保持格式规范
   - 合理设置阈值
   - 避免原词循环引用
   - 合理使用上下文条件
   - 尽量避免重复配置
   - 如有重复，确保配置兼容

2. 性能优化建议：
   - 定期清理无效配置
   - 及时更新常见错误词
   - 适当调整相似度阈值
   - 避免过多的上下文限制
   - 利用文件修改时间检查，避免不必要的重新生成
   - 合理使用重复配置合并机制 