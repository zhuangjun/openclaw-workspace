# Friday Portfolio - Telegram Channel 配置

## Channel 信息

| 属性 | 值 |
|------|-----|
| **Channel ID** | `friday-portfolio` |
| **用途** | 模拟投资组合交易通知 |
| **Bot Token** | 已配置 |
| **创建时间** | 2026-02-09 |

## 通知类型

以下情况会发送通知到此 Channel：

1. **🟢 交易执行** - 买入/卖出操作
2. **🔴 止损触发** - 强制止损
3. **📊 周报** - 每周投资组合回顾
4. **⚠️ 风控告警** - 仓位异常、风险提醒

## 使用方法

### 方式1: 使用 Python 脚本

```python
import subprocess
import json

# 发送交易通知
message = """🟢 **交易执行**

**标的**: MSFT
**方向**: 买入
**金额**: ¥100,000
**仓位**: 10%
"""

result = subprocess.run(
    ["python3", "channel_notifier.py", message],
    capture_output=True,
    text=True
)

# 解析输出获取发送参数
output = json.loads(result.stdout)
# output = {"action": "send", "target": "friday-portfolio", "message": "..."}
```

### 方式2: 通过 trade_executor 自动发送

```python
from trade_executor import execute_trade_with_notification

trade_data = {
    "symbol": "MSFT",
    "direction": "买入",
    # ... 其他字段
}

result = execute_trade_with_notification(trade_data)
# 会自动发送通知到 friday-portfolio channel
```

## 通知格式

### 交易通知模板

```
🟢 **模拟盘交易执行**

**标的**: {symbol} ({name})
**方向**: {direction}
**价格**: ${price}
**数量**: {shares}
**金额**: ¥{amount:,}
**仓位占比**: {ratio}%
**风格**: {style}

💡 **买入理由**: {reason}

📊 投资组合已更新
🌐 https://danielzhuang.xyz/Friday

🎯 **责任声明**: 本交易由 Friday (AI) 全权负责执行
```

### 风控告警模板

```
🚫 **交易被拒绝**

❌ 风控拒绝: {reason}

责任方: Friday (AI)
```

## 当前聊天窗口

- 交易通知 → **friday-portfolio** Channel
- 日常对话 → **当前聊天窗口** (Daniel Zhuang)

---

*配置文件: `config/channel.json`*
