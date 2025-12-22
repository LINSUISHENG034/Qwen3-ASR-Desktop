# 快速开始 (Quick Start)

本文档将帮助您快速接入 Qwen3-ASR 语音识别 API。

## 前置条件

1.  **获取 API Key**: 访问 [阿里云百炼控制台](https://help.aliyun.com/zh/model-studio/get-api-key) 获取 API Key。
2.  **配置环境**: 推荐将 API Key 配置为环境变量 `DASHSCOPE_API_KEY`。

## 1. 短音频识别 (Sync)

适用于 5 分钟以内的音频。

**Python 示例**:

```python
import os
import dashscope

dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

messages = [
    {"role": "user", "content": [{"audio": "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"}]}
]

response = dashscope.MultiModalConversation.call(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen3-asr-flash",
    messages=messages,
    result_format="message"
)
print(response)
```

## 2. 长音频识别 (Async)

适用于 12 小时以内的长音频，采用“提交任务 -> 轮询结果”的异步模式。

**Python 示例**:

```python
import os
import time
import requests
import json

API_URL_SUBMIT = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
API_URL_QUERY_BASE = "https://dashscope.aliyuncs.com/api/v1/tasks/"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable"
}

# 1. 提交任务
payload = {
    "model": "qwen3-asr-flash-filetrans",
    "input": {"file_url": "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"},
    "parameters": {"enable_itn": False}
}

response = requests.post(API_URL_SUBMIT, headers=headers, json=payload)
task_id = response.json()["output"]["task_id"]
print(f"Task ID: {task_id}")

# 2. 轮询结果
while True:
    time.sleep(2)
    query_resp = requests.get(API_URL_QUERY_BASE + task_id, headers=headers)
    status = query_resp.json()["output"]["task_status"]
    print(f"Status: {status}")
    if status in ["SUCCEEDED", "FAILED", "UNKNOWN"]:
        print(json.dumps(query_resp.json(), indent=2, ensure_ascii=False))
        break
```

更多语言 SDK 及详细参数请参考 [同步调用 API](./synchronous-api.md) 和 [异步调用 API](./asynchronous-api.md)。
