---
name: portfolio-risk
description: 投资组合风险分析工具。用于计算 VaR (风险价值)、最大回撤、夏普比率、索提诺比率、波动率等风险指标。支持单资产分析和组合风险分析，兼容 LongPort API、Yahoo Finance 和演示数据模式。
---

# Portfolio Risk Analysis - 投资组合风险分析

## 用途

当需要分析投资组合或单个资产的风险指标时使用此工具。

## 核心功能

### 风险指标

| 指标 | 说明 |
|------|------|
| **VaR (95%/99%)** | 风险价值，正常情况下的最大预期损失 |
| **CVaR** | 条件VaR，超过VaR阈值的平均损失 |
| **最大回撤** | 从高点到低点的最大跌幅 |
| **年化波动率** | 价格波动程度 |
| **下行波动率** | 只考虑负收益的波动率 |

### 调整收益指标

| 指标 | 说明 |
|------|------|
| **夏普比率** | (收益-无风险利率)/波动率 |
| **索提诺比率** | (收益-无风险利率)/下行波动率 |
| **卡玛比率** | 年化收益/最大回撤 |

### 收益分布特征

- **偏度 (Skewness)**: 收益分布的不对称性
- **峰度 (Kurtosis)**: 收益分布的尾部厚度
- **Jarque-Bera 检验**: 正态性检验

## 使用方法

### 单资产分析

```bash
cd investment

# 基础分析 (演示模式)
python3 portfolio_risk.py --symbol MSFT --days 90 --demo

# 分析港股
python3 portfolio_risk.py --symbol 700.HK --days 60 --demo

# JSON 输出
python3 portfolio_risk.py --symbol MSFT --output json
```

### 组合分析

```bash
# 分析整个投资组合
python3 portfolio_risk.py --portfolio-file data/portfolio.json --days 252
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--symbol` | 股票代码 | - |
| `--portfolio-file` | 组合 JSON 文件 | - |
| `--days` | 历史数据天数 | 252 |
| `--risk-free-rate` | 无风险利率 | 4.5% |
| `--demo` | 使用演示数据 | False |
| `--output` | 输出格式 (table/json) | table |

## 数据源

按优先级尝试:

1. **LongPort API** (已配置时) - 美股/港股实时数据
2. **Yahoo Finance** (已安装 yfinance) - 美股/港股
3. **演示数据** - 模拟价格数据

## 风险评级标准

| 评级 | 说明 |
|------|------|
| 🔴 高风险 | 高波动率或高回撤 |
| 🟡 中高风险 | 中等偏高风险 |
| 🟢 中等风险 | 中等风险 |
| 🔵 低风险 | 低波动率且低回撤 |

## 依赖

```bash
pip3 install pandas numpy scipy --user
```

## 文件位置

- **主脚本**: `investment/portfolio_risk.py`
- **技能文档**: `skills/portfolio-risk/SKILL.md`

## VaR 解读

VaR 表示在正常市场条件下，特定置信度下的最大预期损失。

例如：95% VaR = -2.2% 表示
- 在95%的交易日，日亏损不会超过2.2%
- 如果投资10万元，正常日亏损不超过2200元
- 只有5%的交易日亏损会超过这个值
