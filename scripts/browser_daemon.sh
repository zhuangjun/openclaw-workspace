#!/bin/bash
# OpenClaw 浏览器守护程序
# 功能：监控浏览器连接状态，自动重连，执行任务队列

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$WORKSPACE_DIR/logs/browser_daemon.log"
QUEUE_FILE="$WORKSPACE_DIR/.task_queue"
PID_FILE="$WORKSPACE_DIR/.browser_daemon.pid"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查是否已在运行
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "⚠️ 守护程序已在运行 (PID: $pid)"
            exit 1
        fi
    fi
    echo $$ > "$PID_FILE"
}

# 检查浏览器状态
check_browser() {
    # 使用浏览器状态检查
    local status=$(browser status 2>/dev/null | grep -o '"running": true' || echo "")
    if [ -n "$status" ]; then
        return 0  # 运行中
    else
        return 1  # 未运行
    fi
}

# 尝试启动浏览器
start_browser() {
    log "🚀 尝试启动浏览器..."
    browser start 2>/dev/null &
    sleep 3
    
    if check_browser; then
        log "✅ 浏览器启动成功"
        return 0
    else
        log "❌ 浏览器启动失败，需要手动连接 Chrome 扩展"
        return 1
    fi
}

# 检查 Chrome 扩展连接
check_extension() {
    # 尝试获取标签页列表
    local tabs=$(browser tabs 2>/dev/null | grep -o '"targetId"' | head -1 || echo "")
    if [ -n "$tabs" ]; then
        return 0  # 扩展已连接
    else
        return 1  # 扩展未连接
    fi
}

# 执行任务
execute_task() {
    local task_file="$1"
    local task_name=$(basename "$task_file")
    
    log "▶️ 执行任务: $task_name"
    
    # 执行脚本
    if bash "$task_file" >> "$LOG_FILE" 2>&1; then
        log "✅ 任务完成: $task_name"
        rm -f "$task_file"
        return 0
    else
        log "❌ 任务失败: $task_name"
        return 1
    fi
}

# 检查任务队列
process_queue() {
    if [ -f "$QUEUE_FILE" ] && [ -s "$QUEUE_FILE" ]; then
        log "📋 发现任务队列"
        
        # 检查浏览器和扩展
        if ! check_browser; then
            start_browser || return 1
        fi
        
        if ! check_extension; then
            log "⏳ 等待 Chrome 扩展连接..."
            # 扩展需要手动连接，记录等待
            return 1
        fi
        
        # 处理队列中的任务
        while IFS= read -r task_file; do
            [ -f "$task_file" ] && execute_task "$task_file"
        done < "$QUEUE_FILE"
        
        # 清空队列
        > "$QUEUE_FILE"
    fi
}

# 添加任务到队列
queue_task() {
    local task_script="$1"
    echo "$task_script" >> "$QUEUE_FILE"
    log "📥 任务已加入队列: $(basename "$task_script")"
}

# 主循环
main_loop() {
    log "🤖 浏览器守护程序启动"
    log "   日志: $LOG_FILE"
    log "   队列: $QUEUE_FILE"
    
    while true; do
        # 1. 检查浏览器状态
        if ! check_browser; then
            log "⚠️ 浏览器未运行"
            start_browser
        fi
        
        # 2. 检查扩展连接
        if check_extension; then
            log "✅ 浏览器和扩展都正常"
            # 处理队列
            process_queue
        else
            log "⏳ 等待 Chrome 扩展手动连接..."
            log "   请点击 Chrome 工具栏上的 OpenClaw 图标"
        fi
        
        # 3. 每分钟检查一次
        sleep 60
    done
}

# 清理函数
cleanup() {
    log "🛑 守护程序停止"
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 命令行参数处理
case "${1:-}" in
    start)
        check_running
        main_loop
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            kill "$(cat "$PID_FILE")" 2>/dev/null
            rm -f "$PID_FILE"
            log "🛑 守护程序已停止"
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE")" > /dev/null 2>&1; then
            log "✅ 守护程序运行中 (PID: $(cat "$PID_FILE"))"
            check_browser && log "✅ 浏览器运行中" || log "❌ 浏览器未运行"
            check_extension && log "✅ 扩展已连接" || log "⏳ 扩展未连接"
        else
            log "❌ 守护程序未运行"
        fi
        ;;
    queue)
        shift
        queue_task "$1"
        ;;
    *)
        echo "用法: $0 {start|stop|status|queue <script>}"
        exit 1
        ;;
esac
