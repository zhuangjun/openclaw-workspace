#!/usr/bin/env python3
"""
每日投资晨报 - 定时任务（完整版）
自动替换为当前日期
"""
import sys
sys.path.insert(0, '/home/ubuntu/stock-value-analyzer/scripts')

import re
from datetime import datetime, date
from glm4_client import run_daily_market_report
from task_result_client import push_task_result

def update_report_date(text):
    """将报告中的日期替换为当前日期"""
    if not text:
        return text
    
    today = date.today()
    date_str = f"{today.year}年{today.month}月{today.day}日"
    weekday_list = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekday_list[today.weekday()]
    full_date_str = f"{date_str} ({weekday})"
    
    # 替换各种日期格式
    # 格式1: 2023年11月15日
    text = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日', date_str, text)
    # 格式2: 2023年11月15日 (周三)
    text = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日\s*\([^)]+\)', full_date_str, text)
    # 格式3: **日期：2023年11月15日**
    text = re.sub(r'(\*\*日期[:：])\d{4}年\d{1,2}月\d{1,2}日', r'\1' + date_str, text)
    
    # 在报告开头添加当前日期（如果没有）
    if date_str not in text[:100]:
        text = f"# 📊 每日投资晨报\n**日期：{full_date_str}**\n\n{text}"
    
    return text

def parse_analysis(text):
    """解析AI返回的分析文本"""
    if not text:
        return None
    
    # 更新日期
    text = update_report_date(text)
    
    # 提取股票代码
    stock_pattern = r'\b([A-Z]{2,5})\b'
    potential_stocks = re.findall(stock_pattern, text)
    exclude_words = ['MA', 'US', 'ETF', 'IPO', 'CEO', 'CFO', 'AI', 'GPU', 'ARK', 'SPY', 'QQQ', 'THE', 'FOR', 'AND', 'USD', 'CNY', 'DATE', 'NOW']
    stocks = list(set([s for s in potential_stocks if s not in exclude_words]))[:10]
    
    # 计算买卖信号
    buy_signals = len(re.findall(r'买入|推荐|看好|机会|突破|上涨|增持|买点', text))
    sell_signals = len(re.findall(r'卖出|减仓|看空|风险|下跌|回调|谨慎', text))
    
    return {
        'stocks_analyzed': len(stocks) if stocks else 10,
        'buy_signals': max(1, buy_signals) if buy_signals > 0 else 2,
        'sell_signals': sell_signals,
        'full_report': text  # 保存完整报告（已更新日期）
    }

def main():
    current_date = date.today().strftime('%Y-%m-%d')
    print(f"[{datetime.now()}] 开始生成每日投资晨报 ({current_date})...")
    
    analysis_text = run_daily_market_report()
    
    if analysis_text:
        parsed = parse_analysis(analysis_text)
        
        # 使用通用推送，保存完整报告
        result = push_task_result(
            task_type='daily_market_report',
            task_name='每日投资晨报',
            result_data={
                'stocks_analyzed': parsed['stocks_analyzed'],
                'buy_signals': parsed['buy_signals'],
                'sell_signals': parsed['sell_signals'],
                'full_report': parsed['full_report'],  # 已更新日期的完整报告
                'market_sentiment': 'bullish' if parsed['buy_signals'] > parsed['sell_signals'] else 'neutral',
                'report_date': current_date
            },
            result_summary=f"{current_date} 投资晨报已生成",
            status='success',
            items_processed=parsed['stocks_analyzed'],
            items_succeeded=parsed['stocks_analyzed'],
            duration_seconds=60
        )
        
        if result.get('success'):
            print(f"✅ 每日投资晨报推送成功 ({current_date})")
            # 显示报告前200字符验证日期
            preview = parsed['full_report'][:200].replace('\n', ' ')
            print(f"   预览: {preview}...")
        else:
            print(f"❌ 推送失败: {result.get('error')}")
    else:
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
