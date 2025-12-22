# 同步调用 API (Synchronous)

适用于 `qwen3-asr-flash` 模型，提供短音频（< 5分钟）的实时/流式识别。

## 服务地址

- **中国大陆（北京）**: `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- **国际（新加坡）**: `https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`

## 请求说明

- **Method**: POST
- **Headers**:
    - `Authorization`: `Bearer <YOUR_DASHSCOPE_API_KEY>`
    - `Content-Type`: `application/json`
    - `X-DashScope-SSE`: `enable` (可选，开启流式输出)

### 请求体参数

| 参数名 | 类型 | 必选 | 说明 |
| :--- | :--- | :--- | :--- |
| `model` | string | 是 | 固定为 `qwen3-asr-flash` |
| `input` | object | 是 | 包含输入消息 |
| `input.messages` | array | 是 | 消息列表 |
| `parameters` | object | 否 | 模型配置参数 |

#### `input.messages` 结构

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| `role` | string | `system` (用于配置 Context) 或 `user` (用于传输音频) |
| `content` | array | 内容列表 |

**示例 content**:
- 音频: `[{"audio": "https://example.com/file.mp3"}]`
- Context: `[{"text": "热词1, 热词2"}]`

#### `parameters` (asr_options)

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `language` | string | 指定语种 (zh, en, ja, 等)。不确定语种时请勿指定。 |
| `enable_itn` | boolean | 是否启用逆文本标准化 (ITN)，默认 false。 |

### 请求示例 (cURL)

```bash
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation \
-H "Authorization: Bearer $DASHSCOPE_API_KEY" \
-H "Content-Type: application/json" \
-d '{
    "model": "qwen3-asr-flash",
    "input": {
        "messages": [
            {
                "role": "system",
                "content": [{"text": "阿里云, DashScope"}]
            },
            {
                "role": "user",
                "content": [{"audio": "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"}]
            }
        ]
    },
    "parameters": {
        "enable_itn": true
    }
}'
```

## 响应说明

### 成功响应

```json
{
    "output": {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": [{"text": "欢迎使用阿里云。"}],
                    "annotations": [
                        {
                            "language": "zh",
                            "type": "audio_info",
                            "emotion": "neutral"
                        }
                    ]
                }
            }
        ]
    },
    "usage": {
        "input_tokens_details": {"text_tokens": 0},
        "output_tokens_details": {"text_tokens": 6},
        "seconds": 1
    },
    "request_id": "..."
}
```

### 字段说明

- **output.choices.message.content**: 识别出的文本。
- **output.choices.message.annotations**: 包含语种 (`language`) 和情感 (`emotion`) 信息。
- **usage.seconds**: 音频时长（秒）。

## 支持的输入格式

- **HTTP URL**: 公网可访问的音频链接。
- **Base64**: `data:audio/mp3;base64,xxxx...`
- **本地文件**: 通过 SDK 使用 `file://` 协议（不推荐用于高并发）。

支持格式: `mp3`, `wav`, `m4a`, `aac`, `flac`, `ogg` 等。
