#!/usr/bin/env python3
"""
Friday 模拟盘实时估值脚本
使用 LongPort API 获取实时价格
"""

import json
import sys
from decimal import Decimal
from longport.openapi import QuoteContext, Config

# 汇率（可改为实时获取）
USD_CNY_RATE = 7.25
HKD_CNY_RATE = 0.93

# LongPort API 配置
LONGPORT_ENABLED = True  # 是否启用 LongPort API

def load_portfolio(path='investment/data/portfolio.json'):
    """加载模拟盘持仓数据"""
    with open(path, 'r') as f:
        return json.load(f)

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
            elif symbol in ['MSFT', 'TSLA', 'GOOGL', 'NVDA', 'GLD', 'XLU', 'AAPL', 'AMZN', 'META']:
                api_symbol = f"{symbol}.US"
            else:
                continue  # BTC 等跳过
            
            symbols.append(api_symbol)
            positions_map[api_symbol] = {
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

def calculate_portfolio_value(quotes, positions_map, cash_value):
    """计算组合市值"""
    total_value = float(cash_value)
    results = []
    
    for quote in quotes:
        symbol = quote.symbol
        pos = positions_map.get(symbol)
        if not pos:
            continue
        
        current_price = float(quote.last_done)
        shares = pos['shares']
        cost = pos['cost']
        
        market_value = current_price * shares
        cost_value = cost * shares
        
        if pos['currency'] == 'USD':
            market_value_cny = market_value * USD_CNY_RATE
            cost_value_cny = cost_value * USD_CNY_RATE
            price_display = f"${current_price:.2f}"
        elif pos['currency'] == 'HKD':
            market_value_cny = market_value * HKD_CNY_RATE
            cost_value_cny = cost_value * HKD_CNY_RATE
            price_display = f"HK${current_price:.2f}"
        else:
            market_value_cny = market_value
            cost_value_cny = cost_value
            price_display = f"¥{current_price:.2f}"
        
        total_value += market_value_cny
        
        pnl = market_value_cny - cost_value_cny
        pnl_pct = (pnl / cost_value_cny * 100) if cost_value_cny else 0
        change_pct = (current_price - float(quote.prev_close)) / float(quote.prev_close) * 100 if quote.prev_close else 0
        
        results.append({
            'symbol': pos['portfolio_symbol'],
            'name': pos['name'][:10],
            'price': price_display,
            'change': change_pct,
            'value': market_value_cny,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'shares': shares,
            'volume': quote.volume
        })
    
    # 按市值排序
    results.sort(key=lambda x: x['value'], reverse=True)
    return total_value, results

def display_portfolio(portfolio, total_value, results):
    """显示组合信息"""
    initial = float(portfolio['summary']['initial_capital'])
    total_return = total_value - initial
    total_return_pct = total_return / initial * 100
    cash = float(portfolio['allocation']['cash']['value'])
    
    print("=" * 70)
    print("       Friday 模拟盘实时估值 (LongPort API)")
    print("=" * 70)
    print(f"\n📅 起始日期: {portfolio['summary']['start_date']}")
    print(f"💰 初始资金: ¥{initial:,.0f}")
    print(f"🎯 策略: {portfolio['summary']['strategy']}")
    
    print("\n" + "-" * 70)
    print(f"{'持仓':<12} {'现价':>12} {'今日':>8} {'市值(CNY)':>14} {'盈亏':>14}")
    print("-" * 70)
    
    for r in results:
        icon = "🟢" if r['pnl'] >= 0 else "🔴"
        print(f"{icon} {r['symbol']:<9} {r['price']:>12} {r['change']:>+7.1f}% ¥{r['value']:>12,.0f} {r['pnl']:>+12,.0f}")
        print(f"   ({r['name']}) 持仓:{r['shares']}股 ({r['pnl_pct']:+.1f}%)")
    
    print("-" * 70)
    print(f"\n💰 总资产:   ¥{total_value:>14,.0f}")
    print(f"💵 现金储备:  ¥{cash:>14,.0f} ({cash/total_value*100:.1f}%)")
    print(f"📊 股票市值:  ¥{total_value-cash:>14,.0f} ({(total_value-cash)/total_value*100:.1f}%)")
    print(f"📈 累计收益:  ¥{total_return:>+14,.0f} ({total_return_pct:+.2f}%)")
    
    # 目标进度
    target_return = initial * 0.20
    print(f"\n🎯 年度目标: +20% (¥{target_return:,.0f})")
    if total_return_pct >= 20:
        print(f"   ✅ 目标已达成！超额完成 +{total_return_pct-20:.2f}%")
    elif total_return_pct > 0:
        remaining = target_return - total_return
        print(f"   ⏳ 距离目标: ¥{remaining:,.0f} (+{20-total_return_pct:.2f}%)")
    else:
        gap = target_return - total_return
        print(f"   📉 当前亏损，距离目标: ¥{gap:,.0f}")
    
    print("\n" + "=" * 70)
    print(f"📡 数据来源: LongPort API | 汇率: USD/CNY={USD_CNY_RATE}, HKD/CNY={HKD_CNY_RATE}")
    print("=" * 70)

def update_portfolio_json(portfolio, total_value, results):
    """更新 portfolio.json 中的市值数据"""
    # 更新 summary
    portfolio['summary']['current_value'] = total_value
    portfolio['summary']['total_return'] = total_value - portfolio['summary']['initial_capital']
    portfolio['summary']['last_updated'] = datetime.now().isoformat()
    portfolio['summary']['price_source'] = 'LongPort API'
    
    # 更新各持仓市值
    for r in results:
        symbol = r['symbol']
        for category, data in portfolio['allocation'].items():
            if category == 'cash':
                continue
            for pos in data.get('positions', []):
                if pos['symbol'] == symbol:
                    pos['current_price'] = r['price']
                    pos['market_value'] = r['value']
                    pos['pnl'] = r['pnl']
                    pos['pnl_pct'] = r['pnl_pct']
    
    # 保存回文件
    with open('investment/data/portfolio.json', 'w') as f:
        json.dump(portfolio, f, indent=2, ensure_ascii=False)
    
    print("\n✅ portfolio.json 已更新")

def main():
    """主函数"""
    from datetime import datetime
    
    print("📡 正在连接 LongPort API...")
    
    try:
        # 加载持仓
        portfolio = load_portfolio()
        
        # 获取股票代码
        symbols, positions_map = get_symbols_from_portfolio(portfolio)
        
        # 获取实时行情
        print(f"🔄 查询 {len(symbols)} 只持仓...")
        quotes = fetch_quotes(symbols)
        
        # 计算市值
        cash_value = portfolio['allocation']['cash']['value']
        total_value, results = calculate_portfolio_value(quotes, positions_map, cash_value)
        
        # 显示结果
        display_portfolio(portfolio, total_value, results)
        
        # 更新文件（可选）
        # update_portfolio_json(portfolio, total_value, results)
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
