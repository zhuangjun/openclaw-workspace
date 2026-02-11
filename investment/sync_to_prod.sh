#!/bin/bash
# Friday Portfolio Sync Script
# 将本地投资组合数据同步到生产环境数据库

set -e

LOCAL_DIR="/Users/daniel/.openclaw/workspace/investment"

echo "🔄 Friday Portfolio 数据同步"
echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查本地目录是否存在
if [ ! -d "$LOCAL_DIR" ]; then
    echo "❌ Error: Local directory $LOCAL_DIR not found"
    exit 1
fi

cd "$LOCAL_DIR"

# 执行数据库同步
echo "📊 同步投资组合数据到生产数据库..."
python3 sync_portfolio.py

echo ""
echo "✅ 同步完成 at $(date '+%Y-%m-%d %H:%M:%S')"
echo "🌐 https://danielzhuang.xyz/Friday"
