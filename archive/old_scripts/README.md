# 归档脚本说明

## 归档时间
2026-02-10

## 归档原因
这些脚本包含错误的 API 端点配置或已被新版替代。

## 已归档脚本列表

### 晨报推送相关（已废弃）
- `push_daily_report.py` - 使用错误的 API 端点 `/api/cron-results`
- `daily_market_report_task.py` - v1 版本
- `daily_market_report_task_v2.py` - v2 版本
- `daily_market_report_task_v3.py` - v3 版本

### 比特币追踪相关（已废弃）
- `bitcoin_tracker_task.py` - v1 版本
- `bitcoin_tracker_task_v2.py` - v2 版本

### 戴维斯双击扫描（已废弃）
- `davis_double_scan_task.py` - v1 版本
- `davis_double_scan_task_v2.py` - v2 版本

### 其他（已废弃）
- `cron_task_result_fixed.py` - 旧版任务结果处理
- `cron_task_results_api.py` - 旧版 API 客户端
- `execute_all_tasks.py` - 旧版任务执行器

## 当前有效脚本位置

### 根目录保留的脚本
- `push_morning_report.py` - ✅ 新版晨报推送脚本（使用正确 API）
- `task_result_client.py` - ✅ 修复后的任务结果客户端
- `btc_realtime_tracker.py` - 比特币实时追踪

### 其他有效文件
- `HEARTBEAT.md` - 股市晨报监控配置
- `SOUL.md` - AI 人设配置
- `TOOLS.md` - 工具配置
- `USER.md` - 用户信息

## 正确 API 端点
```
https://danielzhuang.xyz/Friday/api/tasks/results/save
```

## 注意事项
如需恢复某个归档脚本，请先检查其 API 端点配置是否正确。
