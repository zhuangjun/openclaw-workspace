# Bitcoin Trading Strategy with Daily Alerts

This system implements an automated Bitcoin trading strategy that analyzes daily price data to generate buy/sell signals and sends alerts when optimal entry/exit points are detected.

## Components

1. **bitcoin_strategy.py** - Core trading strategy implementation with technical indicators
2. **bitcoin_alert_system.py** - Alert system that runs daily checks and sends notifications
3. **bitcoin_strategy_plan.md** - Detailed plan for the trading strategy

## Features

- Daily Bitcoin price data fetching from CoinGecko API
- Technical indicators calculation (SMA, EMA, MACD, RSI, Bollinger Bands)
- Automated buy/sell signal detection based on multiple indicators
- Daily alerts when trading opportunities arise
- Comprehensive market overview even when no signals are triggered

## Setup Instructions

1. Install required dependencies:
   ```bash
   pip install requests pandas numpy
   ```

2. To manually test the system:
   ```bash
   python bitcoin_alert_system.py manual
   ```

3. To set up automatic daily alerts, run:
   ```bash
   python bitcoin_alert_system.py setup
   ```
   Then use the generated OpenClaw cron command to schedule the daily checks.

4. To test the strategy without alerts:
   ```bash
   python bitcoin_alert_system.py test
   ```

## Trading Signals Explained

### Buy Signals
- Price crossing above 20-day SMA with RSI indicating oversold conditions (< 35) and bullish MACD crossover
- RSI below 30 combined with price near lower Bollinger Band

### Sell Signals
- Price crossing below 20-day SMA with RSI indicating overbought conditions (> 65) and bearish MACD crossover
- RSI above 70 combined with price near upper Bollinger Band

### Risk Management
- Always verify signals with multiple indicators
- Consider position sizing and stop-loss levels
- Review market conditions before executing trades

## Logs

The system maintains three types of logs:
- `bitcoin_daily_checks.log` - All daily market analyses
- `bitcoin_trading_alerts.log` - Only buy/sell alerts
- `bitcoin_errors.log` - Any errors encountered during operation

## Important Disclaimer

Cryptocurrency trading involves substantial risk. This system provides analytical tools and signals but does not guarantee profits. Always do your own research and consider consulting with financial advisors before making investment decisions.