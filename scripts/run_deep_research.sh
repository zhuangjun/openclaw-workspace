#!/bin/bash
# Deep Research 任务执行脚本
# 由守护程序调度执行

TASK_NAME="${1:-Deep Research任务}"
TARGET_ID="${2:-}"
TIMEOUT="${3:-1200}"  # 默认20分钟
OUTPUT_DIR="${4:-./reports}"

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="$OUTPUT_DIR/$(echo "$TASK_NAME" | tr ' ' '_')_$(date +%Y%m%d_%H%M).md"
LOG_FILE="./logs/research_$(date +%Y%m%d_%H%M).log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "🔬 开始 Deep Research: $TASK_NAME"
echo "   时间: $(date)"
echo "   超时: ${TIMEOUT}秒"
echo "   输出: $OUTPUT_FILE"
echo ""

# 如果没有提供 targetId，尝试获取
echo "🔍 检查浏览器连接..."
if [ -z "$TARGET_ID" ]; then
    # 尝试获取现有的 Gemini 标签页
    TARGET_ID=$(browser tabs 2>/dev/null | grep -o '"targetId": "[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -z "$TARGET_ID" ]; then
        echo "❌ 错误: 没有可用的浏览器标签页"
        echo "   请先连接 Chrome 扩展"
        exit 1
    fi
    echo "✅ 使用标签页: $TARGET_ID"
fi

# 检查标签页是否可用
echo "🔍 验证标签页..."
if ! browser snapshot --targetId="$TARGET_ID" --refs=aria --limit=100 > /dev/null 2>&1; then
    echo "❌ 错误: 无法连接到标签页"
    exit 1
fi
echo "✅ 标签页连接正常"
echo ""

# 开始轮询监控
echo "⏳ 开始轮询监控..."
INTERVAL=10
ELAPSED=0
COMPLETED=false

while [ $ELAPSED -lt $TIMEOUT ]; do
    # 获取当前状态
    STATUS=$(browser snapshot --targetId="$TARGET_ID" --refs=aria --limit=500 2>/dev/null | grep -o '"已完成"\|"分析结果中"\|"正在研究"\|"Researching websites"' | head -1 || echo "")
    
    CURRENT_TIME=$(date '+%H:%M:%S')
    
    if echo "$STATUS" | grep -q "已完成"; then
        echo ""
        echo "✅ [$CURRENT_TIME] 研究已完成！耗时 ${ELAPSED}秒"
        COMPLETED=true
        break
    elif echo "$STATUS" | grep -q "分析结果中"; then
        echo "⏳ [$CURRENT_TIME] 分析结果中... (${ELAPSED}s)"
    elif echo "$STATUS" | grep -q "正在研究\|Researching"; then
        echo "🔍 [$CURRENT_TIME] 研究中... (${ELAPSED}s)"
    else
        echo "🤔 [$CURRENT_TIME] 状态未知 (${ELAPSED}s)"
    fi
    
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ "$COMPLETED" != "true" ]; then
    echo ""
    echo "⏰ 超时！(${TIMEOUT}秒)"
    echo "⚠️ 研究未在预期时间内完成"
fi

# 保存结果
echo ""
echo "💾 正在保存结果..."
browser snapshot --targetId="$TARGET_ID" --refs=aria --limit=10000 > "$OUTPUT_FILE" 2>/dev/null

if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(wc -c < "$OUTPUT_FILE")
    echo "✅ 结果已保存: $OUTPUT_FILE (${FILE_SIZE} 字节)"
    
    # 发送通知 (如果配置了 Telegram)
    if command -v message >/dev/null 2>&1; then
        echo "📤 发送通知..."
        message send --target="telegram" --message="✅ $TASK_NAME 完成！\n📄 结果: $OUTPUT_FILE\n⏱️ 耗时: ${ELAPSED}秒" 2>/dev/null || true
    fi
    
    exit 0
else
    echo "❌ 保存失败"
    exit 1
fi
