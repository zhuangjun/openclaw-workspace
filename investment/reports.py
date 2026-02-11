from flask import Blueprint, jsonify
import os
import re
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

# Reports 目录路径
REPORTS_DIR = '/home/ubuntu/friday/web/reports'

# 报告元数据映射（用于显示标题和描述）
REPORT_META = {
    'unh_dcf_valuation_2026-02-11.html': {
        'icon': '🏥',
        'title': '联合健康(UNH) DCF估值',
        'meta': '监管风暴下的价值重置 | 目标价 $398.50 | 买入评级'
    },
    'pdd_dcf_valuation_2026-02-11.html': {
        'icon': '🛒',
        'title': '拼多多(PDD) DCF估值',
        'meta': '全球化扩张与Temu韧性 | 目标价 $154 | 优于大盘'
    },
    'msft_dcf_valuation_2026-02-11.html': {
        'icon': '📊',
        'title': 'MSFT DCF估值分析',
        'meta': '微软公司现金流折现估值 | 内在价值 $369.50'
    },
    'us_stock_main_theme_2026-02-11.html': {
        'icon': '🇺🇸',
        'title': '美股主线标的分析',
        'meta': 'AI资本回报率审视 · 行业轮动 · 六只精选标的'
    },
    'davis_double_play_2026-02-11.html': {
        'icon': '🎯',
        'title': '戴维斯双击扫描',
        'meta': '7只潜力标的 | 美光(MU)、阿里(9988.HK)等'
    },
    'investment_logic_2026-02-11.html': {
        'icon': '🧠',
        'title': '投资逻辑分析',
        'meta': '美股·港股·黄金·BTC | 策略权重与风险评估'
    }
}


def scan_reports():
    """扫描报告目录，返回报告列表"""
    reports = []
    
    try:
        if not os.path.exists(REPORTS_DIR):
            return []
        
        files = os.listdir(REPORTS_DIR)
        
        for filename in files:
            if filename.endswith('.html') and filename != 'index.html':
                filepath = os.path.join(REPORTS_DIR, filename)
                stat = os.stat(filepath)
                
                # 从文件名提取日期
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
                report_date = date_match.group(1) if date_match else datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                
                # 获取元数据
                meta = REPORT_META.get(filename, {})
                
                # 如果没有预定义元数据，尝试从文件读取
                title = meta.get('title', filename.replace('.html', '').replace('_', ' '))
                description = meta.get('meta', '投资研究报告')
                icon = meta.get('icon', '📄')
                
                if not meta:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # 尝试提取 title
                            title_match = re.search(r'<title>(.+?)</title>', content)
                            if title_match:
                                title = title_match.group(1).split('|')[0].strip()
                            # 尝试提取 h1
                            h1_match = re.search(r'<h1>(.+?)</h1>', content, re.DOTALL)
                            if h1_match:
                                h1_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
                                if len(h1_text) > 5:
                                    title = h1_text
                    except:
                        pass
                
                reports.append({
                    'file': filename,
                    'title': title,
                    'meta': description,
                    'icon': icon,
                    'date': report_date,
                    'size': stat.st_size,
                    'mtime': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # 按修改时间倒序排列
        reports.sort(key=lambda x: x['mtime'], reverse=True)
        
    except Exception as e:
        print(f"扫描报告目录出错: {e}")
    
    return reports


@reports_bp.route('/list')
def get_reports_list():
    """获取报告列表 API"""
    reports = scan_reports()
    return jsonify({
        'success': True,
        'count': len(reports),
        'reports': reports
    })


@reports_bp.route('/scan')
def scan_and_update():
    """手动触发扫描（用于调试）"""
    reports = scan_reports()
    return jsonify({
        'success': True,
        'message': f'扫描完成，找到 {len(reports)} 份报告',
        'count': len(reports),
        'reports': reports
    })