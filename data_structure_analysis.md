# 数据结构差异分析

## 1. 首次更新数据结构
```javascript
{
    type: 'content_update',
    segments: {
        merged: [{
            segmentId: "speaker_0_cKElFQ",
            speakerKey: "speaker_1",
            speakerDisplayName: "说话人 2",
            speaker_name: "说话人 2",
            start_time: 0,
            end_time: 48.52,
            text: "...",
            timestamps: [...],
            subSegments: [
                {
                    speaker_id: "speaker_1",
                    speaker_name: "说话人 2",
                    speakerKey: "speaker_1",
                    speakerDisplayName: "说话人 2",
                    color: "#409EFF",
                    ...
                }
            ]
        }]
    }
}
```

## 2. 普通文本更新结构
```javascript
{
    type: 'content_update',
    segments: {
        segmentId: "speaker_0_cKElFQ",
        speakerKey: "speaker_1",
        speakerDisplayName: "说话人 2",
        speaker_name: "说话人 2",
        start_time: 0,
        end_time: 48.52,
        text: "...",  // 文本内容有更新
        timestamps: [...],
        subSegments: [...]
    }
}
```

## 3. 说话人更新结构
```javascript
{
    type: 'speaker_update',
    segments: {
        merged: [{
            segmentId: "speaker_0_cKElFQ",
            speakerKey: "speaker_0",  // 变成了 speaker_0
            speakerDisplayName: "说话人 2",
            speaker_name: "说话人 2",
            ...
            subSegments: [
                {
                    speaker_id: "speaker_1",
                    speaker_name: "说话人 2",
                    speakerKey: "speaker_0",  // 子段落也更新了
                    speakerDisplayName: "说话人 2",
                    ...
                }
            ]
        }]
    },
    speakers: [...]  // 额外包含说话人列表
}
```

## 主要差异

1. 数据结构层级：
   - 首次更新：`segments.merged[]`
   - 普通文本更新：直接是 `segments{}`
   - 说话人更新：`segments.merged[]` + `speakers[]`

2. speakerKey 的变化：
   - 首次更新和文本更新：保持原有的 speakerKey
   - 说话人更新：speakerKey 发生变化，且同步更新到所有子段落

3. 数据完整性：
   - 首次更新：完整的段落数据
   - 文本更新：单个段落的数据
   - 说话人更新：完整的段落数据 + 说话人列表

4. type 字段：
   - 首次更新和文本更新：`content_update`
   - 说话人更新：`speaker_update`

## 后端处理逻辑

1. 说话人更新处理：
   - 通过 `type: 'speaker_update'` 进入专门的处理分支
   - 从 `segments.merged` 获取段落数据
   - 遍历每个段落，更新说话人信息
   - 同时更新 speakers 列表
   - 更新所有相关段落的 speakerKey 和显示名称

2. 普通文本更新处理：
   - 复制原有的 segments 数组
   - 从 `segments.subSegments` 获取子段落
   - 根据 subsegmentId 匹配并更新对应的段落（不是用 speakerKey）
   - 使用解构赋值更新整个段落：`{**orig_segment, **sub_segment}`
