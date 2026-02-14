#!/usr/bin/env python3
"""
Friday Portfolio 风险评估工具
计算组合波动率、Beta、夏普比率、VaR、相关性矩阵等风险指标

用法:
    python portfolio_risk.py [--days 90] [--output json|table]
"""

import json
import sys
import argparse
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal
from longport.openapi import QuoteContext, Config
from typing import Dict, List, Tuple, Optional

# 配置
DATA_DIR = Path('/Users/daniel/.openclaw/workspace/investment/data')
PORTFOLIO_FILE = DATA_DIR / 'portfolio.json'

def load_portfolio() -> Dict:
    """加载组合数据"""
    with open(PORTFOLIO_FILE, 'r') as f:
        return json.load(f)

def get_stock_positions(portfolio: Dict) -> List[Dict]:
    """提取股票持仓（用于计算Beta等）"""
    positions = []
    for category, data in portfolio['allocation'].items():
        if category == 'cash':
            continue
        for pos in data.get('positions', []):
            symbol = pos['symbol']
            market_value = pos.get('market_value', pos.get('value', 0))
            if market_value > 0:
                # 转换 API 格式
                if symbol == 'BTC':
                    continue  # 加密货币单独处理
                elif symbol.endswith('.HK'):
                    api_symbol = symbol
                else:
                    api_symbol = f"{symbol}.US"
                
                positions.append({
                    'symbol': symbol,
                    'api_symbol': api_symbol,
                    'market_value': market_value,
                    'category': category
                })
    return positions

def fetch_historical_prices(symbols: List[str], days: int = 90, demo: bool = False) -> Dict[str, List[float]]:
    """从 LongPort API 获取历史价格"""
    if not symbols:
        return {}
    
    if demo:
        print("  📊 演示模式: 生成模拟数据")
        return generate_demo_prices(symbols, days)
    
    try:
        config = Config.from_env()
        ctx = QuoteContext(config)
    except Exception as e:
        print(f"⚠️  LongPort API 配置失败: {e}")
        print("📊 切换到演示模式...")
        return generate_demo_prices(symbols, days)
    
    price_history = {}
    
    for symbol in symbols:
        try:
            # 获取日K线
            candles = ctx.candles(
                symbol,
                period="day",
                count=days,
                adjust_type="forward"
            )
            
            if candles:
                # 提取收盘价
                prices = [float(c.close) for c in candles]
                price_history[symbol] = prices
                print(f"  ✅ {symbol}: {len(prices)} 天数据")
            else:
                print(f"  ⚠️  {symbol}: 无数据")
                
        except Exception as e:
            print(f"  ❌ {symbol}: {str(e)[:50]}")
    
    return price_history

def generate_demo_prices(symbols: List[str], days: int) -> Dict[str, List[float]]:
    """生成模拟价格数据用于演示"""
    np.random.seed(42)  # 固定种子以获得可重复结果
    
    demo_base_prices = {
        'MSFT.US': 415, 'TSLA.US': 410, 'GOOGL.US': 195, 'NVDA.US': 380,
        'GLD.US': 220, 'XLU.US': 75, 'AAPL.US': 225, 'AMZN.US': 230,
        'META.US': 600, 'SPY.US': 590
    }
    
    price_history = {}
    
    for symbol in symbols:
        base_price = demo_base_prices.get(symbol, 100)
        
        # 生成随机游走价格序列
        returns = np.random.normal(0.0005, 0.016, days)  # 均值0.05%, 日波动1.6%
        prices = [base_price]
        
        for ret in returns:
            prices.append(prices[-1] * (1 + ret))
        
        price_history[symbol] = prices
        print(f"  📊 {symbol}: {len(prices)} 天模拟数据 (基准价 ${base_price})")
    
    return price_history

def calculate_returns(prices: List[float]) -> List[float]:
    """计算日收益率序列"""
    if len(prices) < 2:
        return []
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            daily_return = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(daily_return)
    return returns

def calculate_volatility(returns: List[float]) -> float:
    """计算年化波动率"""
    if len(returns) < 2:
        return 0.0
    std = np.std(returns, ddof=1)
    annualized = std * np.sqrt(252)  # 252个交易日
    return annualized

def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
    """计算Beta值"""
    if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
        return 0.0
    
    # 使用协方差/方差计算Beta
    covariance = np.cov(stock_returns, market_returns)[0][1]
    market_variance = np.var(market_returns, ddof=1)
    
    if market_variance == 0:
        return 0.0
    
    beta = covariance / market_variance
    return beta

def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.04) -> float:
    """计算年化夏普比率"""
    if len(returns) < 2:
        return 0.0
    
    excess_returns = [r - risk_free_rate/252 for r in returns]
    avg_excess = np.mean(excess_returns)
    std_excess = np.std(excess_returns, ddof=1)
    
    if std_excess == 0:
        return 0.0
    
    sharpe = (avg_excess / std_excess) * np.sqrt(252)
    return sharpe

def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
    """计算历史VaR (Value at Risk)"""
    if not returns:
        return 0.0
    return np.percentile(returns, (1 - confidence) * 100)

def calculate_max_drawdown(prices: List[float]) -> Tuple[float, int, int]:
    """计算最大回撤及发生时间"""
    if not prices:
        return 0.0, 0, 0
    
    peak = prices[0]
    peak_idx = 0
    max_dd = 0.0
    dd_start = 0
    dd_end = 0
    
    for i, price in enumerate(prices):
        if price > peak:
            peak = price
            peak_idx = i
        
        dd = (peak - price) / peak
        if dd > max_dd:
            max_dd = dd
            dd_start = peak_idx
            dd_end = i
    
    return max_dd, dd_start, dd_end

def calculate_correlation_matrix(price_histories: Dict[str, List[float]]) -> Dict:
    """计算相关性矩阵"""
    symbols = list(price_histories.keys())
    if len(symbols) < 2:
        return {}
    
    # 计算收益率
    returns_data = {}
    for symbol, prices in price_histories.items():
        returns = calculate_returns(prices)
        if returns:
            returns_data[symbol] = returns
    
    if len(returns_data) < 2:
        return {}
    
    # 找到最小长度，使所有序列对齐
    min_len = min(len(r) for r in returns_data.values())
    
    # 构建相关性矩阵
    corr_matrix = {}
    for s1 in returns_data:
        corr_matrix[s1] = {}
        for s2 in returns_data:
            if s1 == s2:
                corr_matrix[s1][s2] = 1.0
            else:
                r1 = returns_data[s1][-min_len:]
                r2 = returns_data[s2][-min_len:]
                corr = np.corrcoef(r1, r2)[0][1]
                corr_matrix[s1][s2] = corr
    
    return corr_matrix

def calculate_concentration_risk(positions: List[Dict]) -> Dict:
    """计算集中度风险"""
    total_value = sum(p['market_value'] for p in positions)
    
    if total_value == 0:
        return {}
    
    # 计算Herfindahl-Hirschman Index (HHI)
    weights = [p['market_value'] / total_value for p in positions]
    hhi = sum(w ** 2 for w in weights)
    
    # 按类别集中度
    category_values = {}
    for pos in positions:
        cat = pos['category']
        category_values[cat] = category_values.get(cat, 0) + pos['market_value']
    
    category_weights = {cat: val/total_value for cat, val in category_values.items()}
    
    return {
        'hhi': hhi,
        'hhi_diversified': hhi < 0.25,  # <0.25表示充分分散
        'max_single_weight': max(weights) if weights else 0,
        'category_weights': category_weights
    }

def get_sp500_proxy() -> str:
    """获取标普500代理ETF"""
    return "SPY.US"  # SPDR S&P 500 ETF

def assess_risk_level(metrics: Dict) -> str:
    """评估整体风险等级"""
    score = 0
    
    # 波动率评分 (0-30)
    vol = metrics.get('portfolio_volatility', 0)
    if vol < 0.15:
        score += 5
    elif vol < 0.25:
        score += 15
    else:
        score += 30
    
    # Beta评分 (0-20)
    beta = metrics.get('portfolio_beta', 1)
    if beta < 0.8:
        score += 5
    elif beta < 1.2:
        score += 10
    else:
        score += 20
    
    # 集中度评分 (0-25)
    hhi = metrics.get('concentration', {}).get('hhi', 0.5)
    if hhi < 0.15:
        score += 5
    elif hhi < 0.25:
        score += 15
    else:
        score += 25
    
    # 最大回撤评分 (0-25)
    mdd = metrics.get('max_drawdown', 0)
    if mdd < 0.15:
        score += 5
    elif mdd < 0.30:
        score += 15
    else:
        score += 25
    
    # 风险等级
    if score <= 20:
        return "低风险 🟢"
    elif score <= 45:
        return "中低风险 🟡"
    elif score <= 70:
        return "中等风险 🟠"
    else:
        return "高风险 🔴"

def format_output(metrics: Dict, output_format: str = 'table') -> str:
    """格式化输出"""
    if output_format == 'json':
        return json.dumps(metrics, indent=2, ensure_ascii=False)
    
    # 表格格式
    lines = []
    lines.append("=" * 70)
    lines.append("           Friday Portfolio 风险评估报告")
    lines.append("=" * 70)
    lines.append(f"\n📅 评估日期: {metrics['date']}")
    lines.append(f"📊 数据周期: 过去 {metrics['lookback_days']} 个交易日")
    lines.append(f"\n🎯 整体风险等级: {metrics['risk_level']}")
    
    # 风险指标
    lines.append(f"\n📈 风险指标:")
    lines.append(f"   组合年化波动率: {metrics['portfolio_volatility']*100:.2f}%")
    lines.append(f"   组合 Beta:      {metrics['portfolio_beta']:.2f}")
    lines.append(f"   夏普比率:       {metrics['sharpe_ratio']:.2f}")
    lines.append(f"   最大回撤:       {metrics['max_drawdown']*100:.2f}%")
    lines.append(f"   VaR (95%):      {metrics['var_95']*100:.2f}%")
    
    # 集中度
    conc = metrics.get('concentration', {})
    lines.append(f"\n📊 集中度分析:")
    lines.append(f"   HHI指数:        {conc.get('hhi', 0):.4f} " + 
                 ("✅ 分散" if conc.get('hhi_diversified') else "⚠️ 集中"))
    lines.append(f"   最大单一持仓:   {conc.get('max_single_weight', 0)*100:.1f}%")
    lines.append(f"   类别分布:")
    for cat, weight in conc.get('category_weights', {}).items():
        lines.append(f"      {cat}: {weight*100:.1f}%")
    
    # 相关性
    corr = metrics.get('correlation_matrix', {})
    if corr:
        lines.append(f"\n🔗 持仓相关性 (高风险组合 > 0.8):")
        symbols = list(corr.keys())
        for i, s1 in enumerate(symbols):
            for s2 in symbols[i+1:]:
                c = corr[s1].get(s2, 0)
                icon = "⚠️" if c > 0.8 else "  "
                lines.append(f"   {icon} {s1} - {s2}: {c:.2f}")
    
    # 个股指标
    lines.append(f"\n📋 个股风险指标:")
    for stock in metrics.get('stock_metrics', []):
        lines.append(f"   {stock['symbol']:10} 波动率:{stock['volatility']*100:>6.1f}% "
                    f"Beta:{stock['beta']:>5.2f} 夏普:{stock['sharpe_ratio']:>5.2f}")
    
    lines.append("\n" + "=" * 70)
    lines.append("💡 风险提示:")
    lines.append("   • 波动率>25%: 高波动，需关注止损")
    lines.append("   • Beta>1.2: 对大盘敏感度高")
    lines.append("   • 夏普比率<1: 风险补偿不足")
    lines.append("   • 相关性>0.8: 分散效果差")
    lines.append("=" * 70)
    
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Friday Portfolio 风险评估')
    parser.add_argument('--days', type=int, default=90, help='回看天数 (默认90)')
    parser.add_argument('--output', type=str, default='table', choices=['json', 'table'],
                        help='输出格式')
    parser.add_argument('--demo', action='store_true', help='演示模式(使用模拟数据)')
    args = parser.parse_args()
    
    print("=" * 70)
    print("Friday Portfolio 风险评估工具")
    print("=" * 70)
    
    # 加载组合
    print(f"\n📂 加载组合数据...")
    portfolio = load_portfolio()
    positions = get_stock_positions(portfolio)
    
    if not positions:
        print("❌ 没有可分析的股票持仓")
        return 1
    
    total_value = sum(p['market_value'] for p in positions)
    print(f"✅ 找到 {len(positions)} 只股票，总市值 ¥{total_value:,.0f}")
    
    # 获取历史价格
    symbols = [p['api_symbol'] for p in positions]
    market_proxy = get_sp500_proxy()
    if market_proxy not in symbols:
        symbols.append(market_proxy)
    
    print(f"\n📡 获取历史价格 ({args.days}天)...")
    if args.demo:
        print("📊 演示模式已启用")
    price_histories = fetch_historical_prices(symbols, args.days, demo=args.demo)
    
    if not price_histories:
        print("❌ 未能获取任何历史价格数据")
        return 1
    
    # 计算市场基准收益率
    market_returns = []
    if market_proxy in price_histories:
        market_returns = calculate_returns(price_histories[market_proxy])
    
    # 计算各股票指标
    print(f"\n🧮 计算风险指标...")
    stock_metrics = []
    portfolio_returns = None
    
    for pos in positions:
        symbol = pos['api_symbol']
        portfolio_symbol = pos['symbol']
        weight = pos['market_value'] / total_value
        
        if symbol not in price_histories:
            continue
        
        prices = price_histories[symbol]
        returns = calculate_returns(prices)
        
        if not returns:
            continue
        
        # 个股指标
        vol = calculate_volatility(returns)
        beta = calculate_beta(returns, market_returns) if market_returns else 0
        sharpe = calculate_sharpe_ratio(returns)
        var = calculate_var(returns)
        mdd, _, _ = calculate_max_drawdown(prices)
        
        stock_metrics.append({
            'symbol': portfolio_symbol,
            'weight': weight,
            'volatility': vol,
            'beta': beta,
            'sharpe_ratio': sharpe,
            'var_95': var,
            'max_drawdown': mdd
        })
        
        # 组合收益率加权
        if portfolio_returns is None:
            portfolio_returns = [r * weight for r in returns]
        else:
            # 对齐长度
            min_len = min(len(portfolio_returns), len(returns))
            portfolio_returns = [portfolio_returns[i] + returns[i] * weight 
                                for i in range(min_len)]
    
    # 计算组合指标
    portfolio_vol = calculate_volatility(portfolio_returns) if portfolio_returns else 0
    portfolio_beta = np.average([s['beta'] for s in stock_metrics], 
                                weights=[s['weight'] for s in stock_metrics]) if stock_metrics else 0
    portfolio_sharpe = calculate_sharpe_ratio(portfolio_returns) if portfolio_returns else 0
    portfolio_var = calculate_var(portfolio_returns) if portfolio_returns else 0
    
    # 最大回撤（用组合价值模拟）
    # 简化为使用持仓加权平均价格序列
    portfolio_prices = None
    for pos in positions:
        symbol = pos['api_symbol']
        weight = pos['market_value'] / total_value
        if symbol in price_histories:
            prices = price_histories[symbol]
            if portfolio_prices is None:
                portfolio_prices = [p * weight for p in prices]
            else:
                min_len = min(len(portfolio_prices), len(prices))
                portfolio_prices = [portfolio_prices[i] + prices[i] * weight 
                                   for i in range(min_len)]
    
    portfolio_mdd, _, _ = calculate_max_drawdown(portfolio_prices) if portfolio_prices else (0, 0, 0)
    
    # 相关性矩阵
    price_histories_no_market = {k: v for k, v in price_histories.items() if k != market_proxy}
    corr_matrix = calculate_correlation_matrix(price_histories_no_market)
    
    # 转换symbol格式
    corr_matrix_clean = {}
    for s1 in corr_matrix:
        clean_s1 = s1.replace('.US', '').replace('.HK', '')
        corr_matrix_clean[clean_s1] = {}
        for s2 in corr_matrix[s1]:
            clean_s2 = s2.replace('.US', '').replace('.HK', '')
            corr_matrix_clean[clean_s1][clean_s2] = corr_matrix[s1][s2]
    
    # 集中度
    concentration = calculate_concentration_risk(positions)
    
    # 汇总
    metrics = {
        'date': datetime.now().isoformat()[:10],
        'lookback_days': args.days,
        'portfolio_volatility': portfolio_vol,
        'portfolio_beta': portfolio_beta,
        'sharpe_ratio': portfolio_sharpe,
        'max_drawdown': portfolio_mdd,
        'var_95': portfolio_var,
        'concentration': concentration,
        'correlation_matrix': corr_matrix_clean,
        'stock_metrics': stock_metrics
    }
    
    # 风险等级
    metrics['risk_level'] = assess_risk_level(metrics)
    
    # 输出
    print(f"\n✅ 分析完成!")
    output = format_output(metrics, args.output)
    print(output)
    
    # 保存JSON
    if args.output == 'json':
        output_file = DATA_DIR / f'risk_report_{metrics["date"]}.json'
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"\n💾 报告已保存: {output_file}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
