#!/bin/bash
# Friday Reports 同步脚本
# 将投资报告同步到生产服务器，并生成友好的索引页面

set -e

REPORTS_DIR="/Users/daniel/.openclaw/workspace/investment/reports"
SERVER="ubuntu@43.134.37.253"
REMOTE_DIR="~/friday/reports"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Friday Reports 同步${NC}"
echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"

# 检查本地报告目录是否存在
if [ ! -d "$REPORTS_DIR" ]; then
    echo -e "${RED}❌ 错误: 本地报告目录不存在: $REPORTS_DIR${NC}"
    exit 1
fi

# 生成索引页面
echo -e "${YELLOW}📝 生成索引页面...${NC}"
python3 /Users/daniel/.openclaw/workspace/investment/generate_report_index.py

# 确保远程目录存在
echo -e "${YELLOW}📁 确保远程目录存在...${NC}"
ssh $SERVER "mkdir -p $REMOTE_DIR"

# 同步报告文件（包括生成的 index.html）
echo -e "${YELLOW}📤 同步报告文件到生产服务器...${NC}"
rsync -avz --delete \
  "$REPORTS_DIR/" \
  "$SERVER:$REMOTE_DIR/"

echo ""
echo -e "${GREEN}✅ 报告同步完成!${NC}"
echo -e "🌐 访问地址: ${BLUE}https://danielzhuang.xyz/Friday/reports/${NC}"
echo -e "📁 远程路径: $REMOTE_DIR"
echo ""

# 列出已同步的文件
echo -e "${BLUE}📋 已同步的报告文件:${NC}"
ssh $SERVER "ls -lh $REMOTE_DIR/"
