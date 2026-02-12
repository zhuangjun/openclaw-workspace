#!/bin/bash
# OpenClaw 扩展自动连接脚本
# 自动将 Browser Relay 扩展设置为 ON

LOG_FILE="$HOME/.openclaw-auto-connect.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== 开始自动连接流程 ==="

# 步骤1: 确保 Gateway 运行
if ! pgrep -x "openclaw-gateway" > /dev/null; then
    log "启动 openclaw-gateway..."
    openclaw gateway start &
    sleep 3
fi

# 步骤2: 确保 Chrome 运行
if ! pgrep -x "Google Chrome" > /dev/null; then
    log "启动 Chrome..."
    open -a "Google Chrome"
    sleep 5
fi

# 步骤3: 激活 Chrome 并尝试连接
log "激活 Chrome..."

# 方法A: 激活 Gemini 标签页（如果有）
python3 << 'PYTHON_SCRIPT'
import subprocess
import json
import time

# 尝试通过 CDP 获取 Chrome 状态
try:
    result = subprocess.run(
        ['curl', '-s', 'http://localhost:18792/json/list'],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        tabs = json.loads(result.stdout)
        gemini_tabs = [t for t in tabs if 'gemini.google.com' in t.get('url', '')]
        if gemini_tabs:
            print(f"找到 {len(gemini_tabs)} 个 Gemini 标签页")
        else:
            print("未找到 Gemini 标签页")
    else:
        print("无法连接到 Gateway")
except Exception as e:
    print(f"检查失败: {e}")
PYTHON_SCRIPT

# 方法B: 使用 AppleScript 强制激活
osascript << 'APPLESCRIPT' 2>&1 | while read line; do log "$line"; done
tell application "Google Chrome"
    activate
    delay 0.5
    
    -- 尝试激活一个网页标签
    try
        set frontWindow to front window
        set active tab index of frontWindow to 1
    end try
end tell

tell application "System Events"
    tell process "Google Chrome"
        -- 尝试点击扩展区域（通常在地址栏右侧）
        try
            -- 获取工具栏所有按钮
            set toolbarButtons to buttons of toolbar 1 of front window
            set buttonCount to count of toolbarButtons
            
            -- 尝试点击最后几个按钮（扩展通常在右边）
            if buttonCount > 3 then
                repeat with i from (buttonCount - 2) to buttonCount
                    try
                        set btn to item i of toolbarButtons
                        click btn
                        delay 0.2
                    end try
                end repeat
            end if
        end try
        
        -- 尝试按 Command+Shift+L（如果扩展设置了此快捷键）
        -- keystroke "l" using {command down, shift down}
    end tell
end tell

return "激活完成"
APPLESCRIPT

# 步骤4: 检查连接状态
log "检查连接状态..."
sleep 2

# 尝试通过 Gateway 测试连接
if curl -s http://localhost:18792/json/version 2>/dev/null | grep -q "Browser"; then
    log "✅ Gateway 连接正常"
else
    log "⚠️ Gateway 可能未完全就绪"
fi

# 步骤5: 如果 Chrome 控制服务在运行，也保持它活跃
if [ -f "$HOME/.openclaw-control.pid" ]; then
    CONTROL_PID=$(cat "$HOME/.openclaw-control.pid")
    if ps -p "$CONTROL_PID" > /dev/null 2>&1; then
        log "✅ openclaw-control 运行中 (PID: $CONTROL_PID)"
    fi
fi

log "=== 自动连接流程完成 ==="
log ""
