#!/bin/bash
# Friday Database Cleanup Script
# 清理 scheduler_logs 和 batch_task_logs 表的一周前数据
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

echo -e "${BLUE}📊 Friday 数据库清理脚本${NC}"
echo "=================================="
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

# scheduler_logs 统计
echo -e "\n${BLUE}表: scheduler_logs${NC}"
TOTAL_SCHEDULER=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM scheduler_logs;" 2>/dev/null || echo "0")
OLD_SCHEDULER=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM scheduler_logs WHERE timestamp < datetime('now', '-$DAYS_TO_KEEP days');" 2>/dev/null || echo "0")
TO_KEEP_SCHEDULER=$((TOTAL_SCHEDULER - OLD_SCHEDULER))
echo "  总行数: $TOTAL_SCHEDULER"
echo "  一周前数据: $OLD_SCHEDULER"
echo "  将保留: $TO_KEEP_SCHEDULER"

# batch_task_logs 统计
echo -e "\n${BLUE}表: batch_task_logs${NC}"
TOTAL_BATCH=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM batch_task_logs;" 2>/dev/null || echo "0")
OLD_BATCH=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM batch_task_logs WHERE timestamp < datetime('now', '-$DAYS_TO_KEEP days');" 2>/dev/null || echo "0")
TO_KEEP_BATCH=$((TOTAL_BATCH - OLD_BATCH))
echo "  总行数: $TOTAL_BATCH"
echo "  一周前数据: $OLD_BATCH"
echo "  将保留: $TO_KEEP_BATCH"

echo ""
echo -e "${YELLOW}⚠️  将要删除的数据:${NC}"
echo "  scheduler_logs: $OLD_SCHEDULER 行"
echo "  batch_task_logs: $OLD_BATCH 行"
echo "  合计: $((OLD_SCHEDULER + OLD_BATCH)) 行"
echo ""

# 试运行模式
if [ "$DRY_RUN" == "--dry-run" ]; then
    echo -e "${YELLOW}🔍 试运行模式 - 不会实际删除数据${NC}"
    echo -e "${GREEN}如需执行清理，请运行: $0 $DB_PATH --execute${NC}"
    echo ""
    echo -e "${YELLOW}📋 将执行的 SQL 语句预览:${NC}"
    echo ""
    echo "-- 清理 scheduler_logs"
    echo "DELETE FROM scheduler_logs WHERE created_at < datetime('now', '-$DAYS_TO_KEEP days');"
    echo ""
    echo "-- 清理 batch_task_logs"  
    echo "DELETE FROM batch_task_logs WHERE created_at < datetime('now', '-$DAYS_TO_KEEP days');"
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
echo -e "${RED}这将删除 $((OLD_SCHEDULER + OLD_BATCH)) 行数据，且不可恢复！${NC}"
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
BACKUP_FILE="/home/ubuntu/db_backup/stock_analyzer_pre_cleanup_$(date +%Y%m%d_%H%M%S).db"
cp "$DB_PATH" "$BACKUP_FILE"
echo -e "${GREEN}✅ 备份已创建: $BACKUP_FILE${NC}"
echo ""

# 执行清理
echo -e "${BLUE}🗑️  清理 scheduler_logs...${NC}"
sqlite3 "$DB_PATH" "DELETE FROM scheduler_logs WHERE timestamp < datetime('now', '-$DAYS_TO_KEEP days');"
SCHEDULER_DELETED=$?

if [ $SCHEDULER_DELETED -eq 0 ]; then
    echo -e "${GREEN}✅ scheduler_logs 清理完成${NC}"
else
    echo -e "${RED}❌ scheduler_logs 清理失败${NC}"
fi

echo ""
echo -e "${BLUE}🗑️  清理 batch_task_logs...${NC}"
sqlite3 "$DB_PATH" "DELETE FROM batch_task_logs WHERE timestamp < datetime('now', '-$DAYS_TO_KEEP days');"
BATCH_DELETED=$?

if [ $BATCH_DELETED -eq 0 ]; then
    echo -e "${GREEN}✅ batch_task_logs 清理完成${NC}"
else
    echo -e "${RED}❌ batch_task_logs 清理失败${NC}"
fi

# 执行 VACUUM 回收空间
echo ""
echo -e "${BLUE}🧹 执行 VACUUM 回收空间...${NC}"
sqlite3 "$DB_PATH" "VACUUM;"
echo -e "${GREEN}✅ VACUUM 完成${NC}"

# 统计清理后的数据
echo ""
echo -e "${YELLOW}📊 清理后统计:${NC}"
NEW_TOTAL_SCHEDULER=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM scheduler_logs;" 2>/dev/null || echo "0")
NEW_TOTAL_BATCH=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM batch_task_logs;" 2>/dev/null || echo "0")
NEW_SIZE=$(du -h $DB_PATH | cut -f1)

echo "scheduler_logs: $NEW_TOTAL_SCHEDULER 行 (删除 $((TOTAL_SCHEDULER - NEW_TOTAL_SCHEDULER)) 行)"
echo "batch_task_logs: $NEW_TOTAL_BATCH 行 (删除 $((TOTAL_BATCH - NEW_TOTAL_BATCH)) 行)"
echo ""
echo -e "${GREEN}✅ 清理完成！${NC}"
echo "数据库大小: $NEW_SIZE"
echo "备份位置: $BACKUP_FILE"
