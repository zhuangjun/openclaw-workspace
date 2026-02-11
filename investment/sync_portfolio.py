#!/usr/bin/env python3
"""
Friday Portfolio 同步工具
将本地投资组合数据同步到生产环境数据库

使用方法:
    python sync_portfolio.py [--dry-run]

数据来源:
    - data/portfolio.json: 持仓配置和净值
    - data/trades.json: 交易记录

同步目标:
    - 远程服务器 SQLite 数据库: ~/friday/friday.db
    - 表: portfolio_positions, portfolio_nav, portfolio_trades
"""

import json
import argparse
import subprocess
import tempfile
import os
from datetime import datetime
from pathlib import Path

# 配置
LOCAL_DIR = Path('/Users/daniel/.openclaw/workspace/investment')
DATA_DIR = LOCAL_DIR / 'data'
PORTFOLIO_FILE = DATA_DIR / 'portfolio.json'
TRADES_FILE = DATA_DIR / 'trades.json'

# 服务器配置
REMOTE_HOST = 'ubuntu@43.134.37.253'
REMOTE_DB = '/home/ubuntu/friday/friday.db'

# 分类映射
CATEGORY_MAP = {
    "core_large": "core",
    "satellite": "satellite",
    "defensive": "defense"
}

def load_json(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载失败 {filepath}: {e}")
        return None

def generate_sync_sql(portfolio, trades):
    """生成同步 SQL"""
    lines = []
    lines.append("-- Friday Portfolio 同步脚本")
    lines.append(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    summary = portfolio.get('summary', {})
    allocation = portfolio.get('allocation', {})
    
    # 1. 清空并重新插入持仓
    lines.append("-- 1. 同步持仓数据")
    lines.append("DELETE FROM portfolio_positions;")
    lines.append("")
    
    total_value = summary.get('current_value', 1000000)
    
    # 同步各类仓位
    for category_key, category_data in allocation.items():
        if category_key == 'cash':
            continue  # 现金单独处理
        
        category = CATEGORY_MAP.get(category_key, category_key)
        positions = category_data.get('positions', [])
        
        for pos in positions:
            symbol = pos['symbol']
            name = pos['name'].replace("'", "''")
            shares = pos.get('shares', 0)
            cost_basis = pos.get('cost', 0)
            market_value = pos.get('value', 0)
            weight_pct = pos.get('ratio', 0)
            currency = pos.get('currency', 'USD')
            position_type = category_data.get('name', category_key)
            
            lines.append(f"""INSERT INTO portfolio_positions (symbol, name, category, position_type, shares, cost_basis, market_value, weight_pct, currency, updated_at)
VALUES ('{symbol}', '{name}', '{category}', '{position_type}', {shares}, {cost_basis}, {market_value}, {weight_pct}, '{currency}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');""")
    
    # 添加现金
    cash_data = allocation.get('cash', {})
    cash_value = cash_data.get('value', 324000)
    cash_ratio = cash_data.get('current_ratio', 32.4)
    lines.append(f"""INSERT INTO portfolio_positions (symbol, name, category, position_type, shares, cost_basis, market_value, weight_pct, currency, updated_at)
VALUES ('CASH', '现金储备', 'cash', '现金储备', 0, 0, {cash_value}, {cash_ratio}, 'CNY', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');""")
    
    lines.append("")
    
    # 2. 同步净值
    lines.append("-- 2. 同步净值数据")
    nav_date = summary.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    nav = summary.get('current_value', 1000000)
    total_return = summary.get('total_return', 0)
    
    lines.append(f"""INSERT OR REPLACE INTO portfolio_nav (nav_date, nav, daily_return_pct, cumulative_return_pct, total_value, notes)
VALUES ('{nav_date}', {nav}, 0, {total_return}, {nav}, '同步于 {datetime.now().strftime('%Y-%m-%d %H:%M')} | {summary.get('strategy', '')}');""")
    
    lines.append("")
    
    # 3. 同步交易记录
    lines.append("-- 3. 同步交易记录")
    lines.append("DELETE FROM portfolio_trades;")
    lines.append("")
    
    for trade in trades:
        symbol = trade['symbol']
        action = 'buy' if trade.get('direction') == '买入' else 'sell'
        shares = trade.get('shares', 0)
        price = trade.get('price', 0)
        amount = trade.get('amount_cny', 0)
        trade_date = trade.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 构建 notes
        logic = trade.get('logic', {})
        background = logic.get('background', '')[:50].replace("'", "''")
        style = trade.get('style', '').replace("'", "''")
        notes = f"{style} | {background}..."
        
        lines.append(f"""INSERT INTO portfolio_trades (trade_date, symbol, action, shares, price, amount, fees, notes)
VALUES ('{trade_date}', '{symbol}', '{action}', {shares}, {price}, {amount}, 0, '{notes}');""")
    
    lines.append("")
    lines.append("-- 同步完成")
    
    return '\n'.join(lines)

def execute_remote_sync(sql_content, dry_run=False):
    """在远程服务器执行 SQL"""
    # 写入临时 SQL 文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql_content)
        temp_sql = f.name
    
    try:
        # 复制到远程
        scp_cmd = ['scp', temp_sql, f'{REMOTE_HOST}:/tmp/portfolio_sync.sql']
        print(f"📤 复制 SQL 到远程服务器...")
        
        if not dry_run:
            result = subprocess.run(scp_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ SCP 失败: {result.stderr}")
                return False
            print("✅ SQL 文件已上传")
        
        # 在远程执行 SQL
        sqlite_cmd = f"sqlite3 {REMOTE_DB} < /tmp/portfolio_sync.sql"
        ssh_cmd = ['ssh', REMOTE_HOST, sqlite_cmd]
        print(f"🔄 执行数据库同步...")
        
        if not dry_run:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ SQL 执行失败: {result.stderr}")
                return False
            print("✅ 数据库同步成功")
        
        return True
        
    finally:
        os.unlink(temp_sql)

def main():
    parser = argparse.ArgumentParser(description='同步投资组合到 Friday 生产环境')
    parser.add_argument('--dry-run', action='store_true', help='仅生成 SQL，不执行')
    parser.add_argument('--output', '-o', help='输出 SQL 文件路径')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Friday Portfolio 同步工具")
    print("=" * 60)
    print()
    
    # 加载数据
    print(f"📂 加载持仓数据: {PORTFOLIO_FILE}")
    portfolio = load_json(PORTFOLIO_FILE)
    if not portfolio:
        print("❌ 无法加载 portfolio.json")
        return 1
    
    print(f"📂 加载交易数据: {TRADES_FILE}")
    trades = load_json(TRADES_FILE)
    if trades is None:
        trades = []
    print(f"   共 {len(trades)} 笔交易")
    
    # 计算持仓数量
    allocation = portfolio.get('allocation', {})
    position_count = sum(len(cat.get('positions', [])) for cat in allocation.values() if isinstance(cat, dict) and 'positions' in cat)
    print(f"   共 {position_count} 个持仓")
    
    # 生成 SQL
    print("\n📝 生成同步 SQL...")
    sql = generate_sync_sql(portfolio, trades)
    
    # 输出或执行
    if args.output:
        with open(args.output, 'w') as f:
            f.write(sql)
        print(f"✅ SQL 已保存到: {args.output}")
    
    if args.dry_run:
        print("\n--- SQL 预览 ---")
        print(sql[:1500])
        print("...")
        print("\n💡 干运行模式，未实际执行")
    else:
        print(f"\n🌐 同步到生产服务器: {REMOTE_HOST}")
        if execute_remote_sync(sql, dry_run=False):
            print("\n" + "=" * 60)
            print("✅ 同步成功!")
            print("=" * 60)
            print(f"\n📊 持仓总数: {position_count} + 现金")
            print(f"💰 净值: ¥{portfolio.get('summary', {}).get('current_value', 0):,}")
            print(f"📈 交易记录: {len(trades)} 笔")
            print(f"\n🌐 访问: https://danielzhuang.xyz/Friday")
        else:
            print("\n❌ 同步失败")
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
