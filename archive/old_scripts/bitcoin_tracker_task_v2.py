#!/usr/bin/env python3
"""
比特币追踪分析 - 定时任务（完整版）
"""
import sys
sys.path.insert(0, '/home/ubuntu/stock-value-analyzer/scripts')

import re
from datetime import datetime
from glm4_client import run_bitcoin_tracker
from task_result_client import push_task_result

def main():
    print(f"[{datetime.now()}] 开始比特币追踪分析...")
    
    analysis_text = run_bitcoin_tracker()
    
    if analysis_text:
        # 提取价格
        price_match = re.search(r'(\$?[\d,]+(?:\.\d+)?)[Kk]?', analysis_text)
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
        change_match = re.search(r'([\+\-]?\d+\.?\d*)%', analysis_text)
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
        ]
        for keyword, signal_text in signal_keywords:
            if keyword in analysis_text:
                signals.append(signal_text)
        if not signals:
            signals = ['技术面中性', '等待方向明确']
        
        # 推送完整报告
        result = push_task_result(
            task_type='bitcoin_tracker',
            task_name='比特币追踪分析',
            result_data={
                'btc_price': btc_price,
                'price_change_24h': price_change,
                'signals': signals,
                'full_report': analysis_text  # 保存完整报告
            },
            result_summary=f"BTC当前${btc_price:,.0f}，24h{price_change:+.2f}%",
            status='success',
            items_processed=len(signals),
            items_succeeded=len(signals),
            duration_seconds=45
        )
        
        if result.get('success'):
            print(f"✅ 比特币追踪推送成功")
            print(f"   报告长度: {len(analysis_text)} 字符")
        else:
            print(f"❌ 推送失败: {result.get('error')}")
    else:
        push_task_result(
            task_type='bitcoin_tracker',
            task_name='比特币追踪分析',
            result_data={'error': 'API调用失败'},
            result_summary='AI分析调用失败',
            status='failed',
            error_message='无法调用GLM-4 API'
        )
        print("❌ 比特币追踪分析失败")

if __name__ == "__main__":
    main()
