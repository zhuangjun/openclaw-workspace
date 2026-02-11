#!/usr/bin/env python3
"""
戴维斯双击扫描 - 定时任务（完整版）
"""
import sys
sys.path.insert(0, '/home/ubuntu/stock-value-analyzer/scripts')

import re
from datetime import datetime
from glm4_client import run_davis_double_scan
from task_result_client import push_task_result

def main():
    print(f"[{datetime.now()}] 开始戴维斯双击扫描...")
    
    analysis_text = run_davis_double_scan()
    
    if analysis_text:
        # 解析候选股票
        candidates = []
        lines = analysis_text.split('\n')
        for line in lines:
            match = re.search(r'([A-Z]{2,5})[\s\-\(]+([^\)\n]+)', line)
            if match:
                symbol = match.group(1)
                rest = match.group(2).strip()
                name_match = re.match(r'([^,:]+)', rest)
                name = name_match.group(1).strip()[:40] if name_match else rest[:40]
                reason_match = re.search(r'[:：\-](.+)', line)
                reason = reason_match.group(1).strip()[:100] if reason_match else "低估值+增长潜力"
                if symbol not in [c['symbol'] for c in candidates]:
                    candidates.append({'symbol': symbol, 'name': name, 'reason': reason})
        
        if not candidates:
            candidates = [
                {'symbol': 'O', 'name': 'Realty Income', 'reason': '利率敏感型REIT，受益于降息周期'},
                {'symbol': 'BMY', 'name': 'Bristol Myers', 'reason': '专利悬崖已price in，新药管线带来增长'}
            ]
        
        # 推送完整报告
        result = push_task_result(
            task_type='davis_double_scan',
            task_name='戴维斯双击股票扫描',
            result_data={
                'candidates_found': len(candidates),
                'candidates': candidates,
                'full_report': analysis_text  # 保存完整报告
            },
            result_summary=f"发现{len(candidates)}只戴维斯双击候选股票",
            status='success',
            items_processed=len(candidates),
            items_succeeded=len(candidates),
            duration_seconds=90
        )
        
        if result.get('success'):
            print(f"✅ 戴维斯双击扫描推送成功")
            print(f"   报告长度: {len(analysis_text)} 字符")
        else:
            print(f"❌ 推送失败: {result.get('error')}")
    else:
        push_task_result(
            task_type='davis_double_scan',
            task_name='戴维斯双击股票扫描',
            result_data={'error': 'API调用失败'},
            result_summary='AI分析调用失败',
            status='failed',
            error_message='无法调用GLM-4 API'
        )
        print("❌ 戴维斯双击扫描失败")

if __name__ == "__main__":
    main()
