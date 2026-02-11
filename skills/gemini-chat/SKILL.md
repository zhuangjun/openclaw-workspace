# SKILL.md - Gemini Chat via Browser Automation

通过浏览器自动化控制 Gemini 进行高质量投资分析和深度对话。

## 重要原则

### Chrome 使用原则
**永远只使用一个 Tab**，专门用于 Gemini 任务（Browser Relay ON）

### 模式选择
**投资分析任务必须使用"思考"模式！**

---

## 前置要求

### 1. Chrome Browser Relay 设置
```bash
# 在 Chrome 浏览器中安装 OpenClaw Browser Relay 扩展
# 点击扩展图标，确保 badge 显示为 ON
```

### 2. 浏览器控制服务检查
```bash
# 检查服务状态
openclaw gateway status

# 如需重启
openclaw gateway restart
```

---

## 核心流程

### 单轮对话流程（标准）

```python
def chat_with_gemini(question, is_new_chat=False):
    """
    使用 Gemini 进行单轮对话
    """
    # 1. 获取并聚焦 Gemini tab
    tabs = browser.tabs(profile="chrome")
    gemini_tab = next((t for t in tabs if "gemini.google.com" in t.get("url", "")), None)
    
    if not gemini_tab:
        result = browser.open(targetUrl="https://gemini.google.com/", profile="chrome")
        gemini_tab_id = result["targetId"]
    else:
        gemini_tab_id = gemini_tab["targetId"]
    
    browser.focus(targetId=gemini_tab_id)
    
    # 2. 检查并切换模式（仅新对话需要）
    if is_new_chat:
        snapshot = browser.snapshot(refs="aria")
        if "用户问候语" in str(snapshot) or "需要我为你做些什么" in str(snapshot):
            # 切换到"思考"模式
            browser.act(request={"kind": "click", "ref": "e141"})
            time.sleep(0.5)
            browser.act(request={"kind": "click", "ref": "e174"})
            time.sleep(0.5)
    
    # 3. 输入并发送问题
    browser.act(request={"kind": "type", "ref": "e117", "text": question})
    browser.act(request={"kind": "click", "ref": "e188"})
    
    # 4. 等待并提取回答
    time.sleep(5)  # 根据问题复杂度调整
    final_snapshot = browser.snapshot(refs="aria")
    
    return extract_gemini_answer(final_snapshot)
```

### 多轮对话流程

```python
# 同一对话中继续提问，无需切换模式
browser.act(request={"kind": "type", "ref": "e117", "text": follow_up_question})
browser.act(request={"kind": "click", "ref": "e188"})
time.sleep(5)
answer = extract_gemini_answer(browser.snapshot(refs="aria"))
```

### 发起新对话

```python
# 点击"发起新对话"按钮
browser.act(request={"kind": "click", "ref": "e43"})
time.sleep(2)

# 注意：新对话会回到"快速"模式，需要重新切换到"思考"
```

---

## 关键 Ref 识别

| 元素 | 典型 ref | 说明 |
|------|---------|------|
| 模式选择器 | e141 | "快速/思考/Pro" 下拉按钮 |
| "思考"选项 | e174 | 模式选择菜单中的"思考" |
| 输入框 | e117 | 文本输入框 |
| 发送按钮 | e188 | 发送/停止回答按钮 |
| 发起新对话 | e43 | 左上角新建对话按钮 |

**注意**：Ref 可能随页面更新而变化，每次操作前建议重新 snapshot。

---

## 等待时间建议

| 问题类型 | 等待时间 | 说明 |
|---------|---------|------|
| 简单问答 | 3-5 秒 | 如"什么是戴维斯双击" |
| 中等复杂 | 5-8 秒 | 如"分析某公司财报" |
| 深度分析 | 8-15 秒 | 如"进行DCF估值" |
| 极复杂任务 | 15-30 秒 | 如"深度研究报告" |

---

## 常见问题处理

### 1. 429 错误（Gemini 限流）
**原因**：Gemini 每天的使用额度有限制，可能被限流。

**解决方案**：
- 晚些再使用（避开高峰期）
- 等待额度重置后再继续
- 使用备用方案（web_search、web_fetch 等）

### 2. "Can't reach the OpenClaw browser control service"
```bash
# 重启 gateway 服务
openclaw gateway restart
```

### 3. "tab not found" 错误
```python
# 重新获取 tabs 列表
tabs = browser.tabs(profile="chrome")
```

### 4. "Validation failed for tool" 错误
- 检查 ref 是否正确（需要最新的 snapshot）
- 确保请求格式正确

### 5. 模式自动切换回"快速"
- 只有发起新对话时才会发生
- 在同一对话中，模式会保持

---

## 提取 Gemini 回答

```python
def extract_gemini_answer(snapshot_text):
    """
    从 snapshot 中提取 Gemini 的回答
    """
    import re
    
    # 查找 "Gemini said" 之后的内容
    pattern = r'Gemini said.*?(?=generic.*?button.*?答得好|$)'
    matches = re.findall(pattern, snapshot_text, re.DOTALL)
    
    if matches:
        answer = matches[0]
        # 清理 HTML 标签和多余内容
        answer = re.sub(r'<.*?>', '', answer)
        answer = re.sub(r'\[.*?\]', '', answer)
        return answer.strip()
    
    return None
```

---

## 最佳实践

### 1. 批量处理相关问题
在同一对话中多轮提问，避免频繁发起新对话

### 2. 合理设置等待时间
根据问题复杂度调整等待时间，避免过早截取

### 3. 错误重试
```python
def safe_gemini_chat(question, max_retries=3):
    for attempt in range(max_retries):
        try:
            return chat_with_gemini(question)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2)
```

### 4. 速率控制
避免短时间内发送过多请求，以免触发限流

---

## 维护日志

- 2026-02-11: 初始版本，完成基础流程测试
- 测试通过：戴维斯双击解释、美股市场分析、微软财报分析、DCF估值
- 发现：新对话需手动切换"思考"模式，旧对话保持模式
