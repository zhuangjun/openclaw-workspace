---
name: market-sentiment
description: 获取市场情绪指标（VIX、CNN Fear & Greed Index、加密货币恐惧贪婪指数），用于投资情绪分析和市场择时。当用户需要查询市场情绪、恐惧贪婪指数、VIX波动率时使用此skill。
---

# Market Sentiment 市场情绪指标

用于获取和分析市场情绪指标，辅助投资决策中的情绪判断和择时。

## 功能

- **VIX 波动率指数**: 获取 CBOE 波动率指数，判断市场恐慌程度
- **CNN Fear & Greed Index**: CNN 恐惧贪婪指数，综合7个指标的市场情绪
- **加密货币恐惧贪婪指数**: 比特币/加密货币市场情绪指标

## 使用方法

### CLI 命令

```bash
# 获取所有情绪指标
python3 skills/market-sentiment/scripts/sentiment.py

# 仅获取 VIX
python3 skills/market-sentiment/scripts/sentiment.py --vix

# 仅获取 Fear & Greed Index
python3 skills/market-sentiment/scripts/sentiment.py --fear-greed

# 仅获取加密货币指数
python3 skills/market-sentiment/scripts/sentiment.py --crypto

# JSON 输出
python3 skills/market-sentiment/scripts/sentiment.py --json

# 保存到文件
python3 skills/market-sentiment/scripts/sentiment.py --json -o sentiment.json
```

### Python API

```python
from skills.market_sentiment.scripts.sentiment import MarketSentiment, format_sentiment_report

sentiment = MarketSentiment()

# 获取所有指标
data = sentiment.get_all_sentiment()

# 单独获取
vix_data = sentiment.get_vix()
fg_data = sentiment.get_fear_greed_index()
crypto_data = sentiment.get_crypto_fear_greed()

# 格式化报告
report = format_sentiment_report(data)
print(report)
```

## 指标解读

### VIX (波动率指数)
| 区间 | 含义 | 投资建议 |
|------|------|---------|
| < 20 | 平静/自满 | 警惕可能的回调 |
| 20-25 | 正常 | 维持当前策略 |
| 25-30 | 担忧 | 考虑减仓/对冲 |
| > 30 | 恐慌 | 可能是买入机会 |

### Fear & Greed Index (0-100)
| 区间 | 含义 | 投资建议 |
|------|------|---------|
| 0-24 | 极度恐惧 | 强烈买入信号 |
| 25-44 | 恐惧 | 可考虑逐步建仓 |
| 45-55 | 中性 | 持有观望 |
| 56-75 | 贪婪 | 考虑减仓 |
| 76-100 | 极度贪婪 | 强烈卖出信号 |

### CNN Fear & Greed 分项指标

1. **市场动量** (Market Momentum): S&P 500 相对于 125 日移动平均的表现
2. **股价强度** (Stock Price Strength): NYSE 创 52 周新高 vs 新低的股票数
3. **股价宽度** (Stock Price Breadth): 上涨 vs 下跌股票的成交量(McClellan Summation Index)
4. **期权买卖比** (Put/Call Options): 看跌 vs 看涨期权的交易比率
5. **市场波动率** (Market Volatility): 基于 VIX 及其 50 日移动平均
6. **垃圾债需求** (Junk Bond Demand): 高收益债 vs 投资级债券的利差
7. **避险需求** (Safe Haven Demand): 股票 vs 债券的相对回报

## 依赖

```bash
pip install yfinance requests
```

## 注意事项

- CNN Fear & Greed API 可能会有限流，请合理使用
- VIX 数据通过 yfinance 获取 Yahoo Finance 数据
- 加密货币指数来自 alternative.me，更新频率为每日一次
- 所有 API 均为免费公开接口
