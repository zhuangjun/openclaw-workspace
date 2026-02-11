#!/usr/bin/env python3
"""
Friday Reports 索引页面生成器 - 增强版（支持筛选）
扫描 reports 目录，生成带筛选功能的 HTML 索引页面
"""

import os
import re
import markdown
from datetime import datetime, timedelta
from pathlib import Path

REPORTS_DIR = Path("/Users/daniel/.openclaw/workspace/investment/reports")

def parse_report_filename(filename):
    """解析报告文件名，提取类型和日期"""
    name = filename.replace('.md', '')
    file_path = REPORTS_DIR / filename
    
    # 获取文件修改时间
    mtime = os.path.getmtime(file_path)
    mtime_datetime = datetime.fromtimestamp(mtime)
    
    # 匹配日期格式 (YYYY-MM-DD)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', name)
    date_str = date_match.group(1) if date_match else mtime_datetime.strftime('%Y-%m-%d')
    
    # 提取报告类型
    report_types = {
        'investment_logic': {'name': '投资逻辑分析', 'icon': '🧠', 'color': 'blue'},
        'davis_double_play': {'name': '戴维斯双击扫描', 'icon': '🎯', 'color': 'orange'},
        'market_morning_report': {'name': '股市综合晨报', 'icon': '🌅', 'color': 'purple'},
        'market_report': {'name': '股市综合晨报', 'icon': '🌅', 'color': 'purple'},
        'us_stock_main_theme': {'name': '美股主线分析', 'icon': '🇺🇸', 'color': 'green'},
        'msft_dcf_valuation': {'name': 'DCF估值分析', 'icon': '📊', 'color': 'blue'},
        'a_stock_potential_targets': {'name': 'A股潜力标的', 'icon': '🇨🇳', 'color': 'red'},
        'a_stock_potential_targets': {'name': 'A股潜力标的', 'icon': '🇨🇳', 'color': 'red'},
        'stock_value_analyzer': {'name': '股票价值分析', 'icon': '💎', 'color': 'cyan'},
    }
    
    report_type_key = '投资报告'
    report_type_info = {'name': '投资报告', 'icon': '📄', 'color': 'gray'}
    
    for key, info in report_types.items():
        if key in name.lower():
            report_type_key = key
            report_type_info = info
            break
    
    # 生成友好的标题
    title = name.replace('_', ' ').title()
    if date_match:
        title = title.replace(date_match.group(0), '').strip()
    
    # 解析日期用于筛选
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d') if date_str != "未知日期" else mtime_datetime
    except:
        date_obj = mtime_datetime
    
    return {
        'filename': filename,
        'html_filename': filename.replace('.md', '.html'),
        'date': date_str,
        'time': mtime_datetime.strftime('%H:%M'),
        'date_obj': date_obj,
        'mtime': mtime,
        'type_key': report_type_key,
        'type_name': report_type_info['name'],
        'type_icon': report_type_info['icon'],
        'type_color': report_type_info['color'],
        'title': title,
        'size': os.path.getsize(file_path)
    }

def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} GB"

def generate_html_report(md_file):
    """将 Markdown 文件转换为 HTML"""
    md_path = REPORTS_DIR / md_file
    html_path = REPORTS_DIR / md_file.replace('.md', '.html')
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html_content = md.convert(md_content)
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{md_file.replace('.md', '')} | Friday Reports</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --code-bg: #f1f5f9;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{ font-size: 1.5rem; font-weight: 700; }}
        
        .header a {{
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.2s;
        }}
        
        .header a:hover {{ color: white; }}
        
        .container {{
            max-width: 900px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}
        
        .report-content {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        .report-content h1 {{
            font-size: 2rem;
            margin-bottom: 1rem;
            color: var(--text);
        }}
        
        .report-content h2 {{
            font-size: 1.5rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: var(--text);
            border-bottom: 2px solid var(--border);
            padding-bottom: 0.5rem;
        }}
        
        .report-content h3 {{
            font-size: 1.25rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: var(--text);
        }}
        
        .report-content p {{ margin-bottom: 1rem; color: var(--text); }}
        
        .report-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.9rem;
        }}
        
        .report-content th,
        .report-content td {{
            padding: 0.75rem;
            text-align: left;
            border: 1px solid var(--border);
        }}
        
        .report-content th {{
            background: var(--code-bg);
            font-weight: 600;
            color: var(--text);
        }}
        
        .report-content tr:nth-child(even) {{ background: var(--bg); }}
        
        .report-content code {{
            background: var(--code-bg);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Monaco', monospace;
            font-size: 0.85em;
        }}
        
        .report-content pre {{
            background: var(--code-bg);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        
        .report-content pre code {{ background: none; padding: 0; }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        
        @media (max-width: 768px) {{
            .report-content {{ padding: 1.5rem; }}
            .report-content h1 {{ font-size: 1.5rem; }}
            .report-content h2 {{ font-size: 1.25rem; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <h1>📊 Friday Reports</h1>
            <a href="index.html">← 返回报告列表</a>
        </div>
    </header>
    
    <main class="container">
        <article class="report-content">
{html_content}
        </article>
    </main>
    
    <footer class="footer">
        <p>Friday Portfolio &copy; 2026</p>
    </footer>
</body>
</html>'''
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return html_path.name

def generate_index_page(reports):
    """生成带筛选功能的索引页面"""
    
    # 按文件修改时间倒序排序（最新的在前面）
    reports.sort(key=lambda x: x['mtime'], reverse=True)
    
    # 获取所有类型
    all_types = {}
    for r in reports:
        key = r['type_key']
        if key not in all_types:
            all_types[key] = {'name': r['type_name'], 'icon': r['type_icon'], 'count': 0}
        all_types[key]['count'] += 1
    
    # 生成报告卡片 HTML
    report_cards = []
    for report in reports:
        # 计算距今天数
        days_ago = (datetime.now() - report['date_obj']).days
        date_label = report['date']
        if days_ago == 0:
            date_label = '今天'
        elif days_ago == 1:
            date_label = '昨天'
        elif days_ago < 7:
            date_label = f'{days_ago}天前'
        
        card = f'''
        <div class="report-card" data-date="{report['date']}" data-type="{report['type_key']}" data-days="{days_ago}">
            <div class="report-header">
                <span class="report-type type-{report['type_color']}">
                    <span class="type-icon">{report['type_icon']}</span>
                    {report['type_name']}
                </span>
                <span class="report-date">{date_label} {report['time']}</span>
            </div>
            <h3 class="report-title">{report['title']} <span class="report-date-inline">({report['date']} {report['time']})</span></h3>
            <div class="report-meta">
                <span class="file-size">📄 {format_size(report['size'])}</span>
                <div class="report-actions">
                    <a href="{report['html_filename']}" class="btn btn-primary">阅读报告</a>
                    <a href="{report['filename']}" class="btn btn-secondary" download>下载 MD</a>
                </div>
            </div>
        </div>'''
        report_cards.append(card)
    
    reports_html = '\n'.join(report_cards) if report_cards else '<p class="no-reports">暂无报告</p>'
    
    # 生成类型筛选按钮
    type_buttons = []
    for key, info in sorted(all_types.items(), key=lambda x: -x[1]['count']):
        type_buttons.append(f'<button class="filter-btn" data-filter="type" data-value="{key}"><span class="btn-icon">{info["icon"]}</span> {info["name"]} <span class="btn-count">{info["count"]}</span></button>')
    
    types_html = '\n'.join(type_buttons)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Friday Reports | 投资研究报告库</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --primary-light: #dbeafe;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --success: #10b981;
            --warning: #f59e0b;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        
        .header h1 {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        
        .header p {{ font-size: 1.1rem; opacity: 0.9; max-width: 600px; margin: 0 auto; }}
        
        .stats-bar {{
            background: var(--card-bg);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .stats-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: center;
            gap: 3rem;
            flex-wrap: wrap;
        }}
        
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; color: var(--primary); }}
        .stat-label {{ font-size: 0.85rem; color: var(--text-muted); }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}
        
        /* Filters */
        .filters {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .filter-section {{
            margin-bottom: 1rem;
        }}
        
        .filter-section:last-child {{ margin-bottom: 0; }}
        
        .filter-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.75rem;
            display: block;
        }}
        
        .filter-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .filter-btn {{
            padding: 0.5rem 1rem;
            border: 1px solid var(--border);
            border-radius: 20px;
            background: var(--bg);
            color: var(--text);
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        
        .filter-btn:hover {{
            border-color: var(--primary);
            background: var(--primary-light);
        }}
        
        .filter-btn.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: white;
        }}
        
        .btn-icon {{ font-size: 1.1em; }}
        .btn-count {{
            background: rgba(0,0,0,0.1);
            padding: 0.1rem 0.4rem;
            border-radius: 10px;
            font-size: 0.8em;
        }}
        
        .filter-btn.active .btn-count {{
            background: rgba(255,255,255,0.2);
        }}
        
        .clear-filters {{
            padding: 0.5rem 1rem;
            border: none;
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.9rem;
        }}
        
        .clear-filters:hover {{ color: var(--text); }}
        
        /* Results count */
        .results-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding: 0 0.5rem;
        }}
        
        .results-count {{
            font-size: 1.1rem;
            color: var(--text-muted);
        }}
        
        .results-count strong {{
            color: var(--text);
            font-weight: 600;
        }}
        
        /* Reports Grid */
        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }}
        
        .report-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            transition: all 0.2s;
        }}
        
        .report-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border-color: var(--primary);
        }}
        
        .report-card.hidden {{ display: none; }}
        
        .report-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}
        
        .report-type {{
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        
        .type-icon {{ font-size: 1.1em; }}
        
        .report-type.type-blue {{ background: #dbeafe; color: #1e40af; }}
        .report-type.type-green {{ background: #d1fae5; color: #065f46; }}
        .report-type.type-purple {{ background: #e9d5ff; color: #6b21a8; }}
        .report-type.type-orange {{ background: #ffedd5; color: #9a3412; }}
        .report-type.type-cyan {{ background: #cffafe; color: #155e75; }}
        .report-type.type-gray {{ background: #f3f4f6; color: #374151; }}
        
        .report-date {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        
        .report-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text);
            line-height: 1.4;
        }}
        
        .report-date-inline {{
            font-size: 0.85em;
            font-weight: 500;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }}
        
        .report-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.75rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        
        .file-size {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        
        .report-actions {{
            display: flex;
            gap: 0.5rem;
        }}
        
        .btn {{
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s;
            border: none;
            cursor: pointer;
        }}
        
        .btn-primary {{
            background: var(--primary);
            color: white;
        }}
        
        .btn-primary:hover {{ background: var(--primary-dark); }}
        
        .btn-secondary {{
            background: var(--bg);
            color: var(--text);
            border: 1px solid var(--border);
        }}
        
        .btn-secondary:hover {{ background: var(--border); }}
        
        .no-reports {{
            text-align: center;
            padding: 3rem;
            color: var(--text-muted);
            grid-column: 1 / -1;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .reports-grid {{ grid-template-columns: 1fr; }}
            .filter-buttons {{ gap: 0.4rem; }}
            .filter-btn {{ padding: 0.4rem 0.75rem; font-size: 0.85rem; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>📊 Friday Reports</h1>
        <p>专业的投资研究报告库，支持按时间和类别筛选</p>
    </header>
    
    <div class="stats-bar">
        <div class="stats-content">
            <div class="stat-item">
                <div class="stat-value">{len(reports)}</div>
                <div class="stat-label">报告总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(all_types)}</div>
                <div class="stat-label">报告类型</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{format_size(sum(r['size'] for r in reports))}</div>
                <div class="stat-label">总容量</div>
            </div>
        </div>
    </div>
    
    <main class="container">
        <!-- Filters -->
        <div class="filters">
            <div class="filter-section">
                <span class="filter-label">⏰ 时间筛选</span>
                <div class="filter-buttons">
                    <button class="filter-btn active" data-filter="time" data-value="all">全部时间</button>
                    <button class="filter-btn" data-filter="time" data-value="today">今天</button>
                    <button class="filter-btn" data-filter="time" data-value="week">最近7天</button>
                    <button class="filter-btn" data-filter="time" data-value="month">最近30天</button>
                </div>
            </div>
            
            <div class="filter-section">
                <span class="filter-label">📁 类别筛选</span>
                <div class="filter-buttons">
                    <button class="filter-btn active" data-filter="type" data-value="all">全部类别</button>
{types_html}
                </div>
            </div>
        </div>
        
        <!-- Results -->
        <div class="results-info">
            <span class="results-count">显示 <strong id="visibleCount">{len(reports)}</strong> 份报告</span>
            <button class="clear-filters" onclick="clearAllFilters()">清除筛选</button>
        </div>
        
        <div class="reports-grid" id="reportsGrid">
{reports_html}
        </div>
    </main>
    
    <footer class="footer">
        <p>Friday Portfolio &copy; 2026 | 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p style="margin-top: 0.5rem; font-size: 0.75rem;">⚠️ 本报告仅供参考，不构成投资建议</p>
    </footer>
    
    <script>
        // Filter state
        let activeTimeFilter = 'all';
        let activeTypeFilter = 'all';
        
        // Get all filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        const reportCards = document.querySelectorAll('.report-card');
        const visibleCountEl = document.getElementById('visibleCount');
        
        // Add click handlers
        filterButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                const filterType = btn.dataset.filter;
                const filterValue = btn.dataset.value;
                
                // Update active state
                document.querySelectorAll(`.filter-btn[data-filter="${{filterType}}"]`).forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Update filter state
                if (filterType === 'time') {{
                    activeTimeFilter = filterValue;
                }} else if (filterType === 'type') {{
                    activeTypeFilter = filterValue;
                }}
                
                applyFilters();
            }});
        }});
        
        function applyFilters() {{
            let visibleCount = 0;
            
            reportCards.forEach(card => {{
                const days = parseInt(card.dataset.days);
                const type = card.dataset.type;
                
                let timeMatch = true;
                let typeMatch = true;
                
                // Time filter
                if (activeTimeFilter === 'today') {{
                    timeMatch = days === 0;
                }} else if (activeTimeFilter === 'week') {{
                    timeMatch = days <= 7;
                }} else if (activeTimeFilter === 'month') {{
                    timeMatch = days <= 30;
                }}
                
                // Type filter
                if (activeTypeFilter !== 'all') {{
                    typeMatch = type === activeTypeFilter;
                }}
                
                // Show/hide
                if (timeMatch && typeMatch) {{
                    card.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    card.classList.add('hidden');
                }}
            }});
            
            visibleCountEl.textContent = visibleCount;
        }}
        
        function clearAllFilters() {{
            activeTimeFilter = 'all';
            activeTypeFilter = 'all';
            
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.dataset.value === 'all') {{
                    btn.classList.add('active');
                }}
            }});
            
            applyFilters();
        }}
    </script>
</body>
</html>'''
    
    # 保存索引页面
    index_path = REPORTS_DIR / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return index_path

def main():
    """主函数"""
    print("📝 Friday Reports 索引生成器（增强版）")
    print("=" * 50)
    
    # 扫描报告文件
    reports = []
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith('.md'):
            report_info = parse_report_filename(filename)
            reports.append(report_info)
            
            # 生成 HTML 版本
            print(f"  📄 生成 HTML: {filename}")
            generate_html_report(filename)
    
    if not reports:
        print("⚠️ 没有找到报告文件")
        return
    
    # 生成索引页面
    print(f"\n  📋 找到 {len(reports)} 份报告")
    print("  🎨 生成带筛选功能的索引页面...")
    index_path = generate_index_page(reports)
    
    print(f"\n✅ 完成!")
    print(f"   索引页面: {index_path}")
    print(f"   报告数量: {len(reports)}")
    print(f"   总大小: {format_size(sum(r['size'] for r in reports))}")
    print(f"   功能: 支持按时间/类别筛选 ✨")

if __name__ == '__main__':
    main()
