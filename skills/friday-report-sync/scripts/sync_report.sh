#!/bin/bash
# Friday Report Sync v2.0 - API 驱动的报告同步
# 用法: sync_report.sh [报告md文件路径] [报告类型] [报告标题] [报告日期]

set -e

# 默认配置
API_BASE="${FRIDAY_API_URL:-https://danielzhuang.xyz/Friday/api}"
API_TOKEN="${FRIDAY_API_TOKEN:-dev-token-change-in-production}"
REPORTS_DIR="${FRIDAY_REPORTS_DIR:-/Users/daniel/.openclaw/workspace/investment/reports}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 显示帮助
show_help() {
    cat << EOF
Friday Report Sync v2.0 - API驱动的报告同步工具

用法:
  $0 [选项] <报告文件.md> [类型] [标题] [日期]

参数:
  报告文件.md    Markdown报告文件路径
  类型           报告分类 (investment_logic, davis_double, morning_brief, us_main_theme, dcf_valuation, etc.)
  标题           报告标题（可选，默认从文件名提取）
  日期           报告日期 YYYY-MM-DD（可选，默认从文件名提取或今天）

选项:
  -h, --help     显示帮助信息
  -d, --dry-run  试运行，不实际提交
  -v, --verbose  详细输出

环境变量:
  FRIDAY_API_URL      API基础URL (默认: https://danielzhuang.xyz/api)
  FRIDAY_API_TOKEN    API鉴权Token
  FRIDAY_REPORTS_DIR  报告文件目录

示例:
  $0 ./investment_logic_2026-02-12.md investment_logic
  $0 ./davis_double_2026-02-12.md davis_double "戴维斯双击扫描" 2026-02-12

EOF
}

# 解析参数
DRY_RUN=false
VERBOSE=false
FILE_PATH=""
CATEGORY=""
TITLE=""
DATE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            show_help
            exit 1
            ;;
        *)
            if [[ -z "$FILE_PATH" ]]; then
                FILE_PATH="$1"
            elif [[ -z "$CATEGORY" ]]; then
                CATEGORY="$1"
            elif [[ -z "$TITLE" ]]; then
                TITLE="$1"
            elif [[ -z "$DATE" ]]; then
                DATE="$1"
            fi
            shift
            ;;
    esac
done

# 验证必填参数
if [[ -z "$FILE_PATH" ]]; then
    echo -e "${RED}❌ 错误: 请指定报告文件路径${NC}"
    show_help
    exit 1
fi

if [[ ! -f "$FILE_PATH" ]]; then
    echo -e "${RED}❌ 错误: 文件不存在: $FILE_PATH${NC}"
    exit 1
fi

# 自动检测类别（如果未指定）
if [[ -z "$CATEGORY" ]]; then
    FILENAME=$(basename "$FILE_PATH")
    if [[ "$FILENAME" == *"investment_logic"* ]]; then
        CATEGORY="investment_logic"
    elif [[ "$FILENAME" == *"davis_double"* ]]; then
        CATEGORY="davis_double"
    elif [[ "$FILENAME" == *"morning"* ]] || [[ "$FILENAME" == *"brief"* ]]; then
        CATEGORY="morning_brief"
    elif [[ "$FILENAME" == *"main_theme"* ]] || [[ "$FILENAME" == *"us_stock"* ]]; then
        CATEGORY="us_main_theme"
    elif [[ "$FILENAME" == *"dcf"* ]] || [[ "$FILENAME" == *"valuation"* ]]; then
        CATEGORY="dcf_valuation"
    elif [[ "$FILENAME" == *"gold"* ]]; then
        CATEGORY="gold_analysis"
    elif [[ "$FILENAME" == *"crypto"* ]] || [[ "$FILENAME" == *"bitcoin"* ]]; then
        CATEGORY="crypto_analysis"
    elif [[ "$FILENAME" == *"a_stock"* ]]; then
        CATEGORY="a_stock_scan"
    else
        CATEGORY="general"
    fi
    echo -e "${YELLOW}⚠️  未指定类别，自动检测为: $CATEGORY${NC}"
fi

# 自动提取日期（如果未指定）
if [[ -z "$DATE" ]]; then
    FILENAME=$(basename "$FILE_PATH")
    # 尝试从文件名提取日期 (YYYY-MM-DD 或 YYYYMMDD)
    if [[ "$FILENAME" =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
        DATE="${BASH_REMATCH[1]}"
    elif [[ "$FILENAME" =~ ([0-9]{8}) ]]; then
        DATE="${BASH_REMATCH[1]:0:4}-${BASH_REMATCH[1]:4:2}-${BASH_REMATCH[1]:6:2}"
    else
        DATE=$(date +%Y-%m-%d)
    fi
    echo -e "${YELLOW}⚠️  未指定日期，自动检测为: $DATE${NC}"
fi

# 自动提取标题（如果未指定）
if [[ -z "$TITLE" ]]; then
    # 尝试从文件第一行提取标题 (# 开头的markdown标题)
    FIRST_LINE=$(head -1 "$FILE_PATH")
    if [[ "$FIRST_LINE" == \#* ]]; then
        TITLE=$(echo "$FIRST_LINE" | sed 's/^#\s*//')
    else
        # 从文件名生成标题
        BASENAME=$(basename "$FILE_PATH" .md)
        TITLE=$(echo "$BASENAME" | sed 's/[_-]/ /g' | sed 's/\b\w/\u&/g')
    fi
fi

echo -e "${BLUE}📊 Friday Report Sync v2.0${NC}"
echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
echo "📄 文件: $FILE_PATH"
echo "🏷️  类别: $CATEGORY"
echo "📅 日期: $DATE"
echo "📝 标题: $TITLE"
echo "🌐 API: $API_BASE"
echo ""

# 读取文件内容
CONTENT=$(cat "$FILE_PATH")
FILE_SIZE=$(stat -f%z "$FILE_PATH" 2>/dev/null || stat -c%s "$FILE_PATH" 2>/dev/null || echo "0")

echo -e "${BLUE}📋 文件信息:${NC}"
echo "   大小: $(numfmt --to=iec $FILE_SIZE 2>/dev/null || echo "${FILE_SIZE} bytes")"
echo "   行数: $(wc -l < "$FILE_PATH")"
echo ""

# 构建JSON数据
# 提取摘要（前500字符，去掉markdown标记）
SUMMARY=$(echo "$CONTENT" | sed 's/#//g' | sed 's/\*\*//g' | tr '\n' ' ' | cut -c1-500)

# 生成文件名（用于向后兼容）
FILE_NAME=$(basename "$FILE_PATH")

# 构建JSON
JSON_DATA=$(cat <<EOF
{
    "title": $(echo "$TITLE" | jq -Rs '.'),
    "category": "$CATEGORY",
    "report_date": "$DATE",
    "content_md": $(echo "$CONTENT" | jq -Rs '.'),
    "summary": $(echo "$SUMMARY..." | jq -Rs '.'),
    "source": "gemini-deep-research",
    "author": "Friday AI",
    "file_name": "$FILE_NAME",
    "status": "published"
}
EOF
)

if [[ "$VERBOSE" == true ]]; then
    echo -e "${BLUE}📤 请求数据:${NC}"
    echo "$JSON_DATA" | head -20
    echo ""
fi

if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}🏃 试运行模式，不实际提交${NC}"
    echo "$JSON_DATA"
    exit 0
fi

# 调用API同步报告
echo -e "${YELLOW}📤 正在同步到数据库...${NC}"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/reports" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_TOKEN" \
    -d "$JSON_DATA" 2>&1) || {
    echo -e "${RED}❌ 网络请求失败${NC}"
    echo "错误信息: $RESPONSE"
    exit 1
}

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$VERBOSE" == true ]]; then
    echo -e "${BLUE}📥 响应 (HTTP $HTTP_CODE):${NC}"
    echo "$BODY"
    echo ""
fi

if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "201" ]]; then
    ACTION=$(echo "$BODY" | jq -r '.action // "unknown"' 2>/dev/null)
    REPORT_ID=$(echo "$BODY" | jq -r '.id // "unknown"' 2>/dev/null)
    
    if [[ "$ACTION" == "updated" ]]; then
        echo -e "${GREEN}✅ 报告已更新 (ID: $REPORT_ID)${NC}"
    else
        echo -e "${GREEN}✅ 报告已创建 (ID: $REPORT_ID)${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 同步完成!${NC}"
    echo -e "🌐 访问地址: ${BLUE}https://danielzhuang.xyz/Friday/reports/${NC}"
    exit 0
else
    echo -e "${RED}❌ 同步失败 (HTTP $HTTP_CODE)${NC}"
    echo "响应: $BODY"
    exit 1
fi
