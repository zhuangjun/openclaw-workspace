#!/bin/bash
# OpenClaw 稳定运行方案 - 确保 Browser Relay 扩展保持连接
# 使用方法: ./ensure-openclaw-stable.sh

echo "🔧 OpenClaw 稳定性检查与修复"
echo "================================"
echo ""

# 1. 检查 openclaw-gateway 状态
echo "1️⃣ 检查 OpenClaw Gateway..."
if pgrep -x "openclaw-gateway" > /dev/null; then
    echo "   ✅ openclaw-gateway 正在运行"
else
    echo "   ❌ openclaw-gateway 未运行，正在启动..."
    openclaw gateway start &
    sleep 3
fi

# 2. 检查 openclaw-control 守护进程
echo ""
echo "2️⃣ 检查 Chrome 保持活跃服务..."
if [ -f "$HOME/.openclaw-control.pid" ]; then
    PID=$(cat "$HOME/.openclaw-control.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "   ✅ openclaw-control 正在运行 (PID: $PID)"
    else
        echo "   ❌ openclaw-control 进程已失效，重启中..."
        rm -f "$HOME/.openclaw-control.pid"
        $HOME/openclaw-control.sh daemon
        sleep 2
    fi
else
    echo "   ❌ openclaw-control 未运行，启动中..."
    $HOME/openclaw-control.sh daemon
    sleep 2
fi

# 3. 检查 caffeinate 防止休眠
echo ""
echo "3️⃣ 检查系统休眠阻止..."
if pgrep -f "caffeinate -dimsu" > /dev/null; then
    echo "   ✅ caffeinate 正在运行（防止系统休眠）"
else
    echo "   ❌ caffeinate 未运行，启动中..."
    caffeinate -dimsu &
    echo $! > "$HOME/.caffeinate.pid"
    echo "   ✅ caffeinate 已启动"
fi

# 4. 检查 Chrome 是否运行
echo ""
echo "4️⃣ 检查 Chrome 浏览器..."
if pgrep -x "Google Chrome" > /dev/null; then
    echo "   ✅ Chrome 正在运行"
    
    # 获取 Chrome 的窗口状态
    CHROME_WINDOW=$(osascript -e 'tell application "System Events" to tell process "Google Chrome" to get visible of front window' 2>/dev/null)
    if [ "$CHROME_WINDOW" = "true" ]; then
        echo "   ✅ Chrome 窗口可见"
    else
        echo "   ⚠️  Chrome 窗口可能被隐藏，尝试激活..."
        osascript -e 'tell application "Google Chrome" to activate' 2>/dev/null
    fi
else
    echo "   ❌ Chrome 未运行，正在启动..."
    open -a "Google Chrome"
    sleep 5
    echo "   ✅ Chrome 已启动"
fi

# 5. 自动设置扩展为 ON
echo ""
echo "5️⃣ 自动设置扩展为 ON..."

# 5.1 首先激活 Chrome
osascript -e 'tell application "Google Chrome" to activate' 2>/dev/null
sleep 0.5

# 5.2 尝试通过多种方法激活扩展
osascript << 'APPLESCRIPT' 2>/dev/null
tell application "Google Chrome"
    activate
    delay 0.3
    
    -- 尝试激活 Gemini 标签页（如果存在）
    set geminiFound to false
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "gemini.google.com" then
                set active tab index of w to index of t
                set index of w to 1
                set geminiFound to true
                exit repeat
            end if
        end repeat
        if geminiFound then exit repeat
    end repeat
    
    -- 如果没有 Gemini 标签，确保至少有一个标签被激活
    if not geminiFound then
        try
            set frontWindow to front window
            set active tab index of frontWindow to 1
        end try
    end if
end tell

tell application "System Events"
    tell process "Google Chrome"
        -- 方法1: 尝试点击工具栏右侧的扩展按钮区域
        try
            set toolbarButtons to buttons of toolbar 1 of front window
            set btnCount to count of toolbarButtons
            
            -- 点击最后2-3个按钮（扩展通常在右侧）
            if btnCount > 2 then
                set startIdx to btnCount - 2
                if startIdx < 1 then set startIdx to 1
                
                repeat with i from startIdx to btnCount
                    try
                        click (item i of toolbarButtons)
                        delay 0.15
                    end try
                end repeat
            end if
        end try
        
        -- 方法2: 尝试点击特定位置的按钮（扩展图标通常在地址栏右侧）
        try
            -- 获取窗口大小，计算扩展图标可能的位置
            set winPos to position of front window
            set winSize to size of front window
            set winWidth to item 1 of winSize
            
            -- 扩展图标通常在窗口右上角附近
            -- 这个位置需要根据实际屏幕分辨率调整
            if winWidth > 800 then
                -- 尝试点击右上角区域
                click at {winWidth - 150, 75}
                delay 0.15
            end if
        end try
    end tell
end tell

return "扩展激活尝试完成"
APPLESCRIPT

# 5.3 等待连接建立
sleep 2

# 5.4 测试 Gateway 连接
echo "   测试 Gateway 连接..."
if curl -s http://localhost:18792/json/list 2>/dev/null | grep -q "webSocketDebuggerUrl"; then
    echo "   ✅ Gateway 连接正常，扩展应该已自动连接"
else
    echo "   ⚠️  扩展可能仍处于 OFF 状态"
    echo "      如果 30 秒后仍为 OFF，请手动点击扩展图标"
fi

# 6. 显示状态总结
echo ""
echo "================================"
echo "📊 状态总结"
echo "================================"

# 检查 gateway 端口
if lsof -Pi :18792 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🟢 Gateway 端口 18792: 监听中"
else
    echo "🔴 Gateway 端口 18792: 未监听"
fi

# 检查日志
echo ""
if [ -f "$HOME/openclaw-control.log" ]; then
    echo "📋 最近心跳 (openclaw-control):"
    tail -3 "$HOME/openclaw-control.log"
fi

echo ""
echo "💡 提示:"
echo "   • 如果扩展仍显示 OFF，请手动点击 Chrome 工具栏的 OpenClaw 图标"
echo "   • 建议将扩展固定到工具栏便于查看状态"
echo "   • 夜间运行时保持 Mac 连接电源"
echo ""
echo "✅ 稳定性检查完成"
