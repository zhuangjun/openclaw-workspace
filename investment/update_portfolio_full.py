#!/usr/bin/env python3
"""
Friday Portfolio 完整更新流程
1. 从 LongPort API 获取美股/港股实时价格
2. 从 CoinMarketCap 获取 BTC 价格
3. 获取实时汇率
4. 计算最新市值和盈亏
5. 更新 portfolio.json

使用方法:
    python update_portfolio_full.py [--sync] [--dry-run] [--display-only]
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from longport.openapi import QuoteContext, Config

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from cmc_price import get_crypto_price
from exchange_rate import get_exchange_rates

# 配置
DATA_DIR = Path('/Users/daniel/.openclaw/workspace/investment/data')
PORTFOLIO_FILE = DATA_DIR / 'portfolio.json'

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
    """从持仓中提取需要查询的股票代码和加密资产"""
    stock_symbols = []
    crypto_symbols = []
    positions_map = {}
    
    for category, data in portfolio['allocation'].items():
        if category == 'cash':
            continue
        for idx, pos in enumerate(data.get('positions', [])):
            symbol = pos['symbol']
            
            # 分类处理
            if symbol == 'BTC':
                crypto_symbols.append('BTC')
                positions_map[symbol] = {
                    'type': 'crypto',
                    'category': category,
                    'index': idx,
                    'name': pos['name'],
                    'shares': pos['shares'],
                    'cost': float(pos['cost']),
                    'currency': 'USD'
                }
            elif symbol.endswith('.HK'):
                stock_symbols.append(symbol)
                positions_map[symbol] = {
                    'type': 'stock',
                    'category': category,
                    'index': idx,
                    'name': pos['name'],
                    'shares': pos['shares'],
                    'cost': float(pos['cost']),
                    'currency': 'HKD'
                }
            elif symbol in ['MSFT', 'TSLA', 'GOOGL', 'NVDA', 'GLD', 'XLU', 'AAPL', 'AMZN', 'META']:
                api_symbol = f"{symbol}.US"
                stock_symbols.append(api_symbol)
                positions_map[api_symbol] = {
                    'type': 'stock',
                    'category': category,
                    'index': idx,
                    'portfolio_symbol': symbol,
                    'name': pos['name'],
                    'shares': pos['shares'],
                    'cost': float(pos['cost']),
                    'currency': 'USD'
                }
    
    return stock_symbols, crypto_symbols, positions_map

def fetch_stock_quotes(symbols):
    """从 LongPort API 获取股票行情"""
    if not symbols:
        return []
    config = Config.from_env()
    ctx = QuoteContext(config)
    return ctx.quote(symbols)

def fetch_crypto_prices(symbols):
    """从 CMC 获取加密货币价格"""
    if not symbols:
        return {}
    return get_crypto_price(symbols)

def update_portfolio_with_prices(portfolio, stock_quotes, crypto_prices, positions_map, fx_rates):
    """使用实时价格更新 portfolio"""
    total_stock_value = 0.0
    
    # 汇率
    usd_cny = fx_rates.get('CNY', 7.25)
    usd_hkd = fx_rates.get('HKD', 7.80)
    hkd_cny = usd_cny / usd_hkd
    
    updated_positions = []
    
    # 处理股票
    for quote in stock_quotes:
        symbol = quote.symbol
        pos_info = positions_map.get(symbol)
        if not pos_info or pos_info['type'] != 'stock':
            continue
        
        current_price = float(quote.last_done)
        shares = pos_info['shares']
        cost = pos_info['cost']
        
        # 计算市值
        market_value = current_price * shares
        cost_value = cost * shares
        
        # 转换为 CNY
        if pos_info['currency'] == 'USD':
            market_value_cny = market_value * usd_cny
            cost_value_cny = cost_value * usd_cny
        elif pos_info['currency'] == 'HKD':
            market_value_cny = market_value * hkd_cny
            cost_value_cny = cost_value * hkd_cny
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
        
        updated_positions.append({
            'symbol': pos_info.get('portfolio_symbol', symbol),
            'type': 'stock',
            'price': current_price,
            'market_value_cny': market_value_cny,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        })
    
    # 处理加密货币
    for crypto_symbol, data in crypto_prices.items():
        pos_info = positions_map.get(crypto_symbol)
        if not pos_info or pos_info['type'] != 'crypto':
            continue
        
        current_price = data['price']
        change_24h = data['change_24h']
        shares = pos_info['shares']
        cost = pos_info['cost']
        
        # 计算市值
        market_value = current_price * shares
        cost_value = cost * shares
        market_value_cny = market_value * usd_cny
        cost_value_cny = cost_value * usd_cny
        
        # 计算盈亏
        pnl = market_value_cny - cost_value_cny
        pnl_pct = (pnl / cost_value_cny * 100) if cost_value_cny else 0
        
        # 更新持仓数据
        category = pos_info['category']
        index = pos_info['index']
        
        portfolio['allocation'][category]['positions'][index]['current_price'] = round(current_price, 2)
        portfolio['allocation'][category]['positions'][index]['market_value'] = round(market_value_cny, 2)
        portfolio['allocation'][category]['positions'][index]['pnl'] = round(pnl, 2)
        portfolio['allocation'][category]['positions'][index]['pnl_pct'] = round(pnl_pct, 2)
        portfolio['allocation'][category]['positions'][index]['change_24h'] = round(change_24h, 2)
        portfolio['allocation'][category]['positions'][index]['last_updated'] = datetime.now().isoformat()
        
        total_stock_value += market_value_cny
        
        updated_positions.append({
            'symbol': crypto_symbol,
            'type': 'crypto',
            'price': current_price,
            'market_value_cny': market_value_cny,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'change_24h': change_24h
        })
    
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
    portfolio['summary']['price_source'] = 'LongPort API + CoinMarketCap'
    portfolio['summary']['fx_rates'] = {
        'USD_CNY': round(usd_cny, 4),
        'HKD_CNY': round(hkd_cny, 4),
        'last_updated': fx_rates.get('last_updated', datetime.now().isoformat())
    }
    
    return portfolio, total_value, updated_positions

def display_summary(portfolio, updated_positions, fx_rates):
    """显示更新后的摘要"""
    summary = portfolio['summary']
    initial = summary['initial_capital']
    current = summary['current_value']
    ret = summary['total_return']
    ret_pct = summary['total_return_pct']
    
    print("\n" + "=" * 65)
    print("       Friday 模拟盘实时估值")
    print("=" * 65)
    print(f"\n📅 更新时间: {summary['last_updated'][:19]}")
    print(f"💰 初始资金: ¥{initial:,.0f}")
    print(f"📊 当前净值: ¥{current:,.0f}")
    
    icon = "🟢" if ret >= 0 else "🔴"
    print(f"{icon} 累计收益: ¥{ret:+,.0f} ({ret_pct:+.2f}%)")
    
    # 汇率信息
    print(f"\n💱 实时汇率:")
    print(f"   USD/CNY: {fx_rates.get('CNY', 7.25):.4f}")
    print(f"   HKD/CNY: {fx_rates.get('CNY', 7.25)/fx_rates.get('HKD', 7.80):.4f}")
    
    print(f"\n📈 各类别占比:")
    for cat, data in portfolio['allocation'].items():
        if cat == 'cash':
            print(f"   💵 现金: ¥{data['value']:,.0f} ({data['value']/current*100:.1f}%)")
        else:
            name = data.get('name', cat)
            ratio = data.get('current_ratio', 0)
            value = data.get('current_value', 0)
            print(f"   📦 {name}: {ratio:.1f}% (¥{value:,.0f})")
    
    print("\n📋 持仓实时明细:")
    # 按市值排序
    sorted_positions = sorted(updated_positions, key=lambda x: x['market_value_cny'], reverse=True)
    for pos in sorted_positions:
        icon = "🟢" if pos['pnl'] >= 0 else "🔴"
        symbol = pos['symbol']
        pnl_pct = pos['pnl_pct']
        if pos['type'] == 'crypto':
            change_info = f"24h:{pos.get('change_24h', 0):+.1f}%"
        else:
            change_info = ""
        print(f"   {icon} {symbol:10} ¥{pos['market_value_cny']:>10,.0f} ({pnl_pct:>+5.1f}%) {change_info}")
    
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description='Friday Portfolio 实时更新')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不保存')
    parser.add_argument('--display-only', action='store_true', help='仅显示当前状态')
    args = parser.parse_args()
    
    print("=" * 65)
    print("Friday Portfolio 实时更新工具")
    print("=" * 65)
    
    # 加载数据
    print(f"\n📂 加载持仓: {PORTFOLIO_FILE}")
    portfolio = load_portfolio()
    
    if args.display_only:
        # 仅显示当前状态
        fx_rates = {'CNY': 7.25, 'HKD': 7.80}
        display_summary(portfolio, [], fx_rates)
        return 0
    
    # 获取实时汇率
    print("\n💱 获取实时汇率...")
    fx_rates = get_exchange_rates()
    print(f"✅ USD/CNY: {fx_rates.get('CNY', 7.25):.4f}")
    
    # 获取股票代码和加密货币
    stock_symbols, crypto_symbols, positions_map = get_symbols_from_portfolio(portfolio)
    print(f"\n📊 发现 {len(stock_symbols)} 只股票, {len(crypto_symbols)} 个加密货币")
    
    # 获取股票行情
    print("\n📡 连接 LongPort API...")
    try:
        stock_quotes = fetch_stock_quotes(stock_symbols)
        print(f"✅ 成功获取 {len(stock_quotes)} 条股票行情")
    except Exception as e:
        print(f"❌ LongPort API 连接失败: {e}")
        return 1
    
    # 获取加密货币价格
    print("\n📡 连接 CoinMarketCap API...")
    try:
        crypto_prices = fetch_crypto_prices(crypto_symbols)
        if crypto_prices:
            print(f"✅ 成功获取 {len(crypto_prices)} 个加密货币价格")
            for sym, data in crypto_prices.items():
                print(f"   {sym}: ${data['price']:,.2f}")
        else:
            print("⚠️  未获取到加密货币价格")
    except Exception as e:
        print(f"⚠️  CMC API 获取失败: {e}")
        crypto_prices = {}
    
    # 更新 portfolio
    print("\n🔄 计算市值和盈亏...")
    portfolio, total_value, updated_positions = update_portfolio_with_prices(
        portfolio, stock_quotes, crypto_prices, positions_map, fx_rates
    )
    
    # 显示结果
    display_summary(portfolio, updated_positions, fx_rates)
    
    # 保存
    if not args.dry_run:
        save_portfolio(portfolio)
        print(f"\n💡 提示: 运行 sync_portfolio.py 可同步到生产服务器")
    else:
        print("\n💡 干运行模式，未保存更改")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
