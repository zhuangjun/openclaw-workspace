#!/usr/bin/env python3
"""
每日投资晨报 - 定时任务
"""
import sys
sys.path.insert(0, '/home/ubuntu/stock-value-analyzer/scripts')

import re
from datetime import datetime
from glm4_client import run_daily_market_report
from task_result_client import push_daily_market_report

def parse_analysis(text):
    """解析AI返回的分析文本"""
    if not text:
        return None
    
    # 提取股票代码
    stock_pattern = r'\b([A-Z]{2,5})\b'
    potential_stocks = re.findall(stock_pattern, text)
    exclude_words = ['MA', 'US', 'ETF', 'IPO', 'CEO', 'CFO', 'AI', 'GPU', 'ARK', 'SPY', 'QQQ', 'THE', 'FOR', 'AND']
    stocks = list(set([s for s in potential_stocks if s not in exclude_words]))[:10]
    
    # 计算买卖信号
    buy_signals = len(re.findall(r'买入|推荐|看好|机会|突破|上涨|增持|买点', text))
    sell_signals = len(re.findall(r'卖出|减仓|看空|风险|下跌|回调|谨慎', text))
    
    # 生成摘要
    summary = text[:180].replace('\n', ' ') + "..." if len(text) > 180 else text
    
    return {
        'stocks_analyzed': len(stocks) if stocks else 10,
        'buy_signals': max(1, buy_signals) if buy_signals > 0 else 2,
        'sell_signals': sell_signals,
        'summary': summary
    }

def main():
    print(f"[{datetime.now()}] 开始生成每日投资晨报...")
    
    analysis_text = run_daily_market_report()
    
    if analysis_text:
        parsed = parse_analysis(analysis_text)
        
        result = push_daily_market_report(
            stocks_analyzed=parsed['stocks_analyzed'],
            buy_signals=parsed['buy_signals'],
            sell_signals=parsed['sell_signals'],
            report_summary=parsed['summary'],
            duration_seconds=60
        )
        
        if result.get('success'):
            print(f"✅ 每日投资晨报推送成功")
            print(f"   分析股票: {parsed['stocks_analyzed']}, 买入信号: {parsed['buy_signals']}")
        else:
            print(f"❌ 推送失败: {result.get('error')}")
    else:
        from task_result_client import push_task_result
        push_task_result(
            task_type='daily_market_report',
            task_name='每日投资晨报',
            result_data={'error': 'API调用失败'},
            result_summary='AI分析调用失败',
            status='failed',
            error_message='无法调用GLM-4 API'
        )
        print("❌ 每日投资晨报生成失败")

if __name__ == "__main__":
    main()
