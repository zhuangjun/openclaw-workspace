# OpenCode 定时任务配置

## 已配置的定时任务

| 任务 | 执行时间 | 说明 |
|------|---------|------|
| 每日投资晨报 | 工作日 7:00 | 美股+港股市场分析 |
| 戴维斯双击扫描 | 周二/五 20:00 | 低估值+增长股票扫描 |
| 比特币追踪 | 每天 8:00, 20:00 | BTC技术分析 |

## Crontab 配置

```bash
# 每日投资晨报 - 工作日早7点执行
0 7 * * 1-5 cd /home/ubuntu/stock-value-analyzer && source backend/venv/bin/activate && python scripts/daily_market_report_task.py >> logs/daily_market_report.log 2>&1

# 戴维斯双击扫描 - 每周二、五晚8点执行
0 20 * * 2,5 cd /home/ubuntu/stock-value-analyzer && source backend/venv/bin/activate && python scripts/davis_double_scan_task.py >> logs/davis_double_scan.log 2>&1

# 比特币追踪分析 - 每天早8点和晚8点执行
0 8,20 * * * cd /home/ubuntu/stock-value-analyzer && source backend/venv/bin/activate && python scripts/bitcoin_tracker_task.py >> logs/bitcoin_tracker.log 2>&1
```

## 执行流程

1. **定时触发**：Crontab 按计划时间触发
2. **调用 GLM-4.7**：通过 API 生成投资分析
3. **推送结果**：自动调用 `task_result_client.py` 推送到生产服务器
4. **查看结果**：访问 https://danielzhuang.xyz/crawl

## 日志文件

- `logs/daily_market_report.log` - 每日晨报日志
- `logs/davis_double_scan.log` - 戴维斯双击扫描日志
- `logs/bitcoin_tracker.log` - 比特币追踪日志

## 手动测试

```bash
cd ~/stock-value-analyzer
source backend/venv/bin/activate

# 测试每日晨报
python scripts/daily_market_report_task.py

# 测试戴维斯双击
python scripts/davis_double_scan_task.py

# 测试比特币追踪
python scripts/bitcoin_tracker_task.py
```

## 下次执行时间

- 下次比特币追踪: 今天 20:00
- 下次戴维斯双击: 周二 20:00
- 下次每日晨报: 周一 07:00
