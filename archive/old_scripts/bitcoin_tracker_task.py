#!/usr/bin/env python3
"""
比特币追踪分析 - 定时任务
"""
import sys
sys.path.insert(0, '/home/ubuntu/stock-value-analyzer/scripts')

import re
from datetime import datetime
from glm4_client import run_bitcoin_tracker
from task_result_client import push_bitcoin_tracker

def parse_btc_analysis(text):
    """解析BTC分析"""
    if not text:
        return None
    
    # 提取价格
    price_match = re.search(r'(\$?[\d,]+(?:\.\d+)?)[Kk]?', text)
    btc_price = 98500.0
    
    if price_match:
        price_str = price_match.group(1).replace(',', '').replace('$', '')
        try:
            price = float(price_str)
            if price < 100:
                price *= 1000
            btc_price = price
        except:
            pass
    
    # 提取涨跌幅
    change_match = re.search(r'([\+\-]?\d+\.?\d*)%', text)
    price_change = 0.0
    if change_match:
        try:
            price_change = float(change_match.group(1))
        except:
            pass
    
    # 提取信号
    signals = []
    signal_keywords = [
        ('突破', '突破关键阻力位'),
        ('支撑', '在支撑位企稳'),
        ('超买', 'RSI显示超买'),
        ('超卖', 'RSI显示超卖'),
        ('金叉', 'MACD金叉信号'),
        ('死叉', 'MACD死叉信号'),
        ('多头', '均线多头排列'),
        ('空头', '均线空头排列'),
        ('背离', '出现背离信号'),
        ('放量', '成交量放大'),
        ('缩量', '成交量萎缩')
    ]
    
    for keyword, signal_text in signal_keywords:
        if keyword in text:
            signals.append(signal_text)
    
    if not signals:
        signals = ['技术面中性', '等待方向明确']
    
    # 生成摘要
    summary = f"BTC当前${btc_price:,.0f}"
    if price_change != 0:
        summary += f"，24h{price_change:+.2f}%"
    summary += f"。信号：{', '.join(signals[:2])}"
    
    return {
        'btc_price': btc_price,
        'price_change_24h': price_change,
        'signals': signals[:4],
        'summary': summary
    }

def main():
    print(f"[{datetime.now()}] 开始比特币追踪分析...")
    
    analysis_text = run_bitcoin_tracker()
    
    if analysis_text:
        parsed = parse_btc_analysis(analysis_text)
        
        result = push_bitcoin_tracker(
            btc_price=parsed['btc_price'],
            price_change_24h=parsed['price_change_24h'],
            signals=parsed['signals'],
            analysis_summary=parsed['summary'],
            duration_seconds=45
        )
        
        if result.get('success'):
            print(f"✅ 比特币追踪推送成功")
            print(f"   BTC: ${parsed['btc_price']:,.0f} ({parsed['price_change_24h']:+.2f}%)")
            print(f"   信号: {', '.join(parsed['signals'])}")
        else:
            print(f"❌ 推送失败: {result.get('error')}")
    else:
        print("❌ 比特币追踪分析失败")

if __name__ == "__main__":
    main()
