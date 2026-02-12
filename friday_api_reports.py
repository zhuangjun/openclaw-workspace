"""
Reports API - 数据库驱动的投资研究报告接口
替代原有的文件扫描方式
"""
from flask import Blueprint, jsonify, request
import sqlite3
import os
import re
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)
DB_PATH = os.environ.get('FRIDAY_DB_PATH', '/home/ubuntu/friday/friday.db')

# API 鉴权 Token（简单实现，生产环境建议使用更安全的方案）
API_TOKEN = os.environ.get('FRIDAY_API_TOKEN', 'dev-token-change-in-production')

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def require_auth():
    """简单的 Token 鉴权检查"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    return token == API_TOKEN

# ========== 报告分类 API ==========

@reports_bp.route('/categories')
def get_categories():
    """获取所有报告分类"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM report_categories 
        ORDER BY display_order
    ''')
    categories = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(categories),
        'categories': [dict(row) for row in categories]
    })

# ========== 报告列表 API ==========

@reports_bp.route('', methods=['GET'])
def get_reports():
    """
    获取报告列表，支持分页和筛选
    
    查询参数:
    - page: 页码（从1开始，默认1）
    - per_page: 每页数量（默认9，对应3天，每天最多3份报告）
    - category: 按类别筛选
    - start_date: 开始日期（YYYY-MM-DD）
    - end_date: 结束日期（YYYY-MM-DD）
    - status: 状态筛选（默认 published）
    - days: 最近N天的数据
    """
    # 解析参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)  # 默认9条 = 3天 x 3份
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status', 'published')
    days = request.args.get('days', type=int)
    
    # 限制每页最大数量
    per_page = min(per_page, 50)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 构建查询条件
    where_clauses = ['status = ?']
    params = [status]
    
    if category:
        where_clauses.append('category = ?')
        params.append(category)
    
    if start_date:
        where_clauses.append('report_date >= ?')
        params.append(start_date)
    
    if end_date:
        where_clauses.append('report_date <= ?')
        params.append(end_date)
    
    if days:
        where_clauses.append('report_date >= date(\"now\", \"-{} days\")'.format(days))
    
    where_sql = ' AND '.join(where_clauses)
    
    # 查询总数
    count_sql = f'SELECT COUNT(*) FROM reports WHERE {where_sql}'
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]
    
    # 计算分页
    total_pages = (total + per_page - 1) // per_page
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    offset = (page - 1) * per_page
    
    # 查询数据
    query_sql = f'''
        SELECT r.*, c.name as category_name, c.icon as category_icon
        FROM reports r
        LEFT JOIN report_categories c ON r.category = c.id
        WHERE {where_sql}
        ORDER BY r.report_date DESC, r.created_at DESC
        LIMIT ? OFFSET ?
    '''
    cursor.execute(query_sql, params + [per_page, offset])
    reports = cursor.fetchall()
    conn.close()
    
    # 格式化结果
    data = []
    for row in reports:
        item = dict(row)
        # 清理大字段，列表接口不返回完整内容
        item['content_md'] = item.get('content_md', '')[:500] + '...' if item.get('content_md') and len(item.get('content_md', '')) > 500 else item.get('content_md', '')
        item['content_html'] = None  # 列表不返回 HTML
        data.append(item)
    
    return jsonify({
        'success': True,
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })

@reports_bp.route('/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """获取单个报告详情"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, c.name as category_name, c.icon as category_icon
        FROM reports r
        LEFT JOIN report_categories c ON r.category = c.id
        WHERE r.id = ?
    ''', (report_id,))
    report = cursor.fetchone()
    
    if not report:
        conn.close()
        return jsonify({'success': False, 'error': 'Report not found'}), 404
    
    conn.close()
    return jsonify({
        'success': True,
        'data': dict(report)
    })

@reports_bp.route('/by-date/<date>', methods=['GET'])
def get_reports_by_date(date):
    """获取指定日期的所有报告"""
    category = request.args.get('category')
    
    conn = get_db()
    cursor = conn.cursor()
    
    sql = '''
        SELECT r.*, c.name as category_name, c.icon as category_icon
        FROM reports r
        LEFT JOIN report_categories c ON r.category = c.id
        WHERE r.report_date = ? AND r.status = 'published'
    '''
    params = [date]
    
    if category:
        sql += ' AND r.category = ?'
        params.append(category)
    
    sql += ' ORDER BY r.created_at DESC'
    
    cursor.execute(sql, params)
    reports = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'date': date,
        'count': len(reports),
        'data': [dict(row) for row in reports]
    })

# ========== 报告管理 API（需鉴权） ==========

@reports_bp.route('', methods=['POST'])
def create_report():
    """
    创建/更新报告
    
    请求体:
    {
        "title": "报告标题",
        "category": "investment_logic",
        "report_date": "2026-02-12",
        "content_md": "# Markdown内容...",
        "content_html": "<html>...</html>",  # 可选
        "summary": "摘要",
        "source": "gemini-research",
        "author": "Friday AI",
        "tags": "美股,AI,投资",
        "related_symbols": "AAPL,MSFT,NVDA"
    }
    """
    if not require_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # 验证必填字段
    required = ['title', 'category', 'report_date']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查是否已存在（根据 category + report_date + title）
    cursor.execute('''
        SELECT id FROM reports 
        WHERE category = ? AND report_date = ? AND title = ?
    ''', (data['category'], data['report_date'], data['title']))
    existing = cursor.fetchone()
    
    if existing:
        # 更新现有报告
        cursor.execute('''
            UPDATE reports SET
                title = ?,
                content_md = ?,
                content_html = ?,
                summary = ?,
                source = ?,
                author = ?,
                tags = ?,
                related_symbols = ?,
                status = ?,
                updated_at = datetime('now')
            WHERE id = ?
        ''', (
            data['title'],
            data.get('content_md', ''),
            data.get('content_html', ''),
            data.get('summary', ''),
            data.get('source', ''),
            data.get('author', 'Friday AI'),
            data.get('tags', ''),
            data.get('related_symbols', ''),
            data.get('status', 'published'),
            existing['id']
        ))
        report_id = existing['id']
        action = 'updated'
    else:
        # 创建新报告
        cursor.execute('''
            INSERT INTO reports 
            (title, category, report_date, content_md, content_html, summary,
             source, author, tags, related_symbols, status, file_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data['category'],
            data['report_date'],
            data.get('content_md', ''),
            data.get('content_html', ''),
            data.get('summary', ''),
            data.get('source', ''),
            data.get('author', 'Friday AI'),
            data.get('tags', ''),
            data.get('related_symbols', ''),
            data.get('status', 'published'),
            data.get('file_name', '')
        ))
        report_id = cursor.lastrowid
        action = 'created'
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'id': report_id,
        'action': action,
        'message': f'Report {action} successfully'
    })

@reports_bp.route('/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """更新报告（需鉴权）"""
    if not require_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查报告是否存在
    cursor.execute('SELECT id FROM reports WHERE id = ?', (report_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Report not found'}), 404
    
    # 构建更新字段
    update_fields = []
    params = []
    
    for field in ['title', 'category', 'report_date', 'content_md', 'content_html', 
                  'summary', 'source', 'author', 'tags', 'related_symbols', 'status']:
        if field in data:
            update_fields.append(f'{field} = ?')
            params.append(data[field])
    
    if not update_fields:
        conn.close()
        return jsonify({'success': False, 'error': 'No fields to update'}), 400
    
    params.append(report_id)
    
    cursor.execute(f'''
        UPDATE reports SET {', '.join(update_fields)}, updated_at = datetime('now')
        WHERE id = ?
    ''', params)
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'id': report_id,
        'message': 'Report updated successfully'
    })

@reports_bp.route('/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """删除报告（需鉴权）"""
    if not require_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Report not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Report deleted successfully'
    })

# ========== 向后兼容：保留旧的路由 ==========

@reports_bp.route('/list', methods=['GET'])
def get_reports_list_legacy():
    """向后兼容：旧版报告列表 API"""
    return get_reports()

@reports_bp.route('/scan', methods=['GET'])
def scan_and_update_legacy():
    """向后兼容：手动触发扫描（现在返回数据库状态）"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM reports WHERE status = \"published\"')
    count = cursor.fetchone()[0]
    
    cursor.execute('SELECT DISTINCT report_date FROM reports ORDER BY report_date DESC LIMIT 5')
    recent_dates = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Database-driven reports API',
        'count': count,
        'recent_dates': recent_dates,
        'note': 'Reports are now stored in database, not scanned from files'
    })

# ========== 统计数据 API ==========

@reports_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取报告统计数据"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 总报告数
    cursor.execute('SELECT COUNT(*) FROM reports WHERE status = \"published\"')
    total = cursor.fetchone()[0]
    
    # 今日报告数
    cursor.execute('SELECT COUNT(*) FROM reports WHERE report_date = date(\"now\")')
    today = cursor.fetchone()[0]
    
    # 本周报告数
    cursor.execute('''
        SELECT COUNT(*) FROM reports 
        WHERE report_date >= date(\"now\", \"weekday 0\", \"-7 days\")
    ''')
    this_week = cursor.fetchone()[0]
    
    # 分类统计
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM reports 
        WHERE status = \"published\"
        GROUP BY category
        ORDER BY count DESC
    ''')
    by_category = [dict(row) for row in cursor.fetchall()]
    
    # 最近7天每日统计
    cursor.execute('''
        SELECT report_date, COUNT(*) as count 
        FROM reports 
        WHERE report_date >= date(\"now\", \"-7 days\")
        GROUP BY report_date
        ORDER BY report_date DESC
    ''')
    daily_stats = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total': total,
            'today': today,
            'this_week': this_week,
            'by_category': by_category,
            'daily_7d': daily_stats
        }
    })
