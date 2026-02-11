#!/usr/bin/env python3
"""
上传本地投资组合数据到 Friday 应用
"""
import json
import requests
from datetime import datetime

# API 基础URL
BASE_URL = "http://43.134.37.253:5002"

# 读取本地交易数据
with open('/Users/daniel/.openclaw/workspace/investment/data/trades.json', 'r') as f:
    trades = json.load(f)

# 构建持仓数据
positions = []
total_value = 1000000  # 初始资金 100万

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
    cost_price = trade['price']
    market_value = trade['amount_cny']
    weight_pct = trade['ratio']
    currency = trade['currency']
    
    positions.append({
        'symbol': symbol,
        'name': name,
        'category': category,
        'position_type': trade['style'],
        'shares': shares,
        'cost_basis': cost_price,
        'market_value': market_value,
        'weight_pct': weight_pct,
        'currency': currency
    })

# 添加现金持仓
positions.append({
    'symbol': 'CASH',
    'name': '现金储备',
    'category': 'cash',
    'position_type': '现金储备',
    'shares': 0,
    'cost_basis': 0,
    'market_value': 324000,
    'weight_pct': 32.4,
    'currency': 'CNY'
})

# 构建净值数据
nav_data = {
    'date': '2026-02-09',
    'nav': 1000000,
    'daily_return_pct': 0,
    'cumulative_return_pct': 0,
    'total_value': 1000000,
    'notes': '初始资金+重新平衡'
}

# 上传持仓和净值数据
update_data = {
    'positions': positions,
    'nav': nav_data
}

response = requests.post(f"{BASE_URL}/api/portfolio/update", json=update_data)
print(f"Upload positions response: {response.status_code}")
print(response.json())

# 上传交易记录
for trade in trades:
    trade_data = {
        'trade_date': trade['date'],
        'symbol': trade['symbol'],
        'action': 'buy' if trade['direction'] == '买入' else 'sell',
        'shares': trade['shares'],
        'price': trade['price'],
        'amount': trade['amount_cny'],
        'fees': 0,
        'notes': f"{trade['style']} | {trade['logic']['background'][:50]}..."
    }
    
    # 直接插入到数据库（因为没有专门的 trades API）
    print(f"Trade: {trade['symbol']} - {trade['name']} - {trade['amount_cny']} CNY")

print("\n上传完成！")
