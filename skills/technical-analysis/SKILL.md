---
name: technical-analysis
description: 股票技术分析指标工具，计算移动平均线(MA)、RSI、MACD、布林带等常用技术指标，并生成交易信号
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": { "bins": ["python3"], "python_packages": ["pandas", "numpy"] },
        "install": ["pip3 install pandas numpy"],
      },
  }
---

# Technical Analysis 技术分析指标工具

计算股票常用技术指标，帮助判断买入/卖出时机。

## Features

- **移动平均线 (MA)**: MA5, MA10, MA20, MA60
- **指数移动平均 (EMA)**: EMA12, EMA26
- **RSI**: 相对强弱指标 (14日)
- **MACD**: 异同移动平均线 (12/26/9)
- **布林带**: Bollinger Bands (20日, 2倍标准差)
- **ATR**: 平均真实波幅
- **成交量指标**: OBV, Volume MA
- **交易信号**: 综合评分和买入/卖出建议

## 数据源

工具支持多层级数据源（按优先级）：
1. **LongPort API** - 美股/港股实时数据（需配置环境变量）
2. **Yahoo Finance** - 全球股票数据（需安装 yfinance）
3. **演示模式** - 生成模拟数据（无需任何配置）

## Usage

### 基本用法
```bash
# 分析美股 (演示模式)
technical-analysis --symbol MSFT --demo

# 分析港股 (演示模式)
technical-analysis --symbol 700.HK --demo

# 指定分析天数
 technical-analysis --symbol AAPL --days 60 --demo
```

### JSON 输出
```bash
technical-analysis --symbol MSFT --demo --output json
```

### 保存结果
```bash
technical-analysis --symbol MSFT --demo --output json --save msft_ta.json
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--symbol` | 股票代码 | MSFT, AAPL, 700.HK |
| `--days` | 分析天数 | 30, 60, 90 (默认: 90) |
| `--demo` | 演示模式(模拟数据) | 无需 API 配置 |
| `--output` | 输出格式 | text, json (默认: text) |
| `--save` | 保存到文件 | ./result.json |

## 输出示例

### 文本格式
```
=================================================================
📈 MSFT 技术分析报告
=================================================================

📅 分析时间: 2026-02-14T00:05:30
💰 当前价格: $149.81
📊 成交量: 7,492,862

📈 移动平均线:
   MA5:  $  147.37
   MA20: $   137.5
   MA60: $  124.82
   趋势: ABOVE_MA20

⚡ RSI指标:
   数值: 78.14
   信号: OVERBOUGHT
   建议: 考虑卖出

🔄 MACD指标:
   MACD: 6.634
   信号线: 5.6656
   柱状图: 0.9685
   交叉: ABOVE_SIGNAL
   建议: 多头趋势

📊 布林带:
   上轨: $154.51
   中轨: $137.5
   下轨: $120.48
   位置: 86.19%
   状态: 正常区间

=================================================================
🎯 综合评估
=================================================================

总体信号: ⚪ 观望
置信度: 25.0%
评分: 0.25
建议: 观望
```

### JSON 格式
```json
{
  "timestamp": "2026-02-14T00:05:38",
  "price": {
    "current": 88.37,
    "open": 86.29,
    "high": 90.82,
    "low": 87.66,
    "volume": 8625485
  },
  "moving_averages": {
    "MA5": 89.27,
    "MA20": 91.73,
    "MA60": 98.47,
    "trend": "BELOW_MA20"
  },
  "rsi": {
    "value": 38.14,
    "signal": "NEUTRAL",
    "suggestion": "观望"
  },
  "macd": {
    "macd": -2.607,
    "signal": -2.4842,
    "histogram": -0.1229,
    "cross": "BELOW_SIGNAL",
    "suggestion": "空头趋势"
  },
  "bollinger": {
    "upper": 97.17,
    "middle": 91.73,
    "lower": 86.3,
    "percent": 19.04,
    "position": "WITHIN_BANDS",
    "suggestion": "正常区间"
  },
  "overall_signal": "BEARISH",
  "confidence": 50.0,
  "score": -0.5,
  "suggestion": "看空"
}
```

## 信号解读

### RSI (相对强弱指标)
| 数值 | 信号 | 含义 |
|------|------|------|
| > 70 | OVERBOUGHT | 超买，可能回调 |
| 30-70 | NEUTRAL | 正常区间 |
| < 30 | OVERSOLD | 超卖，可能反弹 |

### MACD
| 信号 | 含义 |
|------|------|
| GOLDEN_CROSS | MACD 上穿信号线，买入信号 |
| DEAD_CROSS | MACD 下穿信号线，卖出信号 |
| ABOVE_SIGNAL | 多头趋势 |
| BELOW_SIGNAL | 空头趋势 |

### 布林带
| 位置 | 含义 |
|------|------|
| ABOVE_UPPER | 价格突破上轨，超买 |
| WITHIN_BANDS | 价格在正常区间 |
| BELOW_LOWER | 价格跌破下轨，超卖 |

### 综合信号
| 信号 | 评分 | 含义 |
|------|------|------|
| BULLISH | > 0.3 | 看多 |
| NEUTRAL | -0.3 ~ 0.3 | 观望 |
| BEARISH | < -0.3 | 看空 |

## 数据源配置

### LongPort API (推荐)
```bash
export LONGPORT_APP_KEY="your_app_key"
export LONGPORT_APP_SECRET="your_app_secret"
export LONGPORT_ACCESS_TOKEN="your_access_token"
```

### Yahoo Finance (备选)
```bash
pip3 install yfinance
```

## 依赖安装

```bash
# 必需依赖
pip3 install pandas numpy

# 可选依赖
pip3 install longport      # LongPort API
pip3 install yfinance      # Yahoo Finance
```

## 使用场景

### 1. 每日盘前分析
```bash
# 分析持仓股
for symbol in MSFT AAPL NVDA; do
    technical-analysis --symbol $symbol --days 30 --output json
done
```

### 2. 交易信号监控
```bash
# 获取 JSON 后解析信号
signal=$(technical-analysis --symbol MSFT --demo --output json | jq -r '.overall_signal')
if [ "$signal" == "BULLISH" ]; then
    echo "考虑买入 MSFT"
fi
```

### 3. 多指标对比
```bash
# 保存多个股票的分析结果
technical-analysis --symbol MSFT --demo --output json --save msft.json
technical-analysis --symbol AAPL --demo --output json --save aapl.json
```

## 注意事项

⚠️ **重要提醒**

1. **技术指标局限性**: 技术分析是概率工具，不能保证盈利
2. **多时间框架**: 建议同时查看日线、周线等多个时间框架
3. **结合基本面**: 技术分析应与基本面分析结合使用
4. **演示模式**: `--demo` 使用模拟数据，仅用于测试和学习

## 相关工具

- `stock-quote`: 获取实时股价
- `dcf-valuation`: DCF 估值分析
- `gemini-deep-research`: 深度基本面分析

## Installation

```bash
ln -sf ~/.openclaw/workspace/skills/technical-analysis/technical-analysis ~/.local/bin/technical-analysis
```

或直接运行：
```bash
python3 /Users/daniel/.openclaw/workspace/investment/technical_analysis.py --symbol MSFT --demo
```
