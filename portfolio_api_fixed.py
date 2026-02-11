from flask import Blueprint, jsonify, request
import sqlite3
import os
from datetime import datetime

portfolio_bp = Blueprint('portfolio', __name__)
DB_PATH = os.environ.get('FRIDAY_DB_PATH', '/home/ubuntu/friday/friday.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@portfolio_bp.route('/summary')
def get_summary():
    """获取组合摘要"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取最新净值
    cursor.execute('''
        SELECT nav, cumulative_return_pct, nav_date as date 
        FROM portfolio_nav 
        ORDER BY nav_date DESC LIMIT 1
    ''')
    latest = cursor.fetchone()
    
    # 获取持仓分布
    cursor.execute('''
        SELECT category, SUM(market_value) as value, SUM(weight_pct) as weight
        FROM portfolio_positions 
        WHERE category != 'cash'
        GROUP BY category
    ''')
    allocation = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'value': latest['nav'] if latest else 1000000,
        'return_pct': latest['cumulative_return_pct'] if latest else 0,
        'date': latest['date'] if latest else datetime.now().strftime('%Y-%m-%d'),
        'allocation': [dict(row) for row in allocation]
    })

@portfolio_bp.route('/positions')
def get_positions():
    """获取持仓明细"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            id,
            symbol,
            name,
            category,
            position_type,
            shares,
            cost_basis as cost_price,
            cost_basis as current_price,
            market_value as value,
            weight_pct as weight,
            currency,
            updated_at,
            0 as pnl_pct
        FROM portfolio_positions 
        ORDER BY 
            CASE category 
                WHEN 'core' THEN 1 
                WHEN 'satellite' THEN 2 
                WHEN 'defense' THEN 3 
                WHEN 'cash' THEN 4 
            END,
            weight_pct DESC
    ''')
    positions = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in positions])

@portfolio_bp.route('/nav/history')
def get_nav_history():
    """获取净值历史"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT nav_date as date, nav, daily_return_pct, cumulative_return_pct, total_value, notes
        FROM portfolio_nav 
        ORDER BY nav_date DESC 
        LIMIT 90
    ''')
    history = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in history])

@portfolio_bp.route('/trades')
def get_trades():
    """获取交易记录"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            id,
            trade_date as date,
            symbol,
            action as type,
            shares,
            price,
            amount,
            fees,
            notes,
            created_at
        FROM portfolio_trades 
        ORDER BY trade_date DESC, id DESC
        LIMIT 50
    ''')
    trades = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in trades])

@portfolio_bp.route('/update', methods=['POST'])
def update_portfolio():
    """更新持仓数据（从生产环境同步）"""
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 更新持仓
    for position in data.get('positions', []):
        cursor.execute('''
            INSERT OR REPLACE INTO portfolio_positions 
            (symbol, name, category, position_type, shares, cost_basis, market_value, weight_pct, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            position['symbol'], position['name'], position['category'],
            position.get('position_type'), position['shares'], position['cost_basis'],
            position['market_value'], position['weight_pct'], datetime.now()
        ))
    
    # 记录净值
    nav_data = data.get('nav', {})
    cursor.execute('''
        INSERT OR REPLACE INTO portfolio_nav 
        (nav_date, nav, daily_return_pct, cumulative_return_pct, total_value, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        nav_data.get('date', datetime.now().strftime('%Y-%m-%d')),
        nav_data.get('nav'), nav_data.get('daily_return_pct'),
        nav_data.get('cumulative_return_pct'), nav_data.get('total_value'),
        nav_data.get('notes')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'ok'})
