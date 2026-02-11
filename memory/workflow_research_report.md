# 研究报告生成工作流程

## 标准流程（当用户要求生成研究报告时）

### 1. 研究阶段
- **工具**: Gemini Deep Research
- **输入**: 用户提供的研究主题/问题
- **深度**: 全面研究，检索权威来源（Bloomberg、FactSet、公司财报等）

### 2. 报告生成
- **整理**: 基于 Deep Research 结果，生成结构化报告
- **格式**: Markdown（本地保存）+ HTML（网页展示）
- **内容结构**:
  - 执行摘要（核心结论）
  - 详细分析（分章节）
  - 数据表格
  - 投资建议
  - 风险提示

### 3. 输出交付
- **Telegram**: 发送精简版报告（核心结论、关键数据）
- **生产服务器**: 自动同步到 https://danielzhuang.xyz/Friday/reports/
- **本地存档**: 保存到 `/Users/daniel/.openclaw/workspace/investment/reports/`

### 4. 文件命名规范
```
{报告类型}_{YYYY-MM-DD}.md

示例:
- investment_logic_2026-02-11.md
- davis_double_play_2026-02-11.md
- msft_dcf_valuation_2026-02-11.md
```

### 5. 报告类型
- **investment_logic**: 投资逻辑分析
- **davis_double_play**: 戴维斯双击扫描
- **market_morning_report**: 股市综合晨报
- **us_stock_main_theme**: 美股主线分析
- **{股票代码}_dcf_valuation**: 个股DCF估值

### 6. 自动化
- 生成报告后自动执行 `sync_reports_to_prod.sh`
- 自动更新索引页面（支持筛选）
- 自动生成 HTML 渲染版本

---

**记忆时间**: 2026-02-11
**优先级**: 高
**适用范围**: 所有投资研究报告生成任务
