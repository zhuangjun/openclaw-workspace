import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Tuple

class CorrectedAHR999Strategy:
    """
    修正版AHR999指数计算的比特币交易策略
    """
    
    def __init__(self):
        self.price_api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        self.historical_api_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        self.fear_greed_api = "https://api.alternative.me/fng/"
        self.signals = []
        
    def get_historical_data(self, days: int = 500) -> pd.DataFrame:
        """
        获取历史价格数据
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            url = f"{self.historical_api_url}?vs_currency=usd&days={days}&interval=daily"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # 转换为DataFrame
            prices = [item[1] for item in data['prices']]
            timestamps = [datetime.fromtimestamp(item[0]/1000) for item in data['prices']]
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'price': prices
            })
            
            return df
        except Exception as e:
            print(f"获取历史数据错误: {e}")
            return pd.DataFrame()
    
    def get_current_price(self) -> float:
        """
        获取当前比特币价格
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(self.price_api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['bitcoin']['usd']
        except Exception as e:
            print(f"获取当前价格失败: {e}")
            # 返回一个模拟值
            return 45000.0
    
    def get_fear_greed_index(self) -> Dict:
        """
        获取恐惧贪婪指数
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(self.fear_greed_api, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data['data'] and len(data['data']) > 0:
                latest_fg = data['data'][0]
                return {
                    'value': int(latest_fg['value']),
                    'classification': latest_fg['value_classification'],
                    'timestamp': datetime.fromtimestamp(int(latest_fg['timestamp']))
                }
        except Exception as e:
            print(f"获取恐惧贪婪指数错误: {e}")
            # 返回模拟值
            return {
                'value': 25,
                'classification': 'Fear',
                'timestamp': datetime.now()
            }
    
    def calculate_corrected_ahr999(self, df: pd.DataFrame, current_price: float) -> float:
        """
        正确计算AHR999指数
        AHR999 = (BTC_price / MA200) * (BTC_price / (0.382 * MA200 + 0.618 * MA200_high))
        """
        if df.empty or len(df) < 200:
            print("警告: 历史数据不足200天，无法准确计算AHR999")
            return None
        
        # 计算200日移动平均线
        df['ma200'] = df['price'].rolling(window=200).mean()
        
        # 计算200日移动平均线的最高价
        df['ma200_high'] = df['ma200'].rolling(window=200).max()
        
        if pd.isna(df['ma200'].iloc[-1]) or pd.isna(df['ma200_high'].iloc[-1]):
            print("警告: 移动平均线数据无效，无法计算AHR999")
            return None
        
        latest_ma200 = df['ma200'].iloc[-1]
        latest_ma200_high = df['ma200_high'].iloc[-1]
        
        # 如果任一值为0或无效，则无法计算
        if latest_ma200 == 0 or latest_ma200_high == 0:
            print("警告: 移动平均线值为0，无法计算AHR999")
            return None
        
        # 计算AHR999
        numerator = current_price / latest_ma200
        denominator = current_price / (0.382 * latest_ma200 + 0.618 * latest_ma200_high)
        
        ahr999 = numerator * denominator
        
        return ahr999
    
    def calculate_basic_ahr999(self, df: pd.DataFrame, current_price: float) -> float:
        """
        简化版AHR999计算（如果完整版不可用）
        只使用BTC价格/Moving Average的比率
        """
        if df.empty or len(df) < 200:
            print("警告: 历史数据不足200天，无法计算简化版AHR999")
            return None
        
        # 计算200日移动平均线
        df['ma200'] = df['price'].rolling(window=200).mean()
        
        if pd.isna(df['ma200'].iloc[-1]):
            print("警告: 200日移动平均线数据无效")
            return None
        
        latest_ma200 = df['ma200'].iloc[-1]
        
        if latest_ma200 == 0:
            return None
        
        # 简化AHR999 = BTC价格 / 200日移动平均线
        simplified_ahr999 = current_price / latest_ma200
        
        return simplified_ahr999
    
    def get_comprehensive_analysis(self) -> Dict:
        """
        获取综合分析
        """
        # 获取历史数据用于计算AHR999
        df = self.get_historical_data(days=500)
        current_price = self.get_current_price()
        fear_greed = self.get_fear_greed_index()
        
        # 尝试计算AHR999指数
        ahr999 = self.calculate_corrected_ahr999(df, current_price)
        
        # 如果完整版AHR999计算失败，尝试简化版
        if ahr999 is None:
            ahr999 = self.calculate_basic_ahr999(df, current_price)
        
        # 生成分析结果
        analysis = {
            'current_price': current_price,
            'fear_greed': fear_greed,
            'ahr999': ahr999,
            'timestamp': datetime.now(),
            'recommendations': {
                'fear_greed_rec': '',
                'ahr999_rec': ''
            }
        }
        
        # 恐惧贪婪指数推荐
        fg_value = fear_greed.get('value', 50)
        if fg_value < 20:  # 极度恐惧
            analysis['recommendations']['fear_greed_rec'] = '可能的买入机会 (极度恐惧)'
        elif fg_value < 40:  # 恐惧
            analysis['recommendations']['fear_greed_rec'] = '谨慎买入 (恐惧)'
        elif fg_value > 70:  # 极度贪婪
            analysis['recommendations']['fear_greed_rec'] = '考虑卖出 (极度贪婪)'
        elif fg_value > 50:  # 贪婪
            analysis['recommendations']['fear_greed_rec'] = '谨慎持有 (贪婪)'
        else:  # 中性到恐惧
            analysis['recommendations']['fear_greed_rec'] = '观望或逐步建仓'
        
        # AHR999指数推荐
        if ahr999 is not None:
            if ahr999 < 0.4:  # 显著低估
                analysis['recommendations']['ahr999_rec'] = '强烈买入信号 (显著低估)'
            elif ahr999 < 1.2:  # 低估
                analysis['recommendations']['ahr999_rec'] = '买入信号 (低估)'
            elif ahr999 > 1.5:  # 高估
                analysis['recommendations']['ahr999_rec'] = '卖出信号 (高估)'
            else:  # 合理估值
                analysis['recommendations']['ahr999_rec'] = '中性 (合理估值)'
        else:
            analysis['recommendations']['ahr999_rec'] = '无法计算 (数据不足)'
        
        return analysis

def print_current_analysis():
    """
    打印当前市场分析
    """
    strategy = CorrectedAHR999Strategy()
    analysis = strategy.get_comprehensive_analysis()
    
    print("=== 比特币综合市场分析 ===")
    print(f"时间: {analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前价格: ${analysis['current_price']:.2f}")
    
    print("\n=== 恐惧贪婪指数 ===")
    fg = analysis['fear_greed']
    print(f"指数: {fg['value']} - {fg['classification']}")
    print(f"建议: {analysis['recommendations']['fear_greed_rec']}")
    
    print("\n=== AHR999指数 ===")
    ahr999 = analysis['ahr999']
    if ahr999 is not None:
        print(f"指数: {ahr999:.3f}")
        print(f"建议: {analysis['recommendations']['ahr999_rec']}")
    else:
        print("指数: 无法计算 (可能由于数据不足)")
        print(f"建议: {analysis['recommendations']['ahr999_rec']}")
    
    print("\n=== 交易建议 ===")
    if ahr999 is not None:
        fg_rec = analysis['recommendations']['fear_greed_rec']
        ahr999_rec = analysis['recommendations']['ahr999_rec']
        
        buy_signals = 0
        sell_signals = 0
        
        # 计算买入信号
        if '买入' in fg_rec:
            buy_signals += 1
        elif '卖出' in fg_rec:
            sell_signals += 1
            
        if '买入' in ahr999_rec:
            buy_signals += 1
        elif '卖出' in ahr999_rec:
            sell_signals += 1
        
        if buy_signals > sell_signals:
            print("综合建议: 买入 (多信号支持)")
        elif sell_signals > buy_signals:
            print("综合建议: 卖出 (多信号支持)")
        else:
            print("综合建议: 持有/观望 (信号冲突或中性)")
    else:
        print("由于AHR999指数无法计算，建议主要参考恐惧贪婪指数和市场价格行为")

if __name__ == "__main__":
    print_current_analysis()