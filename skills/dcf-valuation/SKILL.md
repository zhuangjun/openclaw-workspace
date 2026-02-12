---
name: dcf-valuation
description: DCF 贴现现金流估值模型工具，支持绝对估值计算、敏感性分析、交互模式和JSON输出
metadata:
  {
    "openclaw":
      {
        "emoji": "💰",
        "requires": { "bins": ["python3"] },
        "install": [],
      },
  }
---

# DCF 估值模型工具

基于贴现现金流（Discounted Cash Flow）的绝对估值方法，计算企业内在价值和每股公允价格。

## Features

- **两阶段模型**: 显性预测期 + 永续增长期
- **敏感性分析**: 不同 WACC 和永续增长率下的估值矩阵
- **交互模式**: 引导式参数输入
- **JSON 输出**: 程序化调用和结果保存
- **上涨空间**: 对比当前价格给出投资建议

## 核心公式

### 企业价值 (Enterprise Value)
```
EV = Σ FCF_t / (1+WACC)^t + TV / (1+WACC)^n
```

### 终值 (Terminal Value) - Gordon Growth Model
```
TV = FCF_n × (1+g) / (WACC - g)
```

### 股权价值
```
每股价值 = (EV - 净债务) / 总股本
```

## Usage

### 交互模式（推荐）
```bash
dcf-valuation --interactive
```

### 命令行参数
```bash
dcf-valuation \
  --fcf 65000 \
  --growth-5y 0.12 \
  --growth-terminal 0.025 \
  --wacc 0.09 \
  --shares 7430 \
  --current-price 415
```

### JSON 输入
```bash
dcf-valuation --json '{
  "current_fcf": 65000,
  "growth_rate_5y": 0.12,
  "growth_rate_terminal": 0.025,
  "discount_rate": 0.09,
  "shares_outstanding": 7430,
  "net_debt": 0
}'
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--fcf` | 当前年度自由现金流 (百万美元) | 65000 |
| `--growth-5y` | 前5年增长率 | 0.12 (12%) |
| `--growth-terminal` | 永续增长率 | 0.025 (2.5%) |
| `--wacc` | 折现率/WACC | 0.09 (9%) |
| `--shares` | 总股本 (百万股) | 7430 |
| `--net-debt` | 净债务 (百万美元) | 0 |
| `--current-price` | 当前股价 | 415 |

## 参数获取指南

### 自由现金流 (FCF)
```
FCF = 经营活动现金流 - 资本支出
```
- 查看现金流量表 (Cash Flow Statement)
- 或使用: FCF = 净利润 + 折旧摊销 - 资本支出 - 营运资本变动

### WACC 估算
| 因素 | 取值参考 |
|------|----------|
| 无风险利率 | 10年期美债收益率 (~4-5%) |
| 市场风险溢价 | 4-6% |
| Beta | 股票波动性指标 |
| 债务成本 | 公司债券收益率 |
| 税率 | 公司实际税率 |

### 增长率假设
- **前5年增长**: 基于历史增长和行业前景
  - 成熟期公司: 5-10%
  - 成长型公司: 15-25%
  - 科技/高增长: 20-30%
- **永续增长**: 通常取 GDP 长期增长率 (2-3%)

## 输出示例

```
============================================================
📊 DCF 估值分析报告
============================================================

【输入假设】
  当前自由现金流: $65.00B
  前5年增长率: 12.0%
  永续增长率: 2.5%
  折现率 (WACC): 9.0%
  总股本: 7430.00 百万股

【估值结果】
  企业价值 (EV): $1.53T
  每股内在价值: $205.50
  当前价格: $415.00
  上涨空间: -50.5%
  📉 估值结论: 高估

【敏感性分析 - 每股价值 (WACC vs 永续增长率)】
G\WACC    7.0%          8.0%          9.0%          10.0%         11.0%
----------------------------------------------------------------------
1.5%      $253.13       $212.70       $183.10       $160.50       $142.69
2.5%      $300.65       $244.40       $205.50       $177.02       $155.27
3.5%      $375.33       $290.19       $236.05       $198.62       $171.20
```

## 使用场景

### 1. 个股估值
```bash
dcf-valuation --interactive
# 输入: MSFT 财务数据
# 判断当前价格是否合理
```

### 2. 对比分析
```bash
# 悲观情景
dcf-valuation --growth-5y 0.08 --wacc 0.10

# 乐观情景  
dcf-valuation --growth-5y 0.18 --wacc 0.08
```

### 3. 程序化调用
```bash
# 保存JSON结果供进一步分析
dcf-valuation --json '{...}' --save msft_valuation.json
cat msft_valuation.json | jq '.value_per_share'
```

## 局限性与注意事项

⚠️ **重要提醒**

1. **Garbage In, Garbage Out**: DCF 结果高度依赖输入假设
2. **增长率敏感性**: 永续增长率假设对终值影响巨大
3. **WACC 估算**: 折现率的微小变化会导致估值大幅波动
4. **非经营性资产**: 本模型假设公司仅进行经营性活动
5. **周期性行业**: 对强周期行业的估值需要特别谨慎

## 最佳实践

1. **多情景分析**: 同时使用悲观/中性/乐观三种假设
2. **横向对比**: 与同业公司的估值倍数交叉验证
3. **安全边际**: DCF 给出的是"公允价值"，建议保留 20-30% 安全边际
4. **定期更新**: 每季度根据最新财报更新假设

## Installation

```bash
ln -sf ~/.openclaw/skills/dcf-valuation/dcf-valuation ~/.local/bin/dcf-valuation
```

## 相关工具

- `stock-quote`: 获取实时股价数据
- `gemini-deep-research`: 深度财务分析
- `friday-report-sync`: 估值报告同步到网站

## 数据来源建议

| 数据类型 | 推荐来源 |
|----------|----------|
| 财务报表 | 公司年报/季报、Yahoo Finance |
| 股价数据 | stock-quote skill |
| Beta | Yahoo Finance |
| 债券收益率 | FRED (美联储数据) |
| 行业分析 | Gemini Deep Research |
