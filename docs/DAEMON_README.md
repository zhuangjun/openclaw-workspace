# OpenClaw 浏览器守护程序

自动监控浏览器连接，执行任务队列，处理 Deep Research 流程。

## 文件说明

| 文件 | 用途 |
|------|------|
| `browser_daemon.sh` | 守护程序主脚本 |
| `run_deep_research.sh` | Deep Research 任务执行器 |
| `monitor_deep_research.sh` | 独立的监控脚本 |
| `simple_test.sh` | 简单测试脚本 |

## 使用方法

### 1. 启动守护程序

```bash
./scripts/browser_daemon.sh start
```

守护程序会在后台运行，每分钟检查：
- 浏览器是否运行
- Chrome 扩展是否连接
- 是否有待执行的任务队列

### 2. 查看状态

```bash
./scripts/browser_daemon.sh status
```

### 3. 停止守护程序

```bash
./scripts/browser_daemon.sh stop
```

### 4. 添加任务到队列

```bash
./scripts/browser_daemon.sh queue ./scripts/run_deep_research.sh
```

当浏览器扩展连接后，守护程序会自动执行任务。

## 自动执行 Deep Research（手动触发）

如果守护程序已运行且扩展已连接：

```bash
./scripts/run_deep_research.sh "投资逻辑分析" <targetId> 1200 ./reports
```

参数：
- `$1` - 任务名称
- `$2` - 浏览器标签页 ID（可选，自动检测）
- `$3` - 超时秒数（默认 1200 = 20分钟）
- `$4` - 输出目录（默认 ./reports）

## Cron 自动调度

已配置的定时任务：

| 时间 | 任务 |
|------|------|
| 05:00 | 投资逻辑分析 |
| 05:30 | 戴维斯双击扫描 |
| 06:00 | 股市综合晨报 |
| 06:30 | 美股主线标的 |

**关键**：确保在 05:00 前 Chrome 扩展已连接，否则任务会进入队列等待。

## 日志位置

```
logs/
├── browser_daemon.log    # 守护程序日志
├── research_YYYYMMDD.log  # 研究任务日志
└── app.log               # 应用日志
```

## 一键启动命令

```bash
# 1. 启动守护程序
./scripts/browser_daemon.sh start

# 2. 在 Chrome 中点击 OpenClaw 图标连接扩展

# 3. 等待连接成功后，守护程序会自动处理队列

# 4. 明天早上任务会自动执行
```

## 手动测试流程

```bash
# 测试简单任务
./scripts/simple_test.sh ./test_output.txt 30

# 测试 Deep Research（需要扩展已连接）
./scripts/run_deep_research.sh "测试任务" "" 1200 ./reports
```

## 故障排查

**问题**: 守护程序显示"等待 Chrome 扩展手动连接"
**解决**: 打开 Chrome → 点击工具栏 OpenClaw 图标 → 确认状态为 ON

**问题**: 任务超时
**解决**: 检查网络连接，或增加超时时间参数

**问题**: 结果保存失败
**解决**: 检查 reports/ 目录是否存在且有写入权限
