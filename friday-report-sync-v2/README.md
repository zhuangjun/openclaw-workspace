# Friday Report Sync v2.0 - API驱动
# 投资报告同步到生产环境数据库

## 使用方法

### 基本用法

```bash
# 同步单个报告
./sync_report_api.sh <报告文件.md> [类型] [标题] [日期]

# 示例
./sync_report_api.sh ./investment_logic_2026-02-12.md investment_logic
./sync_report_api.sh ./davis_double_2026-02-12.md davis_double "戴维斯双击扫描"
```

### 自动检测

脚本会自动检测以下信息：
- **类别**: 从文件名关键词识别 (investment_logic, davis_double, morning_brief, dcf_valuation, etc.)
- **日期**: 从文件名提取 (YYYY-MM-DD 或 YYYYMMDD)，默认为今天
- **标题**: 从文件第一行 Markdown 标题提取

### 环境变量

```bash
export FRIDAY_API_URL="https://danielzhuang.xyz/api"
export FRIDAY_API_TOKEN="your-secret-token"
export FRIDAY_REPORTS_DIR="/path/to/reports"
```

### 命令行选项

| 选项 | 说明 |
|------|------|
| `-h, --help` | 显示帮助 |
| `-d, --dry-run` | 试运行，不实际提交 |
| `-v, --verbose` | 详细输出 |

## API 端点

### POST /api/reports
创建/更新报告

**Headers:**
- Content-Type: application/json
- Authorization: Bearer {token}

**Body:**
```json
{
  "title": "报告标题",
  "category": "investment_logic",
  "report_date": "2026-02-12",
  "content_md": "# Markdown内容...",
  "summary": "摘要",
  "source": "gemini-deep-research",
  "author": "Friday AI"
}
```

## 报告分类

| 分类ID | 说明 |
|--------|------|
| investment_logic | 投资逻辑分析 |
| davis_double | 戴维斯双击扫描 |
| morning_brief | 每日投资晨报 |
| us_main_theme | 美股主线标的分析 |
| dcf_valuation | DCF估值分析 |
| crypto_analysis | 加密资产分析 |
| gold_analysis | 黄金投资分析 |
| a_stock_scan | A股潜力标的 |

## 技术说明

此版本 (v2.0) 使用 API 调用替代了原来的 rsync 文件同步方式：
- 报告内容存储在 SQLite 数据库中
- 前端页面从 API 获取数据
- 支持分页、筛选和全文搜索
