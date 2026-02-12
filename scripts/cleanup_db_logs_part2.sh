#!/bin/bash
# Friday Database Cleanup Script - Part 2
# 清理 technical_indicator_history 和 batch_task_items 表的一周前数据
# 注意：执行前请确认！

set -e

# 配置
DB_PATH="${1:-/home/ubuntu/stock-value-analyzer/backend/stock_analyzer.db}"
DRY_RUN="${2:---dry-run}"  # 默认试运行模式
DAYS_TO_KEEP=7

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📊 Friday 数据库清理脚本 - Part 2${NC}"
echo "=================================="
echo "目标表: technical_indicator_history, batch_task_items"
echo "数据库: $DB_PATH"
echo "保留天数: $DAYS_TO_KEEP 天"
echo "模式: $DRY_RUN"
echo ""

# 检查数据库文件
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}❌ 错误: 数据库文件不存在: $DB_PATH${NC}"
    exit 1
fi

# 获取当前数据库大小
echo -e "${YELLOW}📁 当前数据库状态:${NC}"
echo "文件大小: $(du -h $DB_PATH | cut -f1)"
echo ""

# 统计清理前的数据量
echo -e "${YELLOW}📊 清理前统计:${NC}"

# technical_indicator_history 统计
echo -e "\n${BLUE}表: technical_indicator_history${NC}"
TOTAL_TECH=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM technical_indicator_history;" 2>/dev/null || echo "0")
OLD_TECH=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM technical_indicator_history WHERE created_at < datetime('now', '-$DAYS_TO_KEEP days');" 2>/dev/null || echo "0")
TO_KEEP_TECH=$((TOTAL_TECH - OLD_TECH))
echo "  总行数: $TOTAL_TECH"
echo "  一周前数据: $OLD_TECH"
echo "  将保留: $TO_KEEP_TECH"

# batch_task_items 统计
echo -e "\n${BLUE}表: batch_task_items${NC}"
TOTAL_ITEMS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM batch_task_items;" 2>/dev/null || echo "0")
OLD_ITEMS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM batch_task_items WHERE started_at < datetime('now', '-$DAYS_TO_KEEP days');" 2>/dev/null || echo "0")
TO_KEEP_ITEMS=$((TOTAL_ITEMS - OLD_ITEMS))
echo "  总行数: $TOTAL_ITEMS"
echo "  一周前数据: $OLD_ITEMS"
echo "  将保留: $TO_KEEP_ITEMS"

echo ""
echo -e "${YELLOW}⚠️  将要删除的数据:${NC}"
echo "  technical_indicator_history: $OLD_TECH 行"
echo "  batch_task_items: $OLD_ITEMS 行"
echo "  合计: $((OLD_TECH + OLD_ITEMS)) 行"
echo ""

# 试运行模式
if [ "$DRY_RUN" == "--dry-run" ]; then
    echo -e "${YELLOW}🔍 试运行模式 - 不会实际删除数据${NC}"
    echo -e "${GREEN}如需执行清理，请运行: $0 $DB_PATH --execute${NC}"
    echo ""
    echo -e "${YELLOW}📋 将执行的 SQL 语句预览:${NC}"
    echo ""
    echo "-- 清理 technical_indicator_history"
    echo "DELETE FROM technical_indicator_history WHERE created_at < datetime('now', '-$DAYS_TO_KEEP days');"
    echo ""
    echo "-- 清理 batch_task_items"  
    echo "DELETE FROM batch_task_items WHERE started_at < datetime('now', '-$DAYS_TO_KEEP days');"
    echo ""
    echo "-- 清理后执行 VACUUM 回收空间"
    echo "VACUUM;"
    echo ""
    exit 0
fi

# 执行模式
if [ "$DRY_RUN" != "--execute" ]; then
    echo -e "${RED}❌ 错误: 未知的运行模式 '$DRY_RUN'${NC}"
    echo "用法: $0 [数据库路径] [--dry-run|--execute]"
    exit 1
fi

# 确认执行
echo -e "${RED}⚠️  警告: 即将执行数据清理！${NC}"
echo -e "${RED}这将删除 $((OLD_TECH + OLD_ITEMS)) 行数据，且不可恢复！${NC}"
echo ""
read -p "输入 'DELETE' 确认执行: " CONFIRM

if [ "$CONFIRM" != "DELETE" ]; then
    echo -e "${YELLOW}❌ 操作已取消${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🗑️  开始清理数据...${NC}"

# 创建备份
echo -e "${BLUE}📦 创建数据库备份...${NC}"
BACKUP_FILE="/home/ubuntu/db_backup/stock_analyzer_pre_cleanup_part2_$(date +%Y%m%d_%H%M%S).db"
cp "$DB_PATH" "$BACKUP_FILE"
echo -e "${GREEN}✅ 备份已创建: $BACKUP_FILE${NC}"
echo ""

# 执行清理
echo -e "${BLUE}🗑️  清理 technical_indicator_history...${NC}"
sqlite3 "$DB_PATH" "DELETE FROM technical_indicator_history WHERE created_at < datetime('now', '-$DAYS_TO_KEEP days');"
TECH_DELETED=$?

if [ $TECH_DELETED -eq 0 ]; then
    echo -e "${GREEN}✅ technical_indicator_history 清理完成${NC}"
else
    echo -e "${RED}❌ technical_indicator_history 清理失败${NC}"
fi

echo ""
echo -e "${BLUE}🗑️  清理 batch_task_items...${NC}"
sqlite3 "$DB_PATH" "DELETE FROM batch_task_items WHERE started_at < datetime('now', '-$DAYS_TO_KEEP days');"
ITEMS_DELETED=$?

if [ $ITEMS_DELETED -eq 0 ]; then
    echo -e "${GREEN}✅ batch_task_items 清理完成${NC}"
else
    echo -e "${RED}❌ batch_task_items 清理失败${NC}"
fi

# 执行 VACUUM 回收空间
echo ""
echo -e "${BLUE}🧹 执行 VACUUM 回收空间...${NC}"
sqlite3 "$DB_PATH" "VACUUM;"
echo -e "${GREEN}✅ VACUUM 完成${NC}"

# 统计清理后的数据
echo ""
echo -e "${YELLOW}📊 清理后统计:${NC}"
NEW_TOTAL_TECH=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM technical_indicator_history;" 2>/dev/null || echo "0")
NEW_TOTAL_ITEMS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM batch_task_items;" 2>/dev/null || echo "0")
NEW_SIZE=$(du -h $DB_PATH | cut -f1)

echo "technical_indicator_history: $NEW_TOTAL_TECH 行 (删除 $((TOTAL_TECH - NEW_TOTAL_TECH)) 行)"
echo "batch_task_items: $NEW_TOTAL_ITEMS 行 (删除 $((TOTAL_ITEMS - NEW_TOTAL_ITEMS)) 行)"
echo ""
echo -e "${GREEN}✅ 清理完成！${NC}"
echo "数据库大小: $NEW_SIZE"
echo "备份位置: $BACKUP_FILE"
