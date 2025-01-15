+ ## 数据结构
+ 
+ ### 段落数据
+ ```javascript
+ {
+   // 原始字段（不变）
+   speaker_id: 'speaker_0',      // 原始说话人ID
+   speaker_name: '说话人 1',     // 原始说话人名字
+ 
+   // 前端使用的字段
+   speakerDisplayName: '张三',   // 显示用的名字
+   speakerKey: 'custom_1'       // 处理用的key
+ }
+ ```
+ 
+ ### 说话人数据
+ ```javascript
+ {
+   // 前端使用的字段
+   id: 'custom_1',              // 唯一key
+   name: '张三',                // 显示名字
+   color: '#409EFF',           // 显示颜色
+ 
+   // 原始字段（不变）
+   original_id: 'speaker_0',    // 原始ID
+   original_name: '说话人 1'    // 原始名字
+ }
+ ``` 