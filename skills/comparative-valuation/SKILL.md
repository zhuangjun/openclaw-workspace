---
name: comparative-valuation
description: 相对估值分析工具，比较同行业公司的估值倍数 (PE, PB, PS, EV/EBITDA)，识别相对低估/高估机会
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "requires": { "bins": ["python3"], "python_packages": ["yfinance"] },
        "install": ["pip3 install yfinance"],
      },
  }
---

# Comparative Valuation 相对估值分析工具

比较同行业公司的估值倍数，识别相对低估或高估的投资机会。

## Features

- **估值倍数对比**: PE(TTM/Forward), PB, PS, EV/EBITDA
- **成长性分析**: EPS增长, 收入增长, ROE
- **行业均值对比**: 自动计算平均值和中位数
- **PEG指标**: 结合PE和增长率的综合评估
- **排名系统**: 各指标相对排名
- **多数据源**: Yahoo Finance + 演示模式

## 核心概念

### 相对估值 vs 绝对估值

| 方法 | 代表 | 适用场景 |
|------|------|----------|
| **绝对估值** | DCF | 独立判断内在价值 |
| **相对估值** | PE/PB对比 | 同业比较、快速筛选 |

### 关键指标解读

#### PE (市盈率)
```
PE = 股价 / 每股收益
```
- **低PE**: 可能被低估，或增长前景差
- **高PE**: 可能被高估，或高增长预期
- **行业差异**: 科技股PE通常高于银行股

#### PB (市净率)
```
PB = 股价 / 每股净资产
```
- 适用于: 银行、保险、重资产行业
- **PB < 1**: 股价低于账面价值

#### PEG (市盈率增长比)
```
PEG = PE / (盈利增长率 × 100)
```
- **PEG < 1**: 可能被低估
- **PEG > 2**: 可能被高估

## Usage

### 基本用法
```bash
# 比较 MAG7 估值
comparative-valuation --symbols MSFT,AAPL,GOOGL,AMZN,NVDA,META,TSLA

# 演示模式（无需API）
comparative-valuation --symbols MSFT,AAPL,GOOGL --demo

# JSON 输出
comparative-valuation --symbols MSFT,AAPL --output json
```

### 保存结果
```bash
comparative-valuation --symbols MSFT,AAPL,NVDA --save valuation.json
```

## 输出示例

### 文本格式
```
==========================================================================================
📊 相对估值分析报告
==========================================================================================
分析时间: 2026-02-17T00:15:30

【估值倍数对比】
------------------------------------------------------------------------------------------
股票          价格        市值(B)    PE(TTM)    PE(Fwd)       PB       PS    EV/EBITDA
------------------------------------------------------------------------------------------
MSFT        415.82      3,089.0B      34.50      28.20    12.10    12.80      24.50
AAPL        228.02      3,480.0B      32.80      26.50    48.50     8.20      22.10
GOOGL       185.19      2,280.0B      25.20      21.80     6.80     6.10      15.20
...
------------------------------------------------------------------------------------------
平均值                                      30.50      25.50    22.47    9.37      20.43

【成长性指标】
----------------------------------------------------------------------
股票          EPS(TTM)     EPS增长      收入增长        ROE      股息率
----------------------------------------------------------------------
MSFT            12.05        15.0%        12.0%      38.0%       0.7%
AAPL             6.95         8.0%         2.0%     160.0%       0.5%
...
----------------------------------------------------------------------
平均值                                      11.5%         8.0%      35.0%

【估值解读】
----------------------------------------------------------------------
MSFT     PE偏高(34.5x) | PEG>2(高估)
AAPL     PE偏高(32.8x) | 增长缓慢(8%)
GOOGL    PEG<1(低估) | 高增长(25%)
```

### JSON 格式
```json
{
  "metrics": [
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "sector": "Technology",
      "price": 415.82,
      "pe_ttm": 34.5,
      "pe_forward": 28.2,
      "pb": 12.1,
      "eps_growth": 0.15,
      ...
    }
  ],
  "comparison": {
    "averages": {
      "pe_ttm": { "mean": 30.5, "median": 32.8, "min": 25.2, "max": 65.8 }
    },
    "rankings": {
      "pe_ttm": { "GOOGL": 1, "AAPL": 2, "MSFT": 3 }
    }
  }
}
```

## 使用场景

### 1. 行业对比分析
```bash
# 云计算公司对比
comparative-valuation --symbols MSFT,AMZN,GOOGL,CRM,ORCL

# 半导体对比
comparative-valuation --symbols NVDA,AMD,INTC,AVGO,QCOM

# 中国科技股对比
comparative-valuation --symbols BABA,PDD,JD,TCEHY
```

### 2. 寻找被低估标的
```bash
# 获取JSON后筛选PEG<1的股票
comparative-valuation --symbols MSFT,AAPL,GOOGL,AMZN --output json | \
    jq '.metrics[] | select(.pe_ttm != null and .eps_growth != null) | 
        {symbol: .symbol, peg: (.pe_ttm / (.eps_growth * 100))} | 
        select(.peg < 1)'
```

### 3. 定期监控
```bash
# 添加到定时任务，每周比较持仓股
comparative-valuation --symbols MSFT,PDD,9992.HK,3690.HK --save ~/reports/weekly_valuation.json
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--symbols` | 股票代码列表 | MSFT,AAPL,GOOGL |
| `--demo` | 演示模式 | 使用模拟数据 |
| `--output` | 输出格式 | text, json |
| `--save` | 保存文件 | ./result.json |

## 估值解读指南

### PEG 评估
| PEG 范围 | 含义 | 操作建议 |
|----------|------|----------|
| < 1.0 | 可能被低估 | 深入研究 |
| 1.0 - 2.0 | 合理估值 | 结合其他指标 |
| > 2.0 | 可能被高估 | 谨慎 |

### PE 百分位评估
```bash
# PE低于行业均值30% → 相对低估
# PE高于行业均值30% → 相对高估
```

### 综合评估框架
1. **估值水平**: PE/PB/PS vs 行业均值
2. **成长性**: EPS增长 vs 行业均值
3. **盈利质量**: ROE 是否 > 15%
4. **PEG**: 是否 < 1.5

## 局限性与注意事项

⚠️ **重要提醒**

1. **行业差异**: 不同行业的估值倍数差异很大，不要跨行业比较
2. **周期性**: 周期性行业在周期底部PE可能很高（盈利低）
3. **会计差异**: 不同公司的会计政策可能影响可比性
4. **增长阶段**: 成长期和成熟期公司的估值逻辑不同
5. **演示模式**: `--demo` 使用模拟数据，仅用于测试

## 最佳实践

1. **同行业比较**: 确保比较的标的处于同一细分行业
2. **多指标结合**: 不要只看PE，结合PB、PS、PEG
3. **历史对比**: 与标的自身历史估值区间对比
4. **定性分析**: 相对估值后需要深入研究基本面

## 相关工具

- `dcf-valuation`: 绝对估值分析
- `technical-analysis`: 技术分析
- `stock-quote`: 实时股价
- `gemini-deep-research`: 深度基本面分析

## Installation

```bash
ln -sf ~/.openclaw/workspace/skills/comparative-valuation/comparative-valuation ~/.local/bin/comparative-valuation
```

或直接运行：
```bash
python3 /Users/daniel/.openclaw/workspace/skills/comparative-valuation/comparative-valuation --symbols MSFT,AAPL --demo
```

## 依赖安装

```bash
# 必需
pip3 install yfinance

# 可选（用于解析JSON输出）
pip3 install jq
```
