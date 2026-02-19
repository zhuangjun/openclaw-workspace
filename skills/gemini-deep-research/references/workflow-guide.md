# Gemini Deep Research 工作流详细指南

## 完整执行流程（逐步详解）

### 阶段 1: 准备和连接（自动选择浏览器方案）

#### 1.1 启动浏览器控制（优先 Chrome Relay，失败自动切换 Headless）

**第一步：尝试 Chrome Relay（优先方案）**
```bash
browser start profile=chrome
```

**成功响应示例：**
```json
{
  "enabled": true,
  "profile": "chrome",
  "running": true,
  "cdpReady": true,
  "cdpHttp": true,
  "cdpPort": 18792
}
```

**失败时自动切换到 Headless（备用方案）：**
```bash
browser start profile=openclaw
```

**失败判断条件：**
- 返回错误 "no tab is connected"
- 返回错误 "Chrome extension relay is running, but no tab is connected"
- 任何其他启动失败

**自动切换逻辑：**
```
if chrome_start_failed:
    browser start profile=openclaw
    continue_workflow()
```

**Headless 方案特点：**
- 无需 Chrome 扩展
- 无需手动点击连接
- 已自动登录（复用 Chrome 登录状态）
- 适合定时任务自动化

#### 1.2 获取标签页列表
```bash
browser tabs
```

**响应示例：**
```json
{
  "tabs": [
    {
      "targetId": "C2BFBDDFE4D9303ED8D369CC6E3DEC03",
      "title": "Google Gemini",
      "url": "https://gemini.google.com/app",
      "type": "page"
    }
  ]
}
```

记录 `targetId` 供后续使用。

#### 1.3 导航到 Gemini
```bash
browser navigate targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03 targetUrl=https://gemini.google.com/app
```

**注意：** URL 应该是 `https://gemini.google.com/app` 而不是 `https://gemini.google.com/app/`

### 阶段 2: 创建对话

#### 2.1 点击"发起新对话"
使用 `browser snapshot` 获取当前页面状态，找到"发起新对话"元素的 ref。

```bash
browser snapshot targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03
```

查找包含 "发起新对话" 的元素，通常是 `ref=e43`。

```bash
browser act targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03 request={"kind":"click","ref":"e43","slowly":true}
```

#### 2.2 验证新对话页面
再次使用 `browser snapshot` 确认页面已切换到新对话界面，应看到：
- "用户问候语"
- "需要我为你做些什么？"
- 空的输入框

### 阶段 3: 配置研究

#### 3.1 输入研究主题
找到输入框元素（通常是 `ref=e117` 或 `ref=e213`）：

```bash
browser act targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03 request={"kind":"type","ref":"e117","submit":false,"text":"用户的研究主题"}
```

**提示词建议：**
- 具体明确的研究主题
- 包含关键分析维度
- 指定输出格式要求

#### 3.2 启用 Deep Research
1. 点击"工具"按钮（`ref=e131` 或 `ref=e215`）
2. 点击"Deep Research"选项（`ref=e172`）

```bash
browser act targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03 request={"kind":"click","ref":"e131","slowly":true}
```

```bash
browser act targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03 request={"kind":"click","ref":"e172","slowly":true}
```

**验证：** Deep Research 启用后，输入框下方应显示"取消选择'Deep Research'"按钮。

#### 3.3 确认思考模式
检查推理模式选择器按钮：
- 如果显示"思考"，则已正确配置
- 如果显示"快速"，需要切换：
  1. 点击选择器（`ref=e142`）
  2. 选择"思考"模式（`ref=e2669`）

### 阶段 4: 执行研究

#### 4.1 发送请求
点击发送按钮（`ref=e162`）：

```bash
browser act targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03 request={"kind":"click","ref":"e162","slowly":true}
```

#### 4.2 获取研究方案
Gemini 会返回一个研究方案，包含：
- 研究标题
- 研究步骤（通常 7-8 步）
- "修改方案"和"开始研究"按钮

#### 4.3 开始研究
点击"开始研究"按钮（`ref=e346` 或 `ref=e415`）：

```bash
browser act targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03 request={"kind":"click","ref":"e346","slowly":true}
```

### 阶段 5: 等待和获取结果

#### 5.1 监控研究进度
研究通常需要 2-5 分钟。使用 `browser snapshot` 检查状态：

```bash
browser snapshot targetId=C2BFBDDFE4D9303ED8D369CC6E3DEC03
```

**进行中特征：**
- 显示"停止回答"按钮
- 显示"正在研究 X 个网站..."
- 有研究进度面板

**完成特征：**
- 显示完整报告内容
- 有"报告中使用的来源"部分
- 显示"已完成"状态

#### 5.2 提取关键信息
从完成的报告中提取：
1. **执行摘要** - 核心结论
2. **关键数据** - 表格中的数字
3. **投资评级** - 买入/持有/卖出建议
4. **目标价** - 价格区间
5. **风险提示** - 主要风险因素

### 阶段 6: 结果呈现

向用户呈现结构化的研究总结，包括：
- 研究主题和完成时间
- 核心发现（3-5 点）
- 关键数据表格
- 投资建议
- 风险提示

### 阶段 7: 数据同步到数据库（重要）

将研究报告同步到 Friday 数据库，以便在 Reports 页面展示。

#### 7.1 确定报告类别

根据研究主题确定 category：

| 研究类型 | category 值 |
|---------|------------|
| 投资逻辑综合分析 | `investment_logic` |
| 戴维斯双击扫描 | `davis_double` |
| 每日投资晨报 | `morning_brief` |
| 美股主线标的分析 | `us_main_theme` |
| DCF 估值分析 | `dcf_valuation` |
| 黄金投资分析 | `gold_analysis` |
| 加密资产分析 | `crypto_analysis` |
| A股潜力标的 | `a_stock_scan` |

#### 7.2 创建 Markdown 文件

创建精简版报告文件，包含：
- 标题和日期
- 执行摘要
- 核心分析内容（去除过长的详细数据）
- 投资建议和风险提示

文件名格式：`{category}_{YYYYMMDD}.md`

示例：`investment_logic_2026-02-12.md`

#### 7.3 执行同步脚本

```bash
# 基本用法
./sync_report_api.sh <报告文件.md> <category> [标题] [日期]

# 示例
./sync_report_api.sh ./investment_logic_2026-02-12.md investment_logic "投资逻辑分析" 2026-02-12
```

脚本会自动：
1. 检测报告元数据（如未指定标题/日期）
2. 生成摘要
3. 调用 API 同步到数据库
4. 返回同步结果

#### 7.4 验证同步

确认同步成功：
- 检查脚本的输出，应显示 `✅ 报告已创建` 或 `✅ 报告已更新`
- 获取返回的报告 ID
- 可在浏览器中访问 https://danielzhuang.xyz/Friday/reports/ 查看

#### 7.5 错误处理

如果同步失败：
1. 检查 API_TOKEN 是否正确设置
2. 检查网络连接
3. 使用 `--verbose` 查看详细错误信息
4. 如需重试，使用相同命令（会根据标题+日期去重）

## 常见问题排查

### Q: 元素 ref 找不到或点击失败
**A:** 页面结构可能变化。使用 `browser snapshot` 重新扫描页面，查找包含目标文本的元素的新 ref。

### Q: Deep Research 选项不可用
**A:** 确认用户已订阅 Gemini Advanced。免费版不支持 Deep Research。

### Q: 研究长时间未完成
**A:** 
1. 检查网络连接
2. 使用 `browser snapshot` 确认状态
3. 如卡死，点击"停止回答"后重新开始

### Q: 扩展连接中断
**A:** 
1. 提示用户检查扩展状态
2. 如显示"OFF"，让用户点击扩展图标重新连接
3. 重新执行 `browser start`

## 最佳实践

1. **提示词质量** - 提示词越具体，研究结果越好
2. **等待耐心** - Deep Research 需要时间，不要频繁检查
3. **错误恢复** - 任何步骤失败都应优雅地通知用户
4. **结果验证** - 研究报告可能包含过时信息，提醒用户验证关键数据
