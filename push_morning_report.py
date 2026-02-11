#!/usr/bin/env python3
"""
推送每日晨报到 Friday Portfolio 生产服务器
"""
import requests
import json
import os
from datetime import datetime, date

API_URL = "https://danielzhuang.xyz/Friday/api/tasks/results/save"

def push_morning_report(report_data: dict) -> dict:
    """
    推送晨报到 Friday Portfolio
    
    report_data 格式:
    {
        "task_type": "morning_report",
        "task_date": "2026-02-10",
        "title": "股市综合晨报 - 2026年2月10日",
        "summary": "美股科技股回调，港股同步走弱...",
        "content": "# 完整报告内容...",
        "content_format": "markdown",
        "metrics": {
            "vix": 16.28,
            "fear_greed_us": 44,
            "fear_greed_crypto": 14
        },
        "category": "market_analysis",
        "tags": "美股,港股,MAG7",
        "source": "openclaw_kimi",
        "confidence": "high"
    }
    """
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 确保 metrics 是 JSON 字符串
    if isinstance(report_data.get('metrics'), dict):
        report_data['metrics'] = json.dumps(report_data['metrics'], ensure_ascii=False)
    
    try:
        response = requests.post(
            API_URL,
            json=report_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ 晨报推送成功: {report_data.get('task_date')}")
            return {"success": True, "data": response.json()}
        else:
            print(f"❌ 推送失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.Timeout:
        print(f"❌ 推送超时")
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        print(f"❌ 推送异常: {str(e)}")
        return {"success": False, "error": str(e)}


def push_from_json_file(json_file_path: str, model: str = "kimi-coding/k2p5", reasoning: str = "medium") -> dict:
    """从 JSON 文件推送晨报"""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # 转换格式，添加模型信息
    report_data = {
        "task_type": data.get("task_type", "morning_report"),
        "task_date": data.get("date", date.today().isoformat()),
        "title": f"股市综合晨报 - {data.get('date', date.today().isoformat())}",
        "summary": data.get("content", "")[:200] + "..." if len(data.get("content", "")) > 200 else data.get("content", ""),
        "content": data.get("content", ""),
        "content_format": "markdown",
        "metrics": data.get("metrics", {}),
        "category": "market_analysis",
        "tags": f"美股,港股,MAG7,晨报,model:{model},reasoning:{reasoning}",
        "source": f"openclaw_{model.replace('/', '_')}_{reasoning}",
        "confidence": "high",
        "status": "completed"
    }
    
    return push_morning_report(report_data)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='推送晨报到 Friday Portfolio')
    parser.add_argument('--json-file', required=True, help='晨报 JSON 文件路径')
    parser.add_argument('--model', default='kimi-coding/k2p5', help='使用的模型')
    parser.add_argument('--reasoning', default='medium', help='推理级别 (low/medium/high)')
    args = parser.parse_args()
    
    result = push_from_json_file(args.json_file, model=args.model, reasoning=args.reasoning)
    print(json.dumps(result, indent=2, ensure_ascii=False))
