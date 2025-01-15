  ## 数据结构
  
### 段落数据
```javascript
{
  // 原始字段（不变）
  speaker_id: 'speaker_0',        // 原始说话人ID
  speaker_id: '说话人 1',       // 原始说话人名字
  
  // 前端使用的字段（可变）
  speakerKey: 'custom_1',         // 当前说话人Key
  speakerDisplayName: '张三',     // 显示用的名字
  color: '#409EFF',              // 显示颜色
  
  // 段落标识（可变）
  segmentId: 'custom_1_Ab3Kp9',   // 唯一标识符（speakerKey + nanoid(6)）
  
  // 时间信息（可变）
  start_time: 0,                  // 段落开始时间
  end_time: 5,                    // 段落结束时间
  
  // 子段落信息
  subSegments: [
    {
      subsegmentId: 'speaker_0-0-5',  // 子段落唯一标识（speaker_id + start_time + end_time）
      text: '段落1',                  // 子段落文本
      start_time: 0,                  // 子段落开始时间
      end_time: 5,                    // 子段落结束时间
      timestamps: [                   // 单词级别的时间戳（用于单词高亮）
        {
          text: '单',
          start: 0,
          end: 0.5
        },
        {
          text: '词',
          start: 0.5,
          end: 1
        }
      ]
    }
  ]
}
```

### 说话人数据
```javascript
{
  // 前端使用的字段（可变）
  speakerKey: 'custom_1',         // 唯一key
  speakerDisplayName: '张三',     // 显示名字
  color: '#409EFF',              // 显示颜色
  
  // 原始字段（不变）
  speaker_id: 'speaker_0',        // 原始ID
  speaker_name: '说话人 1'        // 原始名字
}
```

### 合并后的段落数据
```javascript
{
  // 段落标识（可变）
  segmentId: 'custom_1_Ab3Kp9',   // 合并后的唯一标识符（speakerKey + nanoid(6)）
  
  // 说话人信息
  speakerKey: 'custom_1',         // 当前说话人Key
  speakerDisplayName: '张三',     // 显示名字
  color: '#409EFF',              // 显示颜色
  
  // 原始字段（不变）
  speaker_id: 'speaker_0',        // 原始说话人ID
  speaker_name: '说话人 1',       // 原始说话人名字
  
  // 时间和文本信息
  start_time: 0,                  // 合并后的开始时间
  end_time: 10,                   // 合并后的结束时间
  text: '段落1\n段落2',          // 合并后的文本
  
  // 子段落信息
  subSegments: [
    {
      subsegmentId: 'speaker_0-0-5',  // 子段落唯一标识
      text: '段落1',
      start_time: 0,
      end_time: 5
    },
    {
      subsegmentId: 'speaker_0-5-10', // 子段落唯一标识
      text: '段落2',
      start_time: 5,
      end_time: 10
    }
  ]
}
```