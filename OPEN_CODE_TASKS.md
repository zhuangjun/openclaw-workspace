# OpenCode 定时任务配置

## 任务列表

| 任务 | 脚本路径 | 执行频率 | 说明 |
|------|---------|---------|------|
| 每日投资晨报 | `scripts/daily_market_report_task.py` | 工作日 7:00 | 美股+港股分析 |
| 戴维斯双击扫描 | `scripts/davis_double_scan_task.py` | 周二/五 20:00 | 低估值+增长股票扫描 |
| 比特币追踪 | `scripts/bitcoin_tracker_task.py` | 每天 8:00/20:00 | BTC技术分析 |

## Crontab 配置

```bash
# OpenCode投资定时任务
# 使用GLM-4.7模型生成投资分析

# 每日投资晨报 - 工作日早7点
0 7 * * 1-5 cd /home/ubuntu/stock-value-analyzer && source backend/venv/bin/activate && python scripts/daily_market_report_task.py >> logs/daily_market_report.log 2>&1

# 戴维斯双击扫描 - 每周二、五晚8点
0 20 * * 2,5 cd /home/ubuntu/stock-value-analyzer && source backend/venv/bin/activate && python scripts/davis_double_scan_task.py >> logs/davis_double_scan.log 2>&1

# 比特币追踪 - 每天早8点和晚8点
0 8,20 * * * cd /home/ubuntu/stock-value-analyzer && source backend/venv/bin/activate && python scripts/bitcoin_tracker_task.py >> logs/bitcoin_tracker.log 2>&1
```

## 手动执行测试

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

## 查看结果

访问: https://danielzhuang.xyz/crawl

## API Key

已配置在 `scripts/glm4_client.py` 中
