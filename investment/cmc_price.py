#!/usr/bin/env python3
"""
CoinMarketCap API 价格获取工具
用于获取 BTC/加密货币价格

环境变量:
    CMC_API_KEY - CoinMarketCap API Key
"""

import os
import sys
import requests
from typing import Optional, Dict, List

CMC_API_BASE = "https://pro-api.coinmarketcap.com/v1"

def get_cmc_api_key() -> str:
    """获取 CMC API Key"""
    key = os.getenv('CMC_API_KEY')
    if not key:
        raise ValueError("CMC_API_KEY 环境变量未设置")
    return key

def get_crypto_price(symbols: List[str], convert: str = "USD") -> Dict[str, float]:
    """
    获取加密货币价格
    
    Args:
        symbols: 加密货币符号列表，如 ["BTC", "ETH"]
        convert: 转换货币，默认 USD
    
    Returns:
        Dict: {symbol: price}
    """
    api_key = get_cmc_api_key()
    
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }
    
    params = {
        'symbol': ','.join(symbols),
        'convert': convert
    }
    
    try:
        response = requests.get(
            f"{CMC_API_BASE}/cryptocurrency/quotes/latest",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        result = {}
        if 'data' in data:
            for symbol in symbols:
                if symbol in data['data']:
                    quote = data['data'][symbol]['quote'][convert]
                    result[symbol] = {
                        'price': quote['price'],
                        'change_24h': quote['percent_change_24h'],
                        'market_cap': quote['market_cap'],
                        'volume_24h': quote['volume_24h']
                    }
        return result
        
    except Exception as e:
        print(f"❌ CMC API 请求失败: {e}")
        return {}

def get_btc_price() -> Optional[Dict]:
    """获取 BTC 价格（快捷方式）"""
    prices = get_crypto_price(["BTC"])
    return prices.get("BTC")

def get_exchange_rates(base: str = "USD") -> Dict[str, float]:
    """
    获取汇率（通过 CMC fiat API）
    
    Args:
        base: 基础货币，默认 USD
    
    Returns:
        Dict: {currency: rate}
    """
    api_key = get_cmc_api_key()
    
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }
    
    # 获取 USD 对 CNY, HKD 的汇率
    try:
        response = requests.get(
            f"{CMC_API_BASE}/fiat/map",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        # CMC 不直接提供汇率，我们用 crypto 价格推算
        # 或者使用其他 API
        return {}
        
    except Exception as e:
        print(f"⚠️  汇率获取失败: {e}")
        return {}

if __name__ == '__main__':
    # 测试
    print("📡 获取 BTC 实时价格...")
    btc = get_btc_price()
    if btc:
        print(f"✅ BTC: ${btc['price']:,.2f}")
        print(f"   24h 涨跌: {btc['change_24h']:+.2f}%")
        print(f"   市值: ${btc['market_cap']/1e12:.2f}T")
        print(f"   24h 成交量: ${btc['volume_24h']/1e9:.1f}B")
    else:
        print("❌ 获取失败")
