# Portfolio Risk Assessment Skill

投资组合风险评估工具，计算波动率、Beta、夏普比率、VaR、相关性等风险指标。

## 用途

用于量化评估投资组合的风险水平，包括：
- 组合整体风险指标（波动率、Beta、VaR）
- 风险调整后收益（夏普比率）
- 持仓分散度（相关性矩阵、集中度）
- 个股风险贡献

## 安装要求

```bash
# 依赖 Python 3.8+
pip install numpy longport-openapi

# 需要 LongPort API 配置
# 环境变量或 ~/.longport/config 文件
```

## 使用方法

### 命令行运行

```bash
# 默认输出（表格格式）- 需要 LongPort API 配置
python scripts/portfolio_risk.py

# 演示模式（使用模拟数据，无需 API）
python scripts/portfolio_risk.py --demo

# 指定回看不同时长
python scripts/portfolio_risk.py --days 180

# JSON 输出
python scripts/portfolio_risk.py --output json
```

### 作为模块导入

```python
from scripts.portfolio_risk import (
    load_portfolio,
    calculate_volatility,
    calculate_beta,
    calculate_sharpe_ratio,
    calculate_var,
    calculate_correlation_matrix
)

# 加载组合
portfolio = load_portfolio()

# 获取历史价格并计算指标
# ...
```

## 数据来源

- **股票价格**: LongPort API (长桥证券)
- **市场基准**: SPY (标普500 ETF)
- **组合数据**: investment/data/portfolio.json

## 输出指标说明

| 指标 | 说明 | 参考范围 |
|------|------|---------|
| 年化波动率 | 组合收益波动程度 | <15%低, 15-25%中, >25%高 |
| Beta | 相对于市场的敏感度 | <0.8防御, 0.8-1.2中性, >1.2激进 |
| 夏普比率 | 风险调整后收益 | >1良好, >2优秀 |
| VaR (95%) | 日风险价值 | 单日最大可能亏损 |
| 最大回撤 | 从历史峰值的最大下跌 | <15%优, <30%可接受 |
| HHI | 持仓集中度指数 | <0.25充分分散 |

## 风险等级评估

- 🟢 **低风险**: 综合评分 ≤ 20
- 🟡 **中低风险**: 综合评分 21-45
- 🟠 **中等风险**: 综合评分 46-70
- 🔴 **高风险**: 综合评分 > 70

## 注意事项

1. 需要有效的 LongPort API 凭证
2. 加密货币 (BTC) 不参与 Beta/相关性计算
3. 港股和美股会统一转换为人民币计价
4. 回看天数建议 ≥ 60 天以获得稳定指标

## 开发计划

- [ ] 添加压力测试模块
- [ ] 支持多市场基准（恒生、纳指）
- [ ] 添加风险归因分析
- [ ] 历史风险报告对比
