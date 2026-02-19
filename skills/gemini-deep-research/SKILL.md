---
name: gemini-deep-research
description: 使用 Gemini Deep Research 进行深度研究。当用户需要进行深度研究、投资分析、市场调查、竞品分析、行业趋势分析等需要多源信息综合分析的任务时使用。通过浏览器自动化控制 Gemini 网页版执行 Deep Research，包括导航到指定URL、创建新对话、启用思考模式、执行研究、获取结果的全流程。
---

# Gemini Deep Research

自动化执行 Gemini Deep Research 的完整流程。

## 使用场景

- 投资标的深度分析（股票、基金、加密货币）
- 行业趋势研究报告
- 竞品分析和市场调查
- 技术方案调研
- 任何需要多源信息综合分析的研究任务

## 前置条件

1. **Chrome 扩展状态**: 确保 OpenClaw Browser Relay 扩展显示 **"ON"**
2. **Gemini 订阅**: 用户需要已订阅 Gemini Advanced
3. **浏览器控制**: 优先使用 `profile="chrome"`，如失败则使用 `profile="openclaw"`

## 浏览器方案选择（重要）

### 方案优先级

| 优先级 | 方案 | Profile | 适用场景 |
|--------|------|---------|---------|
| 1 | Chrome Relay（优先） | `profile="chrome"` | 扩展显示 ON 且已连接 |
| 2 | Headless（备用） | `profile="openclaw"` | Chrome 扩展未连接或失败 |

### 自动检测逻辑

执行以下检测逻辑选择浏览器方案：

```
1. 尝试启动 Chrome Relay: browser start profile=chrome
2. 如果成功，使用 Chrome Relay 方案
3. 如果失败（扩展未连接），自动切换到 Headless: browser start profile=openclaw
4. Headless 方案已自动登录，可直接使用
```

### Chrome Relay 失败判断

以下情况视为 Chrome Relay 失败，需切换到 Headless：
- `browser start profile=chrome` 返回错误
- 提示 "no tab is connected"
- 提示 "Chrome extension relay is running, but no tab is connected"

## 标准执行流程

执行以下流程，优先使用 Chrome Relay，失败时自动切换到 Headless：

### 步骤 1: 启动浏览器（自动选择方案）

**优先尝试 Chrome Relay：**
```
browser start profile=chrome
```

**如果失败，自动切换到 Headless：**
```
browser start profile=openclaw
```

### 步骤 2: 获取标签页
```
browser tabs
```
获取 targetId

### 步骤 3: 导航到 Gemini
```
browser navigate targetId=<targetId> targetUrl=https://gemini.google.com/app
```

### 步骤 4: 发起新对话
点击"发起新对话"链接（ref=e43）
```
browser act targetId=<targetId> request={"kind":"click","ref":"e43","slowly":true}
```

### 步骤 5: 输入研究提示词
在输入框中输入用户的研究主题（ref=e117 或 ref=e213）
```
browser act targetId=<targetId> request={"kind":"type","ref":"e117","submit":false,"text":"用户的研究主题"}
```

### 步骤 6: 打开工具菜单
点击"工具"按钮（ref=e131 或 ref=e215）
```
browser act targetId=<targetId> request={"kind":"click","ref":"e131","slowly":true}
```

### 步骤 7: 选择 Deep Research
选择"Deep Research"选项（ref=e172）
```
browser act targetId=<targetId> request={"kind":"click","ref":"e172","slowly":true}
```

### 步骤 8: 验证思考模式
确认思考模式已启用（按钮显示"思考"）。如未启用：
- 点击推理模式选择器（ref=e142）
- 选择"思考"模式（ref=e2669）

### 步骤 9: 发送请求
点击发送按钮（ref=e162）
```
browser act targetId=<targetId> request={"kind":"click","ref":"e162","slowly":true}
```

### 步骤 10: 开始研究
点击"开始研究"按钮（ref=e346 或 ref=e415）
```
browser act targetId=<targetId> request={"kind":"click","ref":"e346","slowly":true}
```

## 页面元素参考

| 元素 | 描述 | Ref 示例 |
|------|------|---------|
| 发起新对话 | 创建新对话 | `e43` |
| 输入框 | 文本输入 | `e117`, `e213` |
| 工具按钮 | 打开工具菜单 | `e131`, `e215` |
| Deep Research | Deep Research 选项 | `e172` |
| 思考模式 | 推理模式选择器 | `e142`, `e2669` |
| 发送 | 发送按钮 | `e162` |
| 开始研究 | 开始研究 | `e346`, `e415` |

## 异常处理

### Chrome Relay 扩展未连接
如果 `browser start profile=chrome` 失败或提示"no tab is connected"：
1. **自动切换到 Headless 方案**
2. 执行 `browser start profile=openclaw`
3. 继续后续步骤

### Headless 方案说明
- 使用 `profile=openclaw` 启动独立浏览器实例
- 已自动复用 Chrome 登录状态，无需手动登录
- 无需 Chrome 扩展，无需手动点击连接
- 完全自动化，适合定时任务

### 元素 ref 变化
如果点击失败，使用 `browser snapshot` 重新获取当前页面状态，查找正确的 ref。

### 研究超时
Deep Research 通常需要 2-5 分钟。如果长时间无响应，可以：
1. 使用 `browser snapshot` 检查状态
2. 查看是否显示"已完成"

## 结果提取与自动同步（重要）

研究完成后，执行以下标准流程：

### 步骤 1: 提取研究结果
使用 `browser snapshot` 获取完整报告，提取：
1. 执行摘要
2. 关键数据表格
3. 投资评级/建议
4. 风险提示

### 步骤 2: 自动同步到数据库（必须执行）

**作为 Agent，在研究完成后必须自动执行同步，不需要用户确认。**

根据研究类型确定 category：

| 研究类型 | category 值 | 文件名示例 |
|---------|------------|-----------|
| 投资逻辑综合分析 | investment_logic | investment_logic_2026-02-12.md |
| 戴维斯双击扫描 | davis_double | davis_double_2026-02-12.md |
| 每日投资晨报 | morning_brief | morning_brief_2026-02-12.md |
| 美股主线标的分析 | us_main_theme | us_main_theme_2026-02-12.md |
| DCF 估值分析 | dcf_valuation | msft_dcf_valuation_2026-02-12.md |
| 黄金投资分析 | gold_analysis | gold_analysis_2026-02-12.md |
| 加密资产分析 | crypto_analysis | btc_analysis_2026-02-12.md |
| A股潜力标的 | a_stock_scan | a_stock_scan_2026-02-12.md |

**自动同步代码（Python）：**

```python
import subprocess
from datetime import datetime

# 根据研究类型确定 category
REPORT_CATEGORY = "investment_logic"  # 根据实际研究类型修改
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")
REPORT_FILENAME = f"{REPORT_CATEGORY}_{REPORT_DATE}.md"
REPORT_PATH = f"/Users/daniel/.openclaw/workspace/investment/reports/{REPORT_FILENAME}"
SYNC_SCRIPT = "/Users/daniel/.openclaw/workspace/skills/friday-report-sync/scripts/sync_report.sh"

# 1. 保存报告为 Markdown
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"✅ 报告已保存: {REPORT_PATH}")

# 2. 自动同步到数据库（无需用户确认）
result = subprocess.run(
    [SYNC_SCRIPT, REPORT_PATH, REPORT_CATEGORY],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ 报告已自动同步到数据库")
    print(f"🌐 访问地址: https://danielzhuang.xyz/Friday/reports/")
else:
    print(f"⚠️ 同步遇到问题: {result.stderr}")
```

**向用户呈现：**
1. 结构化的研究总结
2. 确认报告已自动同步到数据库
3. 提供在线访问链接

---

## 同步配置参考

### 环境变量

```bash
export FRIDAY_API_URL="https://danielzhuang.xyz/Friday/api"
export FRIDAY_API_TOKEN="dev-token-change-in-production"
```

### 手动同步命令（如需补传）

```bash
/Users/daniel/.openclaw/workspace/skills/friday-report-sync/scripts/sync_report.sh \
  ./report.md investment_logic "标题" 2026-02-12
```

## 示例提示词模板

### 戴维斯双击扫描（简化版）
```
寻找美股和港股中戴维斯双击的股票。
```
*Gemini Deep Research 会自动分析盈利增长和估值扩张的潜力标的。*

### 投资分析模板
```
请对 [股票代码] 进行全面的投资深度研究。分析维度包括：
1. 财务表现（近3年营收/净利润/毛利率趋势，最新财报数据）
2. 业务增长驱动（核心业务、增长引擎、市场份额）
3. 行业与市场（行业规模、竞争格局、政策环境）
4. 估值分析（当前PE/PB vs 历史分位，与可比公司对比，目标价测算）
5. 投资逻辑与风险（增长逻辑、主要风险、催化剂）
请提供结构化投资报告，包含执行摘要、详细分析、数据表格、风险提示和投资评级。
```

### 行业研究模板
```
请深度研究 [行业名称] 的市场趋势和发展前景。分析维度包括：
1. 市场规模和增长率（全球及中国市场）
2. 技术发展趋势和突破
3. 政策环境和监管变化
4. 主要参与者及竞争格局
5. 产业链分析（上游原材料、中游制造、下游应用）
6. 消费者偏好和需求变化
7. 投资机会和风险
请提供结构化的行业研究报告。
```

## 参见

- 详细工作流指南: [references/workflow-guide.md](references/workflow-guide.md)
- Headless 方案文档: [docs/openclaw-browser-fix.md](../docs/openclaw-browser-fix.md)
