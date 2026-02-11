#!/usr/bin/env python3
"""
OpenClaw定时任务结果推送客户端
用于将本地运行的投资定时任务结果推送到生产服务器

使用示例:
    from task_result_client import push_task_result
    
    push_task_result(
        task_type='daily_market_report',
        task_name='每日投资晨报',
        result_data={'stocks': ['AAPL', 'MSFT'], 'signals': 3},
        result_summary='发现3个买入信号',
        status='success',
        items_processed=10
    )
"""

import requests
import os
from datetime import datetime, date
from typing import Dict, Any, Optional

# 生产服务器API配置
PRODUCTION_API_URL = "https://danielzhuang.xyz/Friday/api/tasks/results/save"
# 从环境变量读取API密钥（需要设置）
API_KEY = os.getenv('STOCK_ANALYZER_API_KEY', '')


def push_task_result(
    task_type: str,
    task_name: str,
    result_data: Dict[str, Any],
    result_summary: str,
    status: str = 'success',
    items_processed: int = 0,
    items_succeeded: int = 0,
    items_failed: int = 0,
    duration_seconds: Optional[int] = None,
    error_message: Optional[str] = None,
    meta_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    推送任务执行结果到生产服务器
    
    Args:
        task_type: 任务类型标识（如 daily_market_report, davis_double_scan）
        task_name: 任务显示名称
        result_data: 详细结果数据（字典格式）
        result_summary: 结果摘要（简短描述）
        status: 执行状态（success, failed, partial）
        items_processed: 处理项目总数
        items_succeeded: 成功项目数
        items_failed: 失败项目数
        duration_seconds: 执行耗时（秒）
        error_message: 错误信息（如果失败）
        meta_info: 额外元数据
    
    Returns:
        API响应结果
    """
    
    payload = {
        "task_type": task_type,
        "task_name": task_name,
        "execution_date": date.today().isoformat(),
        "status": status,
        "result_data": result_data,
        "result_summary": result_summary,
        "items_processed": items_processed,
        "items_succeeded": items_succeeded,
        "items_failed": items_failed,
        "duration_seconds": duration_seconds,
        "error_message": error_message,
        "meta_info": meta_info or {
            "source": "openclaw_local",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if API_KEY:
        headers["Authorization"] = API_KEY
    
    try:
        response = requests.post(
            PRODUCTION_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ [{task_name}] 结果推送成功")
            return {"success": True, "data": response.json()}
        else:
            print(f"❌ [{task_name}] 推送失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.Timeout:
        print(f"❌ [{task_name}] 推送超时")
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        print(f"❌ [{task_name}] 推送异常: {str(e)}")
        return {"success": False, "error": str(e)}


def push_daily_market_report(
    stocks_analyzed: int,
    buy_signals: int,
    sell_signals: int,
    report_summary: str,
    duration_seconds: Optional[int] = None
) -> Dict[str, Any]:
    """
    推送每日投资晨报结果
    
    Args:
        stocks_analyzed: 分析的股票数量
        buy_signals: 买入信号数量
        sell_signals: 卖出信号数量
        report_summary: 报告摘要
        duration_seconds: 执行耗时
    """
    return push_task_result(
        task_type='daily_market_report',
        task_name='每日投资晨报',
        result_data={
            'stocks_analyzed': stocks_analyzed,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'market_sentiment': 'bullish' if buy_signals > sell_signals else 'bearish'
        },
        result_summary=report_summary,
        status='success',
        items_processed=stocks_analyzed,
        items_succeeded=stocks_analyzed,
        duration_seconds=duration_seconds
    )


def push_davis_double_scan(
    candidates_found: int,
    candidates: list,
    scan_summary: str,
    duration_seconds: Optional[int] = None
) -> Dict[str, Any]:
    """
    推送戴维斯双击股票扫描结果
    
    Args:
        candidates_found: 发现的候选股票数量
        candidates: 候选股票列表
        scan_summary: 扫描摘要
        duration_seconds: 执行耗时
    """
    return push_task_result(
        task_type='davis_double_scan',
        task_name='戴维斯双击股票扫描',
        result_data={
            'candidates_found': candidates_found,
            'candidates': candidates,
            'scan_date': date.today().isoformat()
        },
        result_summary=scan_summary,
        status='success',
        items_processed=candidates_found,
        items_succeeded=candidates_found,
        duration_seconds=duration_seconds
    )


def push_bitcoin_tracker(
    btc_price: float,
    price_change_24h: float,
    signals: list,
    analysis_summary: str,
    duration_seconds: Optional[int] = None
) -> Dict[str, Any]:
    """
    推送比特币追踪结果
    
    Args:
        btc_price: 当前比特币价格
        price_change_24h: 24小时价格变化（百分比）
        signals: 交易信号列表
        analysis_summary: 分析摘要
        duration_seconds: 执行耗时
    """
    return push_task_result(
        task_type='bitcoin_tracker',
        task_name='比特币追踪分析',
        result_data={
            'btc_price': btc_price,
            'price_change_24h': price_change_24h,
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        },
        result_summary=analysis_summary,
        status='success',
        items_processed=len(signals),
        items_succeeded=len(signals),
        duration_seconds=duration_seconds
    )


# CLI支持
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='推送任务结果到生产服务器')
    parser.add_argument('--task-type', required=True, help='任务类型')
    parser.add_argument('--task-name', required=True, help='任务名称')
    parser.add_argument('--summary', required=True, help='结果摘要')
    parser.add_argument('--data', help='结果数据(JSON字符串)')
    parser.add_argument('--status', default='success', help='执行状态')
    parser.add_argument('--items', type=int, default=0, help='处理项目数')
    
    args = parser.parse_args()
    
    result_data = json.loads(args.data) if args.data else {}
    
    result = push_task_result(
        task_type=args.task_type,
        task_name=args.task_name,
        result_data=result_data,
        result_summary=args.summary,
        status=args.status,
        items_processed=args.items
    )
    
    print(json.dumps(result, indent=2))
