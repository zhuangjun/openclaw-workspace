#!/usr/bin/env python3
"""
直接插入投资组合数据到 Friday 数据库
"""
import json
import sqlite3
from datetime import datetime

# 读取本地交易数据
with open('/Users/daniel/.openclaw/workspace/investment/data/trades.json', 'r') as f:
    trades = json.load(f)

# 连接到远程数据库（通过 SSH 隧道或直接 SCP）
# 先生成 SQL 插入语句

print("-- 持仓数据插入语句")
print("DELETE FROM portfolio_positions;")

category_map = {
    "核心-大仓稳健": "core",
    "卫星-小仓爆发": "satellite",
    "防守型-抗跌": "defense"
}

for trade in trades:
    symbol = trade['symbol']
    name = trade['name']
    category = category_map.get(trade['style'], 'other')
    shares = trade['shares']
    cost_basis = trade['price']
    market_value = trade['amount_cny']
    weight_pct = trade['ratio']
    currency = trade['currency']
    
    print(f"""INSERT INTO portfolio_positions (symbol, name, category, position_type, shares, cost_basis, market_value, weight_pct, currency, updated_at)
VALUES ('{symbol}', '{name}', '{category}', '{trade['style']}', {shares}, {cost_basis}, {market_value}, {weight_pct}, '{currency}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');""")

# 添加现金持仓
print(f"""INSERT INTO portfolio_positions (symbol, name, category, position_type, shares, cost_basis, market_value, weight_pct, currency, updated_at)
VALUES ('CASH', '现金储备', 'cash', '现金储备', 0, 0, 324000, 32.4, 'CNY', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');""")

print("\n-- 净值数据插入语句")
print("DELETE FROM portfolio_nav WHERE nav_date = '2026-02-09';")
print(f"""INSERT INTO portfolio_nav (nav_date, nav, daily_return_pct, cumulative_return_pct, total_value, notes)
VALUES ('2026-02-09', 1000000, 0, 0, 1000000, '初始资金+重新平衡');""")

print("\n-- 交易记录插入语句")
print("DELETE FROM portfolio_trades;")

for trade in trades:
    action = 'buy' if trade['direction'] == '买入' else 'sell'
    notes = f"{trade['style']} | {trade['logic']['background'][:30]}..."
    print(f"""INSERT INTO portfolio_trades (trade_date, symbol, action, shares, price, amount, fees, notes)
VALUES ('{trade['date']}', '{trade['symbol']}', '{action}', {trade['shares']}, {trade['price']}, {trade['amount_cny']}, 0, '{notes}');""")
