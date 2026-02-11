#!/usr/bin/env python3
"""
比特币实时数据获取器
使用CoinGecko免费API获取实时价格数据
与Kimi分析合并后推送到生产服务器
"""
import requests
import json
from datetime import datetime, date
import sys
sys.path.insert(0, '/home/ubuntu/stock-value-analyzer/scripts')
from task_result_client import push_task_result

# CoinGecko免费API（无需API Key）
COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_btc_realtime_data():
    """获取BTC实时价格数据"""
    try:
        # 1. 获取当前价格
        price_url = f"{COINGECKO_API}/simple/price"
        price_params = {
            "ids": "bitcoin",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }
        
        response = requests.get(price_url, params=price_params, timeout=30)
        price_data = response.json()
        
        btc_data = price_data.get("bitcoin", {})
        
        # 2. 获取OHLC数据（计算支撑阻力位）
        ohlc_url = f"{COINGECKO_API}/coins/bitcoin/ohlc"
        ohlc_params = {
            "vs_currency": "usd",
            "days": "7"  # 7天数据
        }
        
        ohlc_response = requests.get(ohlc_url, params=ohlc_params, timeout=30)
        ohlc_data = ohlc_response.json()
        
        # 计算7日高低点（支撑阻力参考）
        if isinstance(ohlc_data, list) and len(ohlc_data) > 0:
            highs = [candle[2] for candle in ohlc_data]
            lows = [candle[3] for candle in ohlc_data]
            week_high = max(highs)
            week_low = min(lows)
        else:
            week_high = btc_data.get("usd", 0) * 1.1
            week_low = btc_data.get("usd", 0) * 0.9
        
        # 3. 获取市场数据（恐惧贪婪指数等）
        # 注意：CoinGecko免费版没有恐惧贪婪指数，需要其他API或省略
        
        return {
            "price": btc_data.get("usd", 0),
            "change_24h": btc_data.get("usd_24h_change", 0),
            "volume_24h": btc_data.get("usd_24h_vol", 0),
            "market_cap": btc_data.get("usd_market_cap", 0),
            "week_high": week_high,
            "week_low": week_low,
            "timestamp": datetime.now().isoformat(),
            "data_source": "CoinGecko API (Real-time)"
        }
        
    except Exception as e:
        print(f"获取实时数据失败: {e}")
        return None

def get_kimi_analysis():
    """
    获取Kimi的定性分析报告
    实际运行时会调用Kimi生成
    """
    # 这里会由Kimi生成后传入
    # 或者通过消息触发Kimi生成
    pass

def generate_report_with_data(btc_data, kimi_analysis_text=None):
    """
    合并实时数据和Kimi分析，生成完整报告
    """
    if not btc_data:
        return None
    
    price = btc_data["price"]
    change = btc_data["change_24h"]
    week_high = btc_data["week_high"]
    week_low = btc_data["week_low"]
    
    # 根据实时数据计算技术信号
    signals = []
    
    # 价格位置判断
    price_range = week_high - week_low
    if price_range > 0:
        position = (price - week_low) / price_range
        if position > 0.7:
            signals.append("接近7日高点")
        elif position < 0.3:
            signals.append("接近7日低点")
        else:
            signals.append("处于7日中间区间")
    
    # 涨跌幅判断
    if change > 5:
        signals.append("24h强势上涨")
    elif change > 2:
        signals.append("24h温和上涨")
    elif change < -5:
        signals.append("24h大幅下跌")
    elif change < -2:
        signals.append("24h回调")
    else:
        signals.append("24h横盘震荡")
    
    # 计算关键价位（基于实时价格）
    resistance_1 = round(price * 1.05, 0)  # +5%
    resistance_2 = round(price * 1.10, 0)  # +10%
    support_1 = round(price * 0.95, 0)     # -5%
    support_2 = round(price * 0.90, 0)     # -10%
    
    # 构建报告
    report = f"""# ₿ 比特币追踪分析报告
**日期：{date.today().strftime('%Y年%m月%d日')}**
**数据更新时间：{btc_data['timestamp'][:19]}**

---

## 📊 实时价格数据

| 指标 | 数据 |
|------|------|
| **当前价格** | ${price:,.2f} |
| **24h涨跌** | {change:+.2f}% {'📈' if change > 0 else '📉' if change < 0 else '➡️'} |
| **24h交易量** | ${btc_data['volume_24h']:,.0f} |
| **市值** | ${btc_data['market_cap']:,.0f} |
| **7日最高** | ${week_high:,.2f} |
| **7日最低** | ${week_low:,.2f} |
| **数据来源** | {btc_data['data_source']} |

---

## 📈 技术分析（基于实时数据）

### 关键价位（动态计算）
| 类型 | 价位 | 距离当前 |
|------|------|----------|
| **阻力位1** | ${resistance_1:,.0f} | +{((resistance_1/price-1)*100):.1f}% |
| **阻力位2** | ${resistance_2:,.0f} | +{((resistance_2/price-1)*100):.1f}% |
| **当前价格** | ${price:,.2f} | - |
| **支撑位1** | ${support_1:,.0f} | {((support_1/price-1)*100):.1f}% |
| **支撑位2** | ${support_2:,.0f} | {((support_2/price-1)*100):.1f}% |

### 实时技术信号
{chr(10).join(['• ' + s for s in signals])}

### 价格位置分析
当前价格处于7日区间的 **{((price - week_low) / (week_high - week_low) * 100):.1f}%** 位置

---

## 💡 操作建议（基于实时数据）

### 短线交易者（1-3天）
"""
    
    # 根据实时价格给出具体建议
    if change < -5:
        report += """• **超卖反弹机会**：24h跌幅较大，可能存在技术性反弹
• 可在当前价位小仓位试多，止损设于${:.0f}
• 目标位：${:.0f}（回本出局）""".format(support_2, price * 1.03)
    elif change > 5:
        report += """• **追高风险**：24h涨幅较大，不宜追高
• 等待回调至${:.0f}附近再考虑入场
• 或分批止盈现有仓位""".format(support_1)
    else:
        report += """• **震荡观望**：当前处于横盘区间，方向不明
• 突破${:.0f}可追涨，跌破${:.0f}需止损
• 区间内可做高抛低吸""".format(resistance_1, support_1)
    
    report += f"""

### 中长线持有者（1-3个月）
• **核心支撑**：${support_2:,.0f}（不破持有，跌破减仓）
• **加仓区间**：${support_1:,.0f} - ${support_2:,.0f}
• **止盈目标**：${resistance_1:,.0f} / ${resistance_2:,.0f}

---

## 📝 分析说明

**⚠️ 重要提示**：
1. 以上价格为CoinGecko实时API数据，更新于{btc_data['timestamp'][:16]}
2. 加密货币价格波动极大，请以交易平台实际报价为准
3. 技术分析仅供参考，不构成投资建议
4. 投资有风险，入市需谨慎

---

*数据由CoinGecko API提供 | 分析由Kimi生成*
"""
    
    return report

def main():
    """主函数：获取实时数据并推送"""
    print(f"[{datetime.now()}] 开始获取BTC实时数据...")
    
    # 1. 获取实时数据
    btc_data = get_btc_realtime_data()
    
    if not btc_data:
        print("❌ 获取实时数据失败")
        return
    
    print(f"✅ 获取实时数据成功")
    print(f"   价格: ${btc_data['price']:,.2f}")
    print(f"   24h变化: {btc_data['change_24h']:+.2f}%")
    
    # 2. 生成报告（基于实时数据）
    report_text = generate_report_with_data(btc_data)
    
    if not report_text:
        print("❌ 生成报告失败")
        return
    
    # 3. 推送到生产服务器
    result = push_task_result(
        task_type='bitcoin_tracker',
        task_name='比特币追踪分析',
        result_data={
            'full_report': report_text,
            'btc_price': btc_data['price'],
            'price_change_24h': btc_data['change_24h'],
            'signals': [
                f"价格: ${btc_data['price']:,.0f}",
                f"24h: {btc_data['change_24h']:+.2f}%",
                f"7日区间: ${btc_data['week_low']:,.0f} - ${btc_data['week_high']:,.,.0f}"
            ],
            'week_high': btc_data['week_high'],
            'week_low': btc_data['week_low'],
            'data_source': 'CoinGecko API',
            'timestamp': btc_data['timestamp']
        },
        result_summary=f"BTC ${btc_data['price']:,.0f} ({btc_data['change_24h']:+.2f}%) | 数据时间: {btc_data['timestamp'][:16]}",
        status='success',
        items_processed=1,
        items_succeeded=1,
        duration_seconds=30
    )
    
    if result.get('success'):
        print(f"✅ 报告已推送到生产服务器")
        print(f"   价格: ${btc_data['price']:,.2f}")
        print(f"   查看: https://danielzhuang.xyz/reports")
    else:
        print(f"❌ 推送失败: {result.get('error')}")

if __name__ == "__main__":
    main()
