# Git 开源配置指南

## 推荐方案：创建独立仓库

### Step 1: 在 GitHub 创建新仓库

仓庛建议命名（任选其一）：
- `qwen3-asr-desktop`
- `qwen3-asr-gui`
- `qwen3-asr-toolkit-pro`
- `Qwen3-ASR-Desktop-Edition`

**关键设置**：
- [x] 设为 Public 公开仓库
- [ ] 不要添加 .gitignore（项目已有）
- [ ] 不要添加 License（项目已有）

---

### Step 2: 配置本地仓库

```bash
# 1. 重命名远程仓库（保留原项目作为 upstream 引用）
git remote rename origin upstream

# 2. 添加新的 origin（替换为你的新仓库地址）
git remote add origin https://github.com/LINSUISHENG034/qwen3-asr-desktop.git

# 3. 推送到新仓库
git push -u origin main

# 4. 验证远程配置
git remote -v
# 应该看到：
# upstream    https://github.com/QwenLM/Qwen3-ASR-Toolkit.git (fetch)
# upstream    https://github.com/QwenLM/Qwen3-ASR-Toolkit.git (push)
# origin      https://github.com/LINSUISHENG034/qwen3-asr-desktop.git (fetch)
# origin      https://github.com/LINSUISHENG034/qwen3-asr-desktop.git (push)
```

---

### Step 3: 同步上游更新（定期执行）

```bash
# 方法一：直接合并（推荐）
git fetch upstream
git merge upstream/main

# 方法二：变基（保持历史清晰）
git fetch upstream
git rebase upstream/main

# 推送更新到你的仓库
git push origin main
```

**建议设置别名简化操作**：
```bash
git config --global alias.sync '!f() { git fetch upstream && git merge upstream/main; }; f'
# 之后只需运行：git sync
```

---

### Step 4: 更新 .gitignore（可选）

确保不会推送敏感文件：

```gitignore
# .gitignore
.asr_env
*.pyc
__pycache__/
.venv/
build/
dist/
*.egg-info/
.bmad-output/
```

---

## GitHub 项目设置

### Repository Topics（标签）
在 GitHub Settings → Topics 中添加：
```
asr, speech-recognition, qwen, pyqt6, gui, desktop-app, chinese, audio-processing, subtitle-generator, batch-processing
```

### Repository Description（简介）
```
Modern PyQt6 desktop GUI for Qwen3-ASR with batch transcription support
```

### Website 链接
指向你的文档或演示视频（如有）

---

## License 说明

原项目使用 MIT License，你的项目也保持 MIT：

1. 保留原 `LICENSE` 文件
2. 在 README 中明确说明基于原项目
3. 你的新增代码同样 MIT 授权

---

## PyPI 发布（可选）

如果想作为独立包发布：

```bash
# 1. 修改 setup.py 中的包名
# 从: qwen3-asr-toolkit
# 到: qwen3-asr-desktop

# 2. 构建
python -m build

# 3. 发布（需要 PyPI 账号）
twine upload dist/*
```
