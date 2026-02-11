#!/usr/bin/env python3
"""
执行所有投资定时任务并将结果推送到监控系统
"""

import subprocess
import json
import requests
from datetime import datetime, date
import os
import time

# 配置
API_BASE_URL = "http://localhost:5001/api"
ADMIN_PASSWORD = "03158566"
SCRIPTS_DIR = "/home/ubuntu/stock-value-analyzer/scripts"
LOGS_DIR = "/home/ubuntu/stock-value-analyzer/logs"

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def save_task_result(task_type, task_name, status, result_data, result_summary, 
                     items_processed=0, items_succeeded=0, items_failed=0, 
                     duration_seconds=0, error_message=None):
    """保存任务结果到监控系统"""
    url = f"{API_BASE_URL}/cron-results"
    
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
        "meta_info": {
            "triggered_by": "manual_execution",
            "executed_at": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            log(f"✅ {task_name} 结果已保存")
            return True
        else:
            log(f"❌ {task_name} 结果保存失败: {response.text}")
            return False
    except Exception as e:
        log(f"❌ {task_name} 结果保存异常: {str(e)}")
        return False

def execute_script(script_name, task_type, task_name):
    """执行shell脚本并捕获结果"""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    
    if not os.path.exists(script_path):
        log(f"❌ 脚本不存在: {script_path}")
        return False
    
    log(f"🚀 开始执行: {task_name}")
    start_time = time.time()
    
    try:
        # 执行脚本
        env = os.environ.copy()
        env['ADMIN_PASSWORD'] = ADMIN_PASSWORD
        env['API_BASE_URL'] = API_BASE_URL
        
        result = subprocess.run(
            ['bash', script_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5分钟超时
            env=env
        )
        
        duration = int(time.time() - start_time)
        
        # 解析输出
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode
        
        if returncode == 0:
            status = "success"
            result_summary = f"执行成功，耗时{duration}秒"
            error_message = None
        else:
            status = "failed"
            result_summary = f"执行失败，退出码: {returncode}"
            error_message = stderr[:500] if stderr else "未知错误"
        
        # 提取处理数量（从输出中解析）
        items_processed = 0
        items_succeeded = 0
        
        # 保存结果
        save_task_result(
            task_type=task_type,
            task_name=task_name,
            status=status,
            result_data={
                "stdout": stdout[-2000:] if stdout else "",  # 限制长度
                "stderr": stderr[-500:] if stderr else "",
                "returncode": returncode
            },
            result_summary=result_summary,
            items_processed=items_processed,
            items_succeeded=items_succeeded if status == "success" else 0,
            items_failed=0 if status == "success" else 1,
            duration_seconds=duration,
            error_message=error_message
        )
        
        log(f"{'✅' if status == 'success' else '❌'} {task_name} 执行完成 (耗时{duration}秒)")
        return status == "success"
        
    except subprocess.TimeoutExpired:
        duration = int(time.time() - start_time)
        save_task_result(
            task_type=task_type,
            task_name=task_name,
            status="failed",
            result_data={},
            result_summary="执行超时（超过5分钟）",
            duration_seconds=duration,
            error_message="脚本执行超时"
        )
        log(f"❌ {task_name} 执行超时")
        return False
    except Exception as e:
        duration = int(time.time() - start_time)
        save_task_result(
            task_type=task_type,
            task_name=task_name,
            status="failed",
            result_data={},
            result_summary=f"执行异常: {str(e)}",
            duration_seconds=duration,
            error_message=str(e)
        )
        log(f"❌ {task_name} 执行异常: {str(e)}")
        return False

def execute_api_task(endpoint, task_type, task_name, method="POST", payload=None):
    """直接调用API执行任务"""
    url = f"{API_BASE_URL}{endpoint}"
    
    log(f"🚀 开始执行: {task_name}")
    start_time = time.time()
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": ADMIN_PASSWORD
        }
        
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, json=payload or {}, timeout=300)
        else:
            response = requests.get(url, headers=headers, params=payload or {}, timeout=300)
        
        duration = int(time.time() - start_time)
        
        if response.status_code == 200:
            data = response.json()
            status = "success" if data.get("success") else "partial"
            items_processed = data.get("data", {}).get("processed", 0) if isinstance(data.get("data"), dict) else 0
            
            save_task_result(
                task_type=task_type,
                task_name=task_name,
                status=status,
                result_data=data,
                result_summary=f"API调用成功，处理了{items_processed}项数据" if status == "success" else "API调用部分成功",
                items_processed=items_processed,
                items_succeeded=items_processed if status == "success" else 0,
                duration_seconds=duration
            )
            log(f"✅ {task_name} 执行完成 (耗时{duration}秒)")
            return True
        else:
            save_task_result(
                task_type=task_type,
                task_name=task_name,
                status="failed",
                result_data={"status_code": response.status_code, "response": response.text[:500]},
                result_summary=f"API调用失败，状态码: {response.status_code}",
                duration_seconds=duration,
                error_message=f"HTTP {response.status_code}: {response.text[:200]}"
            )
            log(f"❌ {task_name} API调用失败: {response.status_code}")
            return False
            
    except Exception as e:
        duration = int(time.time() - start_time)
        save_task_result(
            task_type=task_type,
            task_name=task_name,
            status="failed",
            result_data={},
            result_summary=f"API调用异常: {str(e)}",
            duration_seconds=duration,
            error_message=str(e)
        )
        log(f"❌ {task_name} 执行异常: {str(e)}")
        return False

def main():
    log("="*60)
    log("开始执行所有投资定时任务")
    log("="*60)
    
    # 定义要执行的任务
    daily_tasks = [
        # (脚本名, task_type, task_name)
        ("daily_news_update.sh", "daily_news", "每日新闻更新"),
        ("daily_twitter_update.sh", "daily_twitter", "每日推文摘要更新"),
        ("update_asset_performance.sh", "asset_price", "资产价格更新"),
        ("update_market_sentiment.sh", "market_sentiment", "市场情绪指数更新"),
        ("daily_investor_overview.sh", "investor_overview", "每日投资者概览"),
        ("daily_trading_analysis.sh", "trading_analysis", "每日交易分析"),
    ]
    
    # 执行任务
    success_count = 0
    failed_count = 0
    
    for script, task_type, task_name in daily_tasks:
        if execute_script(script, task_type, task_name):
            success_count += 1
        else:
            failed_count += 1
        time.sleep(2)  # 避免请求过于频繁
    
    log("="*60)
    log(f"任务执行完成: 成功 {success_count} 个, 失败 {failed_count} 个")
    log("="*60)
    
    return failed_count == 0

if __name__ == "__main__":
    main()
