#!/bin/bash
# Friday Reports 数据库重构部署脚本
# 在服务器上执行此脚本完成部署

set -e

echo "=========================================="
echo "📊 Friday Reports 数据库重构部署"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FRIDAY_DIR="${FRIDAY_DIR:-/home/ubuntu/friday}"
BACKUP_DIR="$FRIDAY_DIR/backups/$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}📁 Friday目录: $FRIDAY_DIR${NC}"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 步骤1: 备份现有文件
echo -e "${YELLOW}📦 步骤1: 备份现有文件...${NC}"
if [ -f "$FRIDAY_DIR/api/routes/reports.py" ]; then
    cp "$FRIDAY_DIR/api/routes/reports.py" "$BACKUP_DIR/reports_old.py"
    echo "   ✅ 已备份 API routes"
fi
if [ -f "$FRIDAY_DIR/reports/index.html" ]; then
    cp "$FRIDAY_DIR/reports/index.html" "$BACKUP_DIR/index_old.html"
    echo "   ✅ 已备份前端页面"
fi

# 步骤2: 执行数据库迁移
echo ""
echo -e "${YELLOW}🗄️  步骤2: 执行数据库迁移...${NC}"
if [ -f "$FRIDAY_DIR/migrations/create_reports_table.sql" ]; then
    sqlite3 "$FRIDAY_DIR/friday.db" < "$FRIDAY_DIR/migrations/create_reports_table.sql"
    echo "   ✅ 数据库表已创建"
else
    echo -e "${RED}   ❌ 迁移文件不存在${NC}"
    exit 1
fi

# 步骤3: 更新API路由
echo ""
echo -e "${YELLOW}🔌 步骤3: 更新API路由...${NC}"
if [ -f "$FRIDAY_DIR/updates/friday_api_reports.py" ]; then
    cp "$FRIDAY_DIR/updates/friday_api_reports.py" "$FRIDAY_DIR/api/routes/reports.py"
    echo "   ✅ API路由已更新"
else
    echo -e "${RED}   ❌ 新API文件不存在${NC}"
    exit 1
fi

# 步骤4: 更新前端页面
echo ""
echo -e "${YELLOW}🎨 步骤4: 更新前端页面...${NC}"
if [ -f "$FRIDAY_DIR/updates/friday_reports_index.html" ]; then
    cp "$FRIDAY_DIR/updates/friday_reports_index.html" "$FRIDAY_DIR/reports/index.html"
    echo "   ✅ 前端页面已更新"
else
    echo -e "${RED}   ❌ 新前端文件不存在${NC}"
    exit 1
fi

# 步骤5: 复制同步脚本
echo ""
echo -e "${YELLOW}📤 步骤5: 安装同步脚本...${NC}"
if [ -f "$FRIDAY_DIR/updates/sync_report_api.sh" ]; then
    cp "$FRIDAY_DIR/updates/sync_report_api.sh" "$FRIDAY_DIR/scripts/"
    chmod +x "$FRIDAY_DIR/scripts/sync_report_api.sh"
    echo "   ✅ 同步脚本已安装"
fi

# 步骤6: 检查环境变量
echo ""
echo -e "${YELLOW}🔐 步骤6: 检查环境变量...${NC}"
if [ -z "$FRIDAY_API_TOKEN" ]; then
    echo -e "   ${YELLOW}⚠️  警告: FRIDAY_API_TOKEN 未设置${NC}"
    echo "      请在 ~/.bashrc 中添加:"
    echo "      export FRIDAY_API_TOKEN='your-secure-token'"
else
    echo "   ✅ FRIDAY_API_TOKEN 已设置"
fi

# 步骤7: 重启API服务
echo ""
echo -e "${YELLOW}🔄 步骤7: 重启API服务...${NC}"
if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet friday-api; then
        sudo systemctl restart friday-api
        echo "   ✅ 服务已通过 systemd 重启"
    else
        echo "   ⚠️  friday-api 服务未运行，尝试手动启动"
        pkill -f "python.*app.py" 2>/dev/null || true
        cd "$FRIDAY_DIR/api"
        nohup python3 app.py > "$FRIDAY_DIR/logs/api.log" 2>&1 &
        echo "   ✅ 服务已手动启动"
    fi
else
    pkill -f "python.*app.py" 2>/dev/null || true
    cd "$FRIDAY_DIR/api"
    nohup python3 app.py > "$FRIDAY_DIR/logs/api.log" 2>&1 &
    echo "   ✅ 服务已重启"
fi

# 步骤8: 等待服务启动
echo ""
echo -e "${YELLOW}⏳ 步骤8: 等待服务启动...${NC}"
sleep 3

# 步骤9: 测试API
echo ""
echo -e "${YELLOW}🧪 步骤9: 测试API...${NC}"
if curl -s "http://localhost:5003/api/health" > /dev/null 2>&1; then
    echo "   ✅ API服务运行正常"
else
    echo -e "   ${YELLOW}⚠️  无法连接到本地API，请检查服务状态${NC}"
fi

# 步骤10: 显示完成信息
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 部署完成!${NC}"
echo "=========================================="
echo ""
echo "备份位置: $BACKUP_DIR"
echo ""
echo "验证命令:"
echo "  curl http://localhost:5003/api/reports/categories"
echo "  curl http://localhost:5003/api/reports/stats"
echo ""
echo "访问地址:"
echo "  https://danielzhuang.xyz/Friday/reports/"
echo ""
echo "如需回滚:"
echo "  cp $BACKUP_DIR/reports_old.py $FRIDAY_DIR/api/routes/reports.py"
echo "  cp $BACKUP_DIR/index_old.html $FRIDAY_DIR/reports/index.html"
echo "=========================================="
