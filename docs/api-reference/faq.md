# 常见问题 (FAQ)

## Q: 如何为 API 提供公网可访问的音频 URL？

推荐使用 [阿里云对象存储 OSS](https://www.aliyun.com/product/oss)。
您可以将音频文件上传到 OSS，并生成带有签名的临时 URL（用于私有 Bucket）或直接使用公开 URL（用于公共 Bucket）。

**验证方法**: 在浏览器中直接访问生成的 URL，如果能下载或播放音频，说明 URL 有效。

## Q: 如何检查音频格式是否符合要求？

推荐使用开源工具 `ffprobe` (FFmpeg 的一部分)：

```bash
ffprobe -v error -show_entries format=format_name -show_entries stream=codec_name,sample_rate,channels -of default=noprint_wrappers=1 input.mp3
```

## Q: 如何处理音频以满足模型要求？

使用 `ffmpeg` 进行转换。

**1. 裁剪音频 (用于测试或切片)**
```bash
# 从 01:30 开始截取 2 分钟
ffmpeg -i input.wav -ss 00:01:30 -t 00:02:00 -c copy output_clip.wav
```

**2. 格式转换 (转为 16kHz 单声道 WAV)**
```bash
ffmpeg -i input.mp3 -ac 1 -ar 16000 -sample_fmt s16 output.wav
```

## Q: 支持哪些音频格式？

- **通用**: `mp3`, `wav`, `m4a`, `aac`, `flac`, `ogg`, `opus`, `amr`, `wma` 等。
- **注意**: 尽量使用常见编码格式，避免使用加密或损坏的音频文件。

## Q: 错误码 `FILE_403_FORBIDDEN` 是什么意思？

通常表示提供的音频 `file_url` 无法访问。请检查：
1.  URL 是否过期。
2.  URL 是否有访问权限限制（如防盗链、私有权限）。
3.  服务器是否能够访问该 URL（部分内网 URL 无法被云端服务访问）。
