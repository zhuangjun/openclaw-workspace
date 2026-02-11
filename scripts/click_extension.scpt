#!/usr/bin/osascript
-- 自动点击 Chrome 扩展图标的 AppleScript

on run
    tell application "Google Chrome"
        activate
        delay 1
    end tell
    
    -- 尝试点击菜单栏的 OpenClaw 图标
    -- 注意：需要知道图标的准确位置或使用辅助功能
    
    tell application "System Events"
        tell process "Google Chrome"
            -- 尝试找到扩展按钮（可能需要根据实际 UI 调整）
            try
                click menu bar item 1 of menu bar 2
                display notification "已尝试点击扩展" with title "OpenClaw"
            on error
                display notification "无法找到扩展图标，请手动点击" with title "OpenClaw"
            end try
        end tell
    end tell
end run
