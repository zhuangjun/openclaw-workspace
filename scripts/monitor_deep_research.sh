#!/bin/bash
# Deep Research 自动轮询监控脚本
# 用法: ./monitor_deep_research.sh <targetId> [timeout_seconds]

TARGET_ID="${1:-690CEE9C9711ED4CB79E4F811373FD06}"
TIMEOUT="${2:-1200}"  # 默认20分钟
OUTPUT_FILE="${3:-./deep_research_output.md}"

INTERVAL=10  # 每10秒检测一次
ELAPSED=0

echo "🔍 开始监控 Deep Research 进度..."
echo "   Target ID: $TARGET_ID"
echo "   超时设置: ${TIMEOUT}秒"
echo "   轮询间隔: ${INTERVAL}秒"
echo ""

while [ $ELAPSED -lt $TIMEOUT ]; do
    # 使用 browser snapshot 检查状态
    STATUS=$(browser snapshot --targetId="$TARGET_ID" --refs=aria --limit=1000 2>/dev/null | grep -o '"已完成"\|"分析结果中"\|"正在研究"\|"Researching websites"' | head -1)
    
    CURRENT_TIME=$(date '+%H:%M:%S')
    
    if echo "$STATUS" | grep -q "已完成"; then
        echo "✅ [$CURRENT_TIME] 研究已完成！耗时 ${ELAPSED}秒"
        
        # 获取完整结果
        echo "💾 正在保存结果到 $OUTPUT_FILE ..."
        browser snapshot --targetId="$TARGET_ID" --refs=aria --limit=10000 > "$OUTPUT_FILE" 2>/dev/null
        
        if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
            echo "✅ 结果已保存: $OUTPUT_FILE ($(wc -c < $OUTPUT_FILE) 字节)"
            exit 0
        else
            echo "⚠️ 保存失败，再试一次..."
            sleep 5
            browser snapshot --targetId="$TARGET_ID" --refs=aria --limit=10000 > "$OUTPUT_FILE" 2>/dev/null
        fi
        
        exit 0
    elif echo "$STATUS" | grep -q "分析结果中"; then
        echo "⏳ [$CURRENT_TIME] 分析结果中... (${ELAPSED}s elapsed)"
    elif echo "$STATUS" | grep -q "正在研究\|Researching"; then
        echo "🔍 [$CURRENT_TIME] 研究中... (${ELAPSED}s elapsed)"
    else
        echo "🤔 [$CURRENT_TIME] 状态未知，继续等待... (${ELAPSED}s elapsed)"
    fi
    
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

echo ""
echo "⏰ 超时！(${TIMEOUT}秒)"
echo "⚠️ Deep Research 未在预期时间内完成"
exit 1
