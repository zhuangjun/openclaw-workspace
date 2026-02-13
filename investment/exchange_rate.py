#!/usr/bin/env python3
"""
实时汇率获取工具
使用 exchangerate-api.com（免费版无需 API Key）
或使用其他免费汇率 API
"""

import requests
from typing import Optional, Dict
from datetime import datetime

# 免费汇率 API
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"

def get_exchange_rates() -> Dict[str, float]:
    """
    获取 USD 对其他货币的实时汇率
    
    Returns:
        Dict: {currency: rate}
    """
    try:
        response = requests.get(EXCHANGE_RATE_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        rates = data.get('rates', {})
        
        # 提取关键汇率
        return {
            'CNY': rates.get('CNY', 7.25),
            'HKD': rates.get('HKD', 7.80),
            'EUR': rates.get('EUR', 0.92),
            'JPY': rates.get('JPY', 150),
            'GBP': rates.get('GBP', 0.79),
            'last_updated': data.get('date', datetime.now().strftime('%Y-%m-%d'))
        }
        
    except Exception as e:
        print(f"⚠️  实时汇率获取失败，使用默认值: {e}")
        return {
            'CNY': 7.25,
            'HKD': 7.80,
            'EUR': 0.92,
            'JPY': 150,
            'GBP': 0.79,
            'last_updated': 'fallback'
        }

def get_usd_cny_rate() -> float:
    """获取 USD/CNY 汇率"""
    rates = get_exchange_rates()
    return rates.get('CNY', 7.25)

def get_hkd_cny_rate() -> float:
    """
    获取 HKD/CNY 汇率
    计算方法: CNY/HKD = (CNY/USD) / (HKD/USD)
    """
    rates = get_exchange_rates()
    usd_cny = rates.get('CNY', 7.25)
    usd_hkd = rates.get('HKD', 7.80)
    return usd_cny / usd_hkd  # HKD 转 CNY 需要除以这个值

if __name__ == '__main__':
    print("📡 获取实时汇率...")
    rates = get_exchange_rates()
    
    print(f"✅ USD/CNY: {rates['CNY']:.4f}")
    print(f"✅ USD/HKD: {rates['HKD']:.4f}")
    print(f"✅ HKD/CNY: {rates['CNY']/rates['HKD']:.4f}")
    print(f"   更新时间: {rates.get('last_updated', 'N/A')}")
    
    print(f"\n快捷函数测试:")
    print(f"   get_usd_cny_rate(): {get_usd_cny_rate():.4f}")
    print(f"   get_hkd_cny_rate(): {get_hkd_cny_rate():.4f}")
