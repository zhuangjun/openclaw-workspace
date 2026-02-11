# Gemini Chat Skill

通过浏览器自动化控制 Gemini 进行高质量投资分析和深度对话。

## 快速开始

```bash
# 确保 Chrome Browser Relay 已开启（点击扩展图标，badge 显示 ON）

# 在代码中使用
from skills.gemini_chat import chat_with_gemini

# 单轮对话
answer = chat_with_gemini("什么是戴维斯双击？")

# 多轮对话
answer1 = chat_with_gemini("分析微软(MSFT)的最新财报")
answer2 = chat_with_gemini("基于刚才的分析，进行DCF估值", is_follow_up=True)
```

## 核心功能

- ✅ 自动切换到"思考"模式（投资分析必备）
- ✅ 支持单轮和多轮对话
- ✅ 智能识别对话状态（新对话 vs 旧对话）
- ✅ 自动提取和清理回答内容
- ✅ 完善的错误处理和重试机制

## 文档

详细文档请查看 [SKILL.md](./SKILL.md)

## 测试记录

- 2026-02-11: 初始版本测试通过
  - ✅ 戴维斯双击解释
  - ✅ 2026年美股市场分析
  - ✅ 微软财报深度分析
  - ✅ 微软DCF估值模型
  - ✅ 多轮对话模式保持

## 依赖

- OpenClaw Browser Relay（Chrome 扩展）
- Chrome 浏览器（仅用于 Gemini，一个 Tab）
- OpenClaw gateway 服务

## 注意事项

⚠️ **Chrome 使用原则**：永远只使用一个 Tab，不要打开其他网页

⚠️ **模式选择**：投资分析任务必须使用"思考"模式

⚠️ **数据真实性**：不编造数据，API 失败时必须向用户求助
