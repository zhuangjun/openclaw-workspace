# OpenClaw Browser Relay 自动修复方案

## 问题描述
Chrome 扩展虽然显示 "ON"，但当浏览器重启或扩展重新加载后，需要手动点击扩展图标来连接当前 tab。之前的定时任务只是发送通知，没有实际执行修复。

## 解决方案

### 方案一：自动执行修复脚本（已实施）

**修复脚本**: `/Users/daniel/ensure-openclaw-stable.sh`

功能：
- 检查 OpenClaw 网关状态
- 如果网关未运行则自动启动
- 记录日志到 `/tmp/openclaw-browser-fix.log`
- 自动清理7天前的日志

**定时任务**: 每5分钟执行一次
- 使用 isolated session 运行
- 不发送通知（mode: none）
- 执行修复脚本并检查状态

**查看日志**:
```bash
tail -20 /tmp/openclaw-browser-fix.log
```

### 方案二：开机自启 + 浏览器自动连接（待实施）

**步骤**:
1. 配置 Chrome 开机自启
2. 配置 OpenClaw 网关开机自启
3. 创建 AppleScript 自动点击 Chrome 扩展图标
4. 配置定时任务检查连接状态

### 方案三：使用 headless 浏览器（备选）

如果需要完全自动化，可以考虑：
- 使用 Playwright 或 Puppeteer 启动 headless Chrome
- 避免扩展连接问题
- 但需要单独配置和测试

## 注意事项

1. **Chrome 扩展连接仍需手动**: 目前的脚本只能确保网关和浏览器在运行，但扩展与特定 tab 的连接仍需用户手动点击扩展图标
2. **长期方案**: 考虑使用 headless 浏览器模式实现完全自动化
3. **监控**: 定期检查 `/tmp/openclaw-browser-fix.log` 确保修复脚本正常工作

## 更新记录

- 2026-02-19: 创建修复脚本并更新定时任务
