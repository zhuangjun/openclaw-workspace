#!/usr/bin/env python3
"""
Friday Portfolio 完整更新流程
1. 从 LongPort API 获取实时价格
2. 计算最新市值和盈亏
3. 更新 portfolio.json
4. 可选：同步到生产服务器

使用方法:
    python update_portfolio_full.py [--sync] [--dry-run]
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from longport.openapi import QuoteContext, Config

# 配置
DATA_DIR = Path('/Users/daniel/.openclaw/workspace/investment/data')
PORTFOLIO_FILE = DATA_DIR / 'portfolio.json'

# 汇率（可配置）
USD_CNY_RATE = 7.25
HKD_CNY_RATE = 0.93

def load_portfolio():
    """加载模拟盘持仓数据"""
    with open(PORTFOLIO_FILE, 'r') as f:
        return json.load(f)

def save_portfolio(portfolio):
    """保存 portfolio.json"""
    with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, indent=2, ensure_ascii=False)
    print(f"✅ 已保存: {PORTFOLIO_FILE}")

def get_symbols_from_portfolio(portfolio):
    """从持仓中提取需要查询的股票代码"""
    symbols = []
    positions_map = {}
    
    for category, data in portfolio['allocation'].items():
        if category == 'cash':
            continue
        for pos in data.get('positions', []):
            symbol = pos['symbol']
            # 转换代码格式
            if symbol.endswith('.HK'):
                api_symbol = symbol
            elif symbol in ['MSFT', 'TSLA', 'GOOGL', 'NVDA', 'GLD', 'XLU', 'AAPL', 'AMZN', 'META', 'BTC']:
                if symbol == 'BTC':
                    continue  # BTC 需要特殊处理
                api_symbol = f"{symbol}.US"
            else:
                continue
            
            symbols.append(api_symbol)
            positions_map[api_symbol] = {
                'category': category,
                'index': portfolio['allocation'][category]['positions'].index(pos),
                'portfolio_symbol': symbol,
                'name': pos['name'],
                'shares': pos['shares'],
                'cost': float(pos['cost']),
                'currency': pos['currency']
            }
    
    return symbols, positions_map

def fetch_quotes(symbols):
    """从 LongPort API 获取实时行情"""
    config = Config.from_env()
    ctx = QuoteContext(config)
    return ctx.quote(symbols)

def update_portfolio_with_live_prices(portfolio, quotes, positions_map):
    """使用实时价格更新 portfolio"""
    total_stock_value = 0.0
    
    for quote in quotes:
        symbol = quote.symbol
        pos_info = positions_map.get(symbol)
        if not pos_info:
            continue
        
        current_price = float(quote.last_done)
        shares = pos_info['shares']
        cost = pos_info['cost']
        
        # 计算市值
        market_value = current_price * shares
        cost_value = cost * shares
        
        # 转换为 CNY
        if pos_info['currency'] == 'USD':
            market_value_cny = market_value * USD_CNY_RATE
            cost_value_cny = cost_value * USD_CNY_RATE
        elif pos_info['currency'] == 'HKD':
            market_value_cny = market_value * HKD_CNY_RATE
            cost_value_cny = cost_value * HKD_CNY_RATE
        else:
            market_value_cny = market_value
            cost_value_cny = cost_value
        
        # 计算盈亏
        pnl = market_value_cny - cost_value_cny
        pnl_pct = (pnl / cost_value_cny * 100) if cost_value_cny else 0
        
        # 更新持仓数据
        category = pos_info['category']
        index = pos_info['index']
        
        portfolio['allocation'][category]['positions'][index]['current_price'] = current_price
        portfolio['allocation'][category]['positions'][index]['market_value'] = round(market_value_cny, 2)
        portfolio['allocation'][category]['positions'][index]['pnl'] = round(pnl, 2)
        portfolio['allocation'][category]['positions'][index]['pnl_pct'] = round(pnl_pct, 2)
        portfolio['allocation'][category]['positions'][index]['last_updated'] = datetime.now().isoformat()
        
        total_stock_value += market_value_cny
    
    # 更新分类总值
    for category, data in portfolio['allocation'].items():
        if category == 'cash':
            continue
        cat_value = sum(p.get('market_value', p.get('value', 0)) for p in data['positions'])
        portfolio['allocation'][category]['current_value'] = round(cat_value, 2)
        portfolio['allocation'][category]['current_ratio'] = round(cat_value / 1000000 * 100, 2)
    
    # 更新汇总
    cash_value = portfolio['allocation']['cash']['value']
    total_value = total_stock_value + cash_value
    initial = portfolio['summary']['initial_capital']
    
    portfolio['summary']['current_value'] = round(total_value, 2)
    portfolio['summary']['total_return'] = round(total_value - initial, 2)
    portfolio['summary']['total_return_pct'] = round((total_value - initial) / initial * 100, 2)
    portfolio['summary']['last_updated'] = datetime.now().isoformat()
    portfolio['summary']['price_source'] = 'LongPort API'
    
    return portfolio, total_value

def display_summary(portfolio):
    """显示更新后的摘要"""
    summary = portfolio['summary']
    initial = summary['initial_capital']
    current = summary['current_value']
    ret = summary['total_return']
    ret_pct = summary['total_return_pct']
    
    print("\n" + "=" * 60)
    print("       Friday 模拟盘更新完成")
    print("=" * 60)
    print(f"\n📅 更新时间: {summary['last_updated'][:19]}")
    print(f"💰 初始资金: ¥{initial:,.0f}")
    print(f"📊 当前净值: ¥{current:,.0f}")
    
    icon = "🟢" if ret >= 0 else "🔴"
    print(f"{icon} 累计收益: ¥{ret:+,.0f} ({ret_pct:+.2f}%)")
    
    print(f"\n📈 各类别占比:")
    for cat, data in portfolio['allocation'].items():
        if cat == 'cash':
            print(f"   💵 现金: {data['value']:,.0f} ({data['value']/current*100:.1f}%)")
        else:
            name = data.get('name', cat)
            ratio = data.get('current_ratio', 0)
            print(f"   📦 {name}: {ratio:.1f}%")
    
    print("\n📋 持仓盈亏明细:")
    for cat, data in portfolio['allocation'].items():
        if cat == 'cash':
            continue
        for pos in data.get('positions', []):
            icon = "🟢" if pos.get('pnl', 0) >= 0 else "🔴"
            print(f"   {icon} {pos['symbol']}: ¥{pos.get('market_value', 0):,.0f} ({pos.get('pnl_pct', 0):+.1f}%)")
    
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description='Friday Portfolio 完整更新')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不保存')
    parser.add_argument('--display-only', action='store_true', help='仅显示当前状态')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Friday Portfolio 实时更新工具")
    print("=" * 60)
    
    # 加载数据
    print(f"\n📂 加载持仓: {PORTFOLIO_FILE}")
    portfolio = load_portfolio()
    
    if args.display_only:
        display_summary(portfolio)
        return 0
    
    # 获取股票代码
    symbols, positions_map = get_symbols_from_portfolio(portfolio)
    print(f"📊 发现 {len(symbols)} 只可交易标的")
    
    # 获取实时行情
    print("\n📡 连接 LongPort API...")
    try:
        quotes = fetch_quotes(symbols)
        print(f"✅ 成功获取 {len(quotes)} 条实时行情")
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        return 1
    
    # 更新 portfolio
    print("\n🔄 计算市值和盈亏...")
    portfolio, total_value = update_portfolio_with_live_prices(portfolio, quotes, positions_map)
    
    # 显示结果
    display_summary(portfolio)
    
    # 保存
    if not args.dry_run:
        save_portfolio(portfolio)
        print(f"\n💡 提示: 运行 sync_portfolio.py 可同步到生产服务器")
    else:
        print("\n💡 干运行模式，未保存更改")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
