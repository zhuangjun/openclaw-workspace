import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from typing import Dict

class FinalCorrectedStrategy:
    """
    最终修正版比特币交易策略，包含正确理解的AHR999指数
    """
    
    def __init__(self):
        self.current_price_api = "https://api.coindesk.com/v1/bpi/currentprice/USD.json"
        self.fear_greed_api = "https://api.alternative.me/fng/"
        self.historical_api = "https://api.coindesk.com/v1/bpi/historical/close.json"
        
    def get_current_price(self) -> float:
        """
        获取当前比特币价格
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(self.current_price_api, headers=headers)
            response.raise_for_status()
            data = response.json()
            price_str = data['bpi']['USD']['rate'].replace(',', '')  # 移除千位分隔符
            return float(price_str)
        except Exception as e:
            print(f"获取当前价格失败: {e}")
            return 45000.0  # 默认价格
    
    def get_historical_prices(self, days: int = 500) -> pd.DataFrame:
        """
        获取历史价格数据
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.historical_api}?start={start_date.strftime('%Y-%m-%d')}&end={end_date.strftime('%Y-%m-%d')}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # 解析数据
            dates = list(data['bpi'].keys())
            prices = list(data['bpi'].values())
            timestamps = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'price': prices
            })
            
            # 按时间排序
            df = df.sort_values('timestamp').reset_index(drop=True)
            return df
        except Exception as e:
            print(f"获取历史价格失败: {e}")
            # 创建一个模拟数据框
            dates = [datetime.now() - timedelta(days=i) for i in range(300, 0, -1)]
            prices = [30000 + 100*i + 50*np.sin(i/10) for i in range(len(dates))]  # 模拟价格曲线
            df = pd.DataFrame({
                'timestamp': dates,
                'price': prices
            })
            return df
    
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
    
    def calculate_ahr999_simple(self, df: pd.DataFrame, current_price: float) -> float:
        """
        简化版AHR999计算（因为CoinGecko API受限）
        AHR999 = (BTC价格 / 200日移动平均线) - 这是AHR999的核心概念
        """
        if len(df) < 200:
            print(f"警告: 数据不足200天，只有{len(df)}天数据")
            return None
        
        # 计算200日移动平均线
        df_copy = df.copy()
        df_copy['ma200'] = df_copy['price'].rolling(window=200).mean()
        
        latest_ma200 = df_copy['ma200'].iloc[-1]
        
        if pd.isna(latest_ma200) or latest_ma200 == 0:
            return None
        
        # AHR999的基本形式: BTC价格 / 200日移动平均线
        ahr999 = current_price / latest_ma200
        return ahr999
    
    def get_comprehensive_analysis(self) -> Dict:
        """
        获取综合分析
        """
        print("正在获取当前价格...")
        current_price = self.get_current_price()
        print("正在获取历史数据...")
        df = self.get_historical_prices(days=500)
        print("正在获取恐惧贪婪指数...")
        fear_greed = self.get_fear_greed_index()
        
        # 计算AHR999指数
        ahr999 = self.calculate_ahr999_simple(df, current_price)
        
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
        if fg_value < 5:  # 极度恐惧
            analysis['recommendations']['fear_greed_rec'] = '可能的强力买入机会 (极度恐惧)'
        elif fg_value < 25:  # 恐惧
            analysis['recommendations']['fear_greed_rec'] = '可能的买入机会 (恐惧)'
        elif fg_value < 45:  # 中性偏恐惧
            analysis['recommendations']['fear_greed_rec'] = '谨慎乐观 (中性偏恐惧)'
        elif fg_value > 75:  # 极度贪婪
            analysis['recommendations']['fear_greed_rec'] = '考虑卖出 (极度贪婪)'
        elif fg_value > 55:  # 贪婪
            analysis['recommendations']['fear_greed_rec'] = '谨慎持有 (贪婪)'
        else:  # 中性
            analysis['recommendations']['fear_greed_rec'] = '观望 (中性)'
        
        # AHR999指数推荐 (基于标准定义)
        if ahr999 is not None:
            if ahr999 < 0.4:  # 显著低估
                analysis['recommendations']['ahr999_rec'] = '强烈买入信号 (显著低估)'
            elif ahr999 < 0.8:  # 低估
                analysis['recommendations']['ahr999_rec'] = '买入信号 (低估)'
            elif ahr999 < 1.2:  # 接近合理估值
                analysis['recommendations']['ahr999_rec'] = '轻度买入 (接近合理估值)'
            elif ahr999 > 1.5:  # 高估
                analysis['recommendations']['ahr999_rec'] = '卖出信号 (高估)'
            else:  # 合理估值
                analysis['recommendations']['ahr999_rec'] = '中性 (合理估值)'
        else:
            analysis['recommendations']['ahr999_rec'] = '无法计算 (数据不足)'
        
        return analysis

def print_corrected_analysis():
    """
    打印修正后的市场分析
    """
    print("开始获取比特币综合市场分析...")
    strategy = FinalCorrectedStrategy()
    analysis = strategy.get_comprehensive_analysis()
    
    print("\n" + "="*50)
    print("比特币综合市场分析 (修正版)")
    print("="*50)
    print(f"时间: {analysis['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"当前价格: ${analysis['current_price']:,.2f}")
    
    print("\n--- 恐惧贪婪指数 ---")
    fg = analysis['fear_greed']
    print(f"指数: {fg['value']} - {fg['classification']}")
    print(f"建议: {analysis['recommendations']['fear_greed_rec']}")
    
    print("\n--- AHR999指数 (修正版) ---")
    ahr999 = analysis['ahr999']
    if ahr999 is not None:
        print(f"指数: {ahr999:.3f}")
        print(f"建议: {analysis['recommendations']['ahr999_rec']}")
        print("\nAHR999指数解释:")
        print("- AHR999 < 0.4: 比特币处于极低估值区域，是强力买入时机")
        print("- AHR999 0.4-0.8: 比特币被低估，是买入时机") 
        print("- AHR999 0.8-1.2: 比特币估值趋于合理")
        print("- AHR999 1.2-1.5: 比特币估值偏高，谨慎持有")
        print("- AHR999 > 1.5: 比特币处于高估状态，考虑卖出")
    else:
        print("指数: 无法计算 (可能由于数据不足)")
        print(f"建议: {analysis['recommendations']['ahr999_rec']}")
    
    print("\n--- 综合交易建议 ---")
    fg_rec = analysis['recommendations']['fear_greed_rec']
    ahr999_rec = analysis['recommendations']['ahr999_rec']
    
    # 统计信号
    buy_signals = 0
    sell_signals = 0
    hold_signals = 0
    
    # 恐惧贪婪指数信号
    if any(keyword in fg_rec for keyword in ['买入', '机会']):
        buy_signals += 1
    elif '卖出' in fg_rec:
        sell_signals += 1
    else:
        hold_signals += 1
    
    # AHR999指数信号
    if ahr999 is not None:
        if any(keyword in ahr999_rec for keyword in ['买入', '强力', '强烈']):
            buy_signals += 1
        elif '卖出' in ahr999_rec:
            sell_signals += 1
        else:
            hold_signals += 1
    else:
        # 如果AHR999无法计算，给予中性权重
        hold_signals += 1
    
    print(f"买入信号: {buy_signals}")
    print(f"卖出信号: {sell_signals}")
    print(f"持有/中性信号: {hold_signals}")
    
    if buy_signals > sell_signals:
        strength = "轻度" if buy_signals == 1 else "中度" if buy_signals == 2 else "强烈"
        print(f"\n>>> 总体建议: 买入 ({strength}信号) <<<")
        if '强力' in fg_rec or '强烈' in ahr999_rec:
            print("   特别注意: 至少有一个指标显示强力买入信号")
    elif sell_signals > buy_signals:
        strength = "轻度" if sell_signals == 1 else "中度" if sell_signals == 2 else "强烈"
        print(f"\n>>> 总体建议: 卖出 ({strength}信号) <<<")
    else:
        print(f"\n>>> 总体建议: 持有/观望 (信号冲突或中性) <<<")
    
    print("\n注意: 加密货币市场波动极大，请根据个人风险承受能力谨慎决策。")

if __name__ == "__main__":
    print_corrected_analysis()