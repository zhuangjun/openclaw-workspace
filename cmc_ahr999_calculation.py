import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from typing import Dict

class CMCAHR999Calculator:
    """
    使用CoinMarketCap API计算AHR999指数
    """
    
    def __init__(self):
        # 从环境变量获取API密钥
        self.cmc_api_key = os.environ.get('CMC_API_KEY')
        if not self.cmc_api_key:
            raise ValueError("CMC_API_KEY环境变量未设置")
        
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.cmc_api_key,
        }
        self.base_url = 'https://pro-api.coinmarketcap.com'
    
    def get_btc_current_price(self):
        """
        获取比特币当前价格
        """
        try:
            url = f"{self.base_url}/v1/cryptocurrency/quotes/latest"
            parameters = {
                'symbol': 'BTC',
                'convert': 'USD'
            }
            
            response = requests.get(url, params=parameters, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'BTC' in data['data']:
                btc_data = data['data']['BTC']
                current_price = btc_data['quote']['USD']['price']
                return current_price
            else:
                print("无法从CoinMarketCap获取比特币价格数据")
                return None
        except Exception as e:
            print(f"获取比特币当前价格错误: {e}")
            return None
    
    def get_btc_historical_data(self, days=500):
        """
        获取比特币历史价格数据
        """
        try:
            # 获取比特币ID
            id_url = f"{self.base_url}/v1/cryptocurrency/map"
            id_params = {'symbol': 'BTC'}
            id_response = requests.get(id_url, params=id_params, headers=self.headers, timeout=30)
            id_response.raise_for_status()
            id_data = id_response.json()
            
            if 'data' in id_data and len(id_data['data']) > 0:
                btc_id = id_data['data'][0]['id']
            else:
                print("无法获取比特币ID")
                return None
            
            # 获取历史数据
            # 由于CMC专业版API的限制，我们使用另一种方式获取历史数据
            print("正在获取历史数据...")
            
            # 获取当前日期往前推指定天数的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 使用CMC的历史端点
            hist_url = f"{self.base_url}/v1/cryptocurrency/quotes/historical"
            hist_params = {
                'id': btc_id,
                'time_start': start_date.strftime('%Y-%m-%d'),
                'time_end': end_date.strftime('%Y-%m-%d'),
                'interval': '1d',
                'convert': 'USD'
            }
            
            response = requests.get(hist_url, params=hist_params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'quotes' in data['data']:
                quotes = data['data']['quotes']
                dates = []
                prices = []
                
                for quote in quotes:
                    date_str = quote['time_open'][:10]  # 取日期部分
                    price = quote['quote']['USD']['price']
                    dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                    prices.append(price)
                
                df = pd.DataFrame({
                    'timestamp': dates,
                    'price': prices
                })
                
                # 按时间排序
                df = df.sort_values('timestamp').reset_index(drop=True)
                return df
            else:
                print("无法从CoinMarketCap获取历史数据")
                print(f"响应数据结构: {data.keys() if 'data' in data else 'No data key'}")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 402:  # 付费功能
                print("CoinMarketCap历史数据API需要高级订阅，尝试使用替代方法...")
                return self.get_historical_data_alternative()
            else:
                print(f"获取比特币历史数据HTTP错误: {e}")
                return None
        except Exception as e:
            print(f"获取比特币历史数据错误: {e}")
            return self.get_historical_data_alternative()
    
    def get_historical_data_alternative(self):
        """
        替代方法获取历史数据（如果CMC API受限）
        """
        try:
            print("使用替代API获取历史数据...")
            # 使用CoinGecko作为备选，但使用更可靠的方法
            gecko_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
            
            # 获取过去一年的数据
            end_timestamp = int(time.time())
            start_timestamp = end_timestamp - (500 * 24 * 3600)  # 500天前
            
            params = {
                'vs_currency': 'usd',
                'from': start_timestamp,
                'to': end_timestamp
            }
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(gecko_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'prices' in data:
                prices = [item[1] for item in data['prices']]
                timestamps = [datetime.fromtimestamp(item[0]/1000) for item in data['prices']]
                
                df = pd.DataFrame({
                    'timestamp': timestamps,
                    'price': prices
                })
                
                return df
            else:
                print("无法从替代API获取历史数据")
                return None
        except Exception as e:
            print(f"替代API也失败: {e}")
            return None
    
    def calculate_ahr999(self, df: pd.DataFrame, current_price: float) -> float:
        """
        计算AHR999指数
        AHR999 = (BTC_price / MA200) * (BTC_price / (0.382 * MA200 + 0.618 * MA200_high))
        """
        if df is None or df.empty or len(df) < 200:
            print(f"警告: 数据不足200天，只有{len(df) if df is not None else 0}天数据")
            return None
        
        # 确保数据按时间排序
        df_sorted = df.sort_values('timestamp').reset_index(drop=True)
        
        # 计算200日移动平均线
        df_sorted['ma200'] = df_sorted['price'].rolling(window=200).mean()
        
        # 计算200日移动平均线的最大值（滚动最大值）
        # 这里使用过去一段时间内的MA200的最大值
        ma200_series = df_sorted['price'].rolling(window=200).mean()
        df_sorted['ma200_max'] = ma200_series.rolling(window=200).max()
        
        if pd.isna(df_sorted['ma200'].iloc[-1]) or pd.isna(df_sorted['ma200_max'].iloc[-1]):
            print("警告: 移动平均线数据无效")
            return None
        
        latest_ma200 = df_sorted['ma200'].iloc[-1]
        latest_ma200_max = df_sorted['ma200_max'].iloc[-1]
        
        if latest_ma200 == 0 or latest_ma200_max == 0:
            print("警告: 移动平均线值为0")
            return None
        
        # 计算AHR999
        ratio1 = current_price / latest_ma200
        ratio2 = current_price / (0.382 * latest_ma200 + 0.618 * latest_ma200_max)
        ahr999 = ratio1 * ratio2
        
        return ahr999
    
    def calculate_simple_ahr999(self, df: pd.DataFrame, current_price: float) -> float:
        """
        计算简化AHR999: BTC_price / MA200
        """
        if df is None or df.empty or len(df) < 200:
            print(f"警告: 数据不足200天，只有{len(df) if df is not None else 0}天数据")
            return None
        
        # 确保数据按时间排序
        df_sorted = df.sort_values('timestamp').reset_index(drop=True)
        
        # 计算200日移动平均线
        df_sorted['ma200'] = df_sorted['price'].rolling(window=200).mean()
        
        latest_ma200 = df_sorted['ma200'].iloc[-1]
        
        if pd.isna(latest_ma200) or latest_ma200 == 0:
            print("警告: 200日移动平均线数据无效")
            return None
        
        # 计算简化AHR999
        simplified_ahr999 = current_price / latest_ma200
        return simplified_ahr999

def get_cmc_analysis():
    """
    获取基于CMC API的分析
    """
    print("使用CoinMarketCap API进行AHR999指数计算...")
    
    try:
        calculator = CMCAHR999Calculator()
    except ValueError as e:
        print(f"错误: {e}")
        return None
    
    print("正在获取比特币当前价格...")
    current_price = calculator.get_btc_current_price()
    
    if current_price is None:
        print("无法获取当前价格")
        return None
    
    print(f"当前比特币价格: ${current_price:,.2f}")
    
    print("\n正在获取历史价格数据...")
    df = calculator.get_btc_historical_data(days=500)
    
    if df is None or df.empty:
        print("无法获取历史数据")
        return None
    
    print(f"获取到 {len(df)} 天历史数据")
    
    # 计算AHR999指数
    print("\n正在计算AHR999指数...")
    
    # 先尝试计算简化版
    simple_ahr999 = calculator.calculate_simple_ahr999(df, current_price)
    print(f"简化版AHR999指数: {simple_ahr999:.3f}" if simple_ahr999 else "无法计算简化版AHR999指数")
    
    # 计算标准版（如果数据充足）
    standard_ahr999 = calculator.calculate_ahr999(df, current_price)
    print(f"标准版AHR999指数: {standard_ahr999:.3f}" if standard_ahr999 else "无法计算标准版AHR999指数")
    
    # 使用可用的值进行分析
    ahr999 = simple_ahr999 if simple_ahr999 is not None else standard_ahr999
    
    if ahr999 is not None:
        print(f"\n=== AHR999指数分析 ===")
        print(f"当前AHR999值: {ahr999:.3f}")
        
        if ahr999 < 0.4:
            status = "强烈低估 - 极佳买入时机"
            signal = "强力买入"
        elif ahr999 < 0.8:
            status = "低估 - 买入时机"
            signal = "买入"
        elif ahr999 < 1.2:
            status = "接近合理估值 - 轻度买入或持有"
            signal = "持有/轻度买入"
        elif ahr999 < 1.5:
            status = "偏高估值 - 谨慎持有"
            signal = "谨慎持有"
        else:
            status = "高估 - 考虑卖出"
            signal = "卖出"
        
        print(f"状态: {status}")
        print(f"交易信号: {signal}")
    
    return {
        'current_price': current_price,
        'simple_ahr999': simple_ahr999,
        'standard_ahr999': standard_ahr999,
        'timestamp': datetime.now()
    }

if __name__ == "__main__":
    result = get_cmc_analysis()