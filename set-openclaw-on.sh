#!/bin/bash
# 自动将 OpenClaw Browser Relay 扩展设置为 ON
# 使用方法: ./set-openclaw-on.sh

echo "🔌 尝试自动设置 OpenClaw 扩展为 ON..."

# 方法1: 通过 AppleScript 模拟点击扩展图标
osascript << 'APPLESCRIPT' 2>/dev/null
tell application "Google Chrome"
    activate
    delay 0.5
end tell

tell application "System Events"
    tell process "Google Chrome"
        -- 尝试找到 OpenClaw 扩展图标并点击
        -- 扩展图标通常在工具栏右侧
        set extFound to false
        
        -- 方法A: 尝试通过描述查找
        try
            click (first button of toolbar 1 of front window whose description contains "OpenClaw" or description contains "openclaw")
            set extFound to true
            delay 0.3
        end try
        
        -- 方法B: 如果找不到，尝试点击工具栏最后一个按钮（通常是扩展）
        if not extFound then
            try
                set allButtons to buttons of toolbar 1 of front window
                set lastButton to item -1 of allButtons
                click lastButton
                delay 0.3
            end try
        end if
        
        -- 尝试按快捷键打开扩展（如果扩展有设置快捷键）
        -- 注意：需要在 Chrome 扩展设置中为 OpenClaw 设置快捷键
    end tell
end tell

-- 方法2: 通过激活特定标签页来触发连接
tell application "Google Chrome"
    -- 如果有一个 Gemini 标签页，激活它
    set foundGemini to false
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "gemini.google.com" then
                set active tab index of w to index of t
                set index of w to 1
                set foundGemini to true
                exit repeat
            end if
        end repeat
        if foundGemini then exit repeat
    end repeat
    
    -- 如果没有 Gemini 标签，打开一个
    if not foundGemini then
        open location "https://gemini.google.com/app"
    end if
end tell

return "Chrome 已激活，扩展应该自动连接"
APPLESCRIPT

if [ $? -eq 0 ]; then
    echo "✅ 已尝试激活扩展"
else
    echo "⚠️ AppleScript 执行失败，尝试备用方法..."
fi

# 方法2: 通过刷新 Gateway 来触发重连
echo ""
echo "🔄 尝试刷新 Gateway 连接..."
curl -s http://localhost:18792/json/list 2>/dev/null | head -5 > /dev/null && echo "   ✅ Gateway 响应正常" || echo "   ⚠️ Gateway 可能未响应"

# 方法3: 检查扩展状态
echo ""
echo "📊 当前状态检查:"
if pgrep -x "openclaw-gateway" > /dev/null; then
    echo "   🟢 openclaw-gateway: 运行中"
else
    echo "   🔴 openclaw-gateway: 未运行"
    echo "   正在启动..."
    openclaw gateway start &
    sleep 2
fi

if pgrep -x "Google Chrome" > /dev/null; then
    echo "   🟢 Google Chrome: 运行中"
else
    echo "   🔴 Google Chrome: 未运行"
    echo "   正在启动..."
    open -a "Google Chrome"
    sleep 3
fi

echo ""
echo "💡 如果扩展仍显示 OFF，请尝试:"
echo "   1. 手动点击 Chrome 工具栏的 OpenClaw 图标"
echo "   2. 刷新当前网页"
echo "   3. 重启 Chrome 浏览器"
echo ""
echo "✅ 自动设置完成"
