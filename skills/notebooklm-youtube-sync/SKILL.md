---
name: notebooklm-youtube-sync
description: Monitor YouTube channels for new videos and automatically add them to NotebookLM notebooks. Use when the user wants to (1) Track updates from specific YouTube channels, (2) Automatically add YouTube video URLs to NotebookLM for note-taking/analysis, (3) Set up automated workflows between YouTube and NotebookLM, or (4) Sync video content from creators to their NotebookLM research notebooks.
---

# NotebookLM YouTube Sync

自动化监控 YouTube 频道并将新视频添加到 NotebookLM。

## 前置要求

1. **yt-dlp** 已安装 (用于获取 YouTube 视频信息)
2. **Chrome 浏览器** 已连接 OpenClaw Browser Relay
3. **NotebookLM** 账号已登录

## 核心功能

### 1. 检查频道更新

```bash
python3 /Users/daniel/.openclaw/workspace/skills/notebooklm-youtube-sync/scripts/check_youtube_channel.py <channel_identifier>
```

支持的频道标识格式：
- 完整 URL: `https://www.youtube.com/@MrBeast`
- Handle: `@MrBeast`
- Channel ID: `UC...`
- 纯用户名: `MrBeast`

输出示例：
```json
{
  "channel": "@MrBeast",
  "checked_at": "2026-02-12T19:30:00",
  "new_videos": [
    {
      "id": "abc123",
      "title": "Video Title",
      "upload_date": "20260212",
      "url": "https://www.youtube.com/watch?v=abc123"
    }
  ],
  "total_seen": 150
}
```

### 2. 添加视频到 NotebookLM

NotebookLM 没有公开 API，需要通过浏览器自动化操作：

**步骤：**
1. 导航到 NotebookLM 笔记本 URL:
   `https://notebooklm.google.com/notebook/{notebook_id}`

2. 点击 **"+"** 按钮或 **"Add Source"**

3. 选择 **"YouTube"** 选项

4. 粘贴视频 URL

5. 等待处理完成

## 完整工作流示例

### 单次检查并添加

```bash
# 1. 检查频道更新
python3 scripts/check_youtube_channel.py @ChannelName

# 2. 如果有新视频，使用浏览器添加到 NotebookLM
# (通过 browser action 手动执行)
```

### 设置定时监控 (Cron)

```bash
# 每 6 小时检查一次并自动添加到指定笔记本
openclaw cron add --schedule "every 6 hours" \
  --command "check-and-sync-youtube --channel @ChannelName --notebook <notebook_id>"
```

## 多频道管理

创建配置文件管理多个频道：

```json
{
  "notebooks": {
    "investment-research": "abc123xyz",
    "tech-learning": "def456uvw"
  },
  "channels": [
    {
      "name": "@Channel1",
      "notebook": "investment-research",
      "last_check": null
    },
    {
      "name": "@Channel2", 
      "notebook": "tech-learning",
      "last_check": null
    }
  ]
}
```

## 状态文件

脚本会自动维护状态文件，记录已处理的视频：
- 位置: `data/state.json`
- 内容: 上次检查时间 + 已见视频 ID 列表

## 限制说明

1. **NotebookLM API**: 无公开 API，必须通过浏览器自动化
2. **YouTube 限制**: yt-dlp 可能偶尔受速率限制
3. **视频年龄**: 默认只检查最近 7 天的视频

## 故障排除

### yt-dlp 未找到
```bash
pip3 install --user yt-dlp
```

### 频道无法识别
尝试使用完整 URL 而非 handle:
```bash
python3 scripts/check_youtube_channel.py "https://www.youtube.com/@ChannelName"
```

### NotebookLM 添加失败
1. 确认已登录 NotebookLM
2. 检查 notebook_id 是否正确
3. 确认 Browser Relay 连接正常
