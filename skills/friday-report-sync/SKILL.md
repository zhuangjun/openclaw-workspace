---
name: friday-report-sync
description: 将投资研究报告同步到生产服务器数据库（https://danielzhuang.xyz/Friday/reports/）。用于所有Deep Research任务（股市晨报、投资逻辑分析、美股主线分析、戴维斯双击扫描等）生成报告后同步到线上。当需要将HTML/Markdown报告发布到网站时使用此skill。
---

# Friday Report Sync v2.0

将投资研究报告同步到生产服务器数据库，使其可通过网站访问。

## 使用场景

- **股市综合晨报**生成后同步
- **投资逻辑分析报告**生成后同步
- **美股主线标的分析**生成后同步
- **戴维斯双击扫描报告**生成后同步
- **DCF估值分析**生成后同步
- 任何需要发布到网站的Deep Research报告

## 快速使用

### 同步单个报告文件（推荐）
```bash
# 基本用法 - 自动检测类别和日期
/Users/daniel/.openclaw/workspace/skills/friday-report-sync/scripts/sync_report.sh /path/to/report.md

# 指定类别
/Users/daniel/.openclaw/workspace/skills/friday-report-sync/scripts/sync_report.sh /path/to/report.md investment_logic

# 完整参数
/Users/daniel/.openclaw/workspace/skills/friday-report-sync/scripts/sync_report.sh /path/to/report.md davis_double "戴维斯双击扫描" 2026-02-12
```

### 支持的报告类别

| 类别ID | 说明 | 关键词自动检测 |
|--------|------|----------------|
| investment_logic | 投资逻辑分析 | investment_logic |
| davis_double | 戴维斯双击扫描 | davis_double |
| morning_brief | 每日投资晨报 | morning, brief |
| us_main_theme | 美股主线分析 | main_theme, us_stock |
| dcf_valuation | DCF估值分析 | dcf, valuation |
| gold_analysis | 黄金投资分析 | gold |
| crypto_analysis | 加密资产分析 | crypto, bitcoin |
| a_stock_scan | A股潜力标的 | a_stock |
| general | 通用报告 | 其他 |

## 工作流程

1. **准备报告**
   - 确保报告文件是 Markdown 格式 (.md)
   - 文件名建议包含日期 (YYYY-MM-DD)

2. **执行同步脚本**
   - 脚本会自动检测类别（从文件名关键词）
   - 自动提取日期（从文件名）
   - 自动提取标题（从文件第一行或文件名）
   - 调用 API 保存到数据库

3. **验证访问**
   - 访问 https://danielzhuang.xyz/Friday/reports/
   - 确认报告正常显示

## 在 Deep Research 中使用

研究完成后，保存报告并同步：

```python
# 1. 保存报告到本地
report_path = "/Users/daniel/.openclaw/workspace/investment/reports/investment_logic_2026-02-12.md"
with open(report_path, 'w') as f:
    f.write(report_content)

# 2. 同步到数据库
import subprocess
subprocess.run([
    "/Users/daniel/.openclaw/workspace/skills/friday-report-sync/scripts/sync_report.sh",
    report_path,
    "investment_logic"  # 指定类别
], check=True)
```

## 配置

- **远程服务器**: ubuntu@43.134.37.253
- **API 地址**: https://danielzhuang.xyz/Friday/api
- **访问地址**: https://danielzhuang.xyz/Friday/reports/
- **数据库**: ~/friday/friday.db (SQLite)

### 环境变量（可选）

```bash
export FRIDAY_API_URL="https://danielzhuang.xyz/Friday/api"
export FRIDAY_API_TOKEN="your-token"
export FRIDAY_REPORTS_DIR="/Users/daniel/.openclaw/workspace/investment/reports"
```

## API 端点

| 端点 | 说明 |
|------|------|
| GET /Friday/api/reports | 获取报告列表（支持分页筛选） |
| GET /Friday/api/reports/:id | 获取单个报告详情 |
| POST /Friday/api/reports | 创建/更新报告（需鉴权） |
| GET /Friday/api/reports/categories | 获取分类列表 |
| GET /Friday/api/reports/stats | 获取统计数据 |

## 错误处理

- 如果同步失败，脚本会返回非零退出码
- 检查网络连接和 API 可访问性
- 验证远程服务器可访问性

## 技术架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  本地 Markdown  │────▶│   sync_report   │────▶│  Friday API     │
│  报告文件       │     │   同步脚本      │     │  (Flask/SQLite) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                    ┌────────────────────┘
                                    ▼
                           ┌─────────────────┐
                           │  数据库          │
                           │  friday.db      │
                           └─────────────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │  Web 前端        │
                           │  index.html     │
                           └─────────────────┘
```

## 更新日志

### v2.0 (2026-02-12)
- ✅ 从文件同步改为数据库存储
- ✅ API 驱动的架构
- ✅ 自动类别检测
- ✅ 支持报告更新（重复同步自动更新）
- ✅ 前端支持分页和筛选

### v1.0 (旧版)
- 基于 rsync 的文件同步
- 静态 HTML 索引页面
