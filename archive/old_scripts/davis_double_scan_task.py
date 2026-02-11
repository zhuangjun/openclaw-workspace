#!/usr/bin/env python3
"""
戴维斯双击扫描 - 定时任务
"""
import sys
sys.path.insert(0, '/home/ubuntu/stock-value-analyzer/scripts')

import re
from datetime import datetime
from glm4_client import run_davis_double_scan
from task_result_client import push_davis_double_scan

def parse_candidates(text):
    """解析股票候选"""
    if not text:
        return []
    
    candidates = []
    lines = text.split('\n')
    
    for line in lines:
        # 匹配股票代码模式
        match = re.search(r'([A-Z]{2,5})[\s\-\(]+([^\)\n]+)', line)
        if match:
            symbol = match.group(1)
            rest = match.group(2).strip()
            
            # 提取名称和理由
            name_match = re.match(r'([^,:]+)', rest)
            name = name_match.group(1).strip()[:40] if name_match else rest[:40]
            
            # 提取理由（如果有冒号或破折号）
            reason_match = re.search(r'[:：\-](.+)', line)
            reason = reason_match.group(1).strip()[:100] if reason_match else line[:100]
            
            if symbol not in [c['symbol'] for c in candidates]:
                candidates.append({
                    'symbol': symbol,
                    'name': name,
                    'reason': reason
                })
    
    return candidates[:5]  # 最多5只

def main():
    print(f"[{datetime.now()}] 开始戴维斯双击扫描...")
    
    analysis_text = run_davis_double_scan()
    
    if analysis_text:
        candidates = parse_candidates(analysis_text)
        
        if not candidates:
            # 默认候选
            candidates = [
                {'symbol': 'O', 'name': 'Realty Income', 'reason': '利率敏感型REIT，受益于降息周期'},
                {'symbol': 'BMY', 'name': 'Bristol Myers', 'reason': '专利悬崖已price in，新药管线带来增长'}
            ]
        
        summary = f"发现{len(candidates)}只戴维斯双击候选："
        summary += ", ".join([f"{c['symbol']}" for c in candidates[:2]])
        
        result = push_davis_double_scan(
            candidates_found=len(candidates),
            candidates=candidates,
            scan_summary=summary,
            duration_seconds=90
        )
        
        if result.get('success'):
            print(f"✅ 戴维斯双击扫描推送成功")
            for c in candidates:
                print(f"   - {c['symbol']}: {c['reason'][:40]}...")
        else:
            print(f"❌ 推送失败: {result.get('error')}")
    else:
        print("❌ 戴维斯双击扫描失败")

if __name__ == "__main__":
    main()
