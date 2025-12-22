# 异步调用 API (Asynchronous)

适用于 `qwen3-asr-flash-filetrans` 模型，专为长音频（最长 12 小时）识别设计。

## 1. 提交任务

### 请求地址

- **中国大陆（北京）**: `https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription`
- **国际（新加坡）**: `https://dashscope-intl.aliyuncs.com/api/v1/services/audio/asr/transcription`

### 请求说明

- **Method**: POST
- **Headers**:
    - `Authorization`: `Bearer <YOUR_DASHSCOPE_API_KEY>`
    - `Content-Type`: `application/json`
    - `X-DashScope-Async`: `enable` (必须)

### 请求体参数

| 参数名 | 类型 | 必选 | 说明 |
| :--- | :--- | :--- | :--- |
| `model` | string | 是 | `qwen3-asr-flash-filetrans` |
| `input` | object | 是 | 包含音频 URL |
| `parameters` | object | 否 | 配置参数 |

#### 参数详情

- **input.file_url**: (必选) 公网可访问的音频 URL。支持 OSS 临时 URL（需注意有效期）。
- **parameters.language**: (可选) 指定语种。
- **parameters.enable_itn**: (可选) 开启逆文本标准化。
- **parameters.channel_id**: (可选) 数组，指定需要识别的声道，如 `[0, 1]`。

### 响应 (任务提交成功)

```json
{
    "request_id": "...",
    "output": {
        "task_id": "8fab76d0-0eed-4d20-************",
        "task_status": "PENDING"
    }
}
```

## 2. 查询任务结果

### 请求地址

- **通用**: `https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}`
- **国际**: `https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}`

### 请求说明

- **Method**: GET
- **Headers**:
    - `Authorization`: `Bearer <YOUR_DASHSCOPE_API_KEY>`

### 响应 (任务完成)

```json
{
    "request_id": "...",
    "output": {
        "task_id": "...",
        "task_status": "SUCCEEDED",
        "result": {
            "transcription_url": "http://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/..."
        }
    },
    "usage": {
        "seconds": 120
    }
}
```

- **task_status**: `PENDING` (排队), `RUNNING` (处理中), `SUCCEEDED` (成功), `FAILED` (失败).
- **transcription_url**: 识别结果下载链接（24小时有效期）。

## 3. 识别结果说明

`transcription_url` 指向的 JSON 文件结构：

```json
{
    "file_url": "https://...",
    "transcripts": [
        {
            "channel_id": 0,
            "text": "全文内容...",
            "sentences": [
                {
                    "begin_time": 100,
                    "end_time": 3000,
                    "text": "第一句话。",
                    "emotion": "neutral",
                    "language": "zh"
                }
            ]
        }
    ]
}
```

- **sentences**: 包含句子级的时间戳 (`begin_time`, `end_time` 单位毫秒)、文本、情感 (`emotion`) 和语种 (`language`)。
