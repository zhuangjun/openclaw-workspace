import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict

class AccurateAHR999Calculator:
    """
    使用CoinMarketCap API精确计算AHR999指数
    """
    
    def __init__(self, cmc_api_key="b88a1a0a6b214c79b1112b9e234fc001"):
        self.cmc_api_key = cmc_api_key
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
            
            response = requests.get(url, params=parameters, headers=self.headers)
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
            id_response = requests.get(id_url, params=id_params, headers=self.headers)
            id_data = id_response.json()
            
            if 'data' in id_data and len(id_data['data']) > 0:
                btc_id = id_data['data'][0]['id']
            else:
                print("无法获取比特币ID")
                return None
            
            # 获取历史数据
            hist_url = f"{self.base_url}/v2/cryptocurrency/quotes/historical"
            hist_params = {
                'id': btc_id,
                'time_start': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'time_end': datetime.now().strftime('%Y-%m-%d'),
                'interval': '1d',
                'convert': 'USD'
            }
            
            response = requests.get(hist_url, params=hist_params, headers=self.headers)
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
                return None
        except Exception as e:
            print(f"获取比特币历史数据错误: {e}")
            # 尝试替代方法
            try:
                # 使用CoinGecko作为备选
                print("尝试使用备选API获取数据...")
                gecko_url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}&interval=daily"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                
                response = requests.get(gecko_url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    
                    prices = [item[1] for item in data['prices']]
                    timestamps = [datetime.fromtimestamp(item[0]/1000) for item in data['prices']]
                    
                    df = pd.DataFrame({
                        'timestamp': timestamps,
                        'price': prices
                    })
                    
                    return df
                else:
                    print(f"CoinGecko API也失败，状态码: {response.status_code}")
                    return None
            except:
                print("备选API也失败")
                return None
    
    def calculate_ahr999(self, df: pd.DataFrame, current_price: float) -> float:
        """
        正确计算AHR999指数
        AHR999 = (BTC_price / MA200) * (BTC_price / (0.382 * MA200 + 0.618 * MA200_high))
        但通常简化为 BTC_price / MA200
        """
        if df is None or df.empty or len(df) < 200:
            print(f"警告: 数据不足200天，只有{len(df) if df is not None else 0}天数据")
            return None
        
        # 确保数据按时间排序
        df_sorted = df.sort_values('timestamp').reset_index(drop=True)
        
        # 计算200日移动平均线
        df_sorted['ma200'] = df_sorted['price'].rolling(window=200).mean()
        
        # 计算200日移动平均线的最大值
        df_sorted['ma200_max'] = df_sorted['ma200'].rolling(window=200).max()
        
        if pd.isna(df_sorted['ma200'].iloc[-1]) or pd.isna(df_sorted['ma200_max'].iloc[-1]):
            print("警告: 移动平均线数据无效")
            return None
        
        ma200 = df_sorted['ma200'].iloc[-1]
        ma200_max = df_sorted['ma200_max'].iloc[-1]
        
        if ma200 == 0 or ma200_max == 0:
            print("警告: 移动平均线值为0")
            return None
        
        # 标准AHR999计算
        ratio1 = current_price / ma200
        ratio2 = current_price / (0.382 * ma200 + 0.618 * ma200_max)
        ahr999 = ratio1 * ratio2
        
        return ahr999
    
    def calculate_simple_ahr999(self, df: pd.DataFrame, current_price: float) -> float:
        """
        简化AHR999计算：BTC_price / MA200
        """
        if df is None or df.empty or len(df) < 200:
            print(f"警告: 数据不足200天，只有{len(df) if df is not None else 0}天数据")
            return None
        
        # 确保数据按时间排序
        df_sorted = df.sort_values('timestamp').reset_index(drop=True)
        
        # 计算200日移动平均线
        df_sorted['ma200'] = df_sorted['price'].rolling(window=200).mean()
        
        ma200 = df_sorted['ma200'].iloc[-1]
        
        if pd.isna(ma200) or ma200 == 0:
            print("警告: 200日移动平均线数据无效")
            return None
        
        # 简化AHR999 = BTC价格 / 200日移动平均线
        simplified_ahr999 = current_price / ma200
        return simplified_ahr999

def get_accurate_analysis():
    """
    获取准确的市场分析
    """
    calculator = AccurateAHR999Calculator()
    
    print("正在获取比特币当前价格...")
    current_price = calculator.get_btc_current_price()
    
    if current_price is None:
        print("无法获取当前价格，使用估计值 $45,000")
        current_price = 45000.0
    else:
        print(f"获取到当前价格: ${current_price:,.2f}")
    
    print("\n正在获取历史价格数据...")
    df = calculator.get_btc_historical_data(days=500)
    
    if df is None or df.empty:
        print("无法获取历史数据，使用模拟数据进行演示...")
        # 创建模拟数据
        dates = [datetime.now() - timedelta(days=i) for i in range(500, 0, -1)]
        # 模拟比特币历史价格走势，包含牛市和熊市周期
        prices = []
        for i, date in enumerate(dates):
            # 模拟价格，考虑比特币的波动特性
            base = 20000  # 基础价格
            cycle = 30000 * np.sin(i / 50)  # 周期性波动
            trend = i * 10  # 长期趋势
            noise = np.random.normal(0, 2000)  # 随机噪声
            price = max(base + cycle + trend + noise, 3000)  # 确保不低于最小值
            prices.append(price)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'price': prices
        })
    
    print(f"获取到 {len(df)} 天历史数据")
    
    # 使用简化公式计算AHR999 (更常用的标准)
    simplified_ahr999 = calculator.calculate_simple_ahr999(df, current_price)
    print(f"\n简化版AHR999指数: {simplified_ahr999:.3f}" if simplified_ahr999 else "\n无法计算简化版AHR999指数")
    
    # 使用标准公式计算AHR999
    standard_ahr999 = calculator.calculate_ahr999(df, current_price)
    print(f"标准版AHR999指数: {standard_ahr999:.3f}" if standard_ahr999 else "无法计算标准版AHR999指数")
    
    # 使用可用的AHR999值进行分析
    ahr999 = simplified_ahr999 if simplified_ahr999 is not None else standard_ahr999
    
    if ahr999 is not None:
        print(f"\n=== AHR999指数分析 ===")
        print(f"当前AHR999值: {ahr999:.3f}")
        
        if ahr999 < 0.4:
            print("状态: 强烈低估 - 极佳买入时机")
        elif ahr999 < 0.8:
            print("状态: 低估 - 买入时机")
        elif ahr999 < 1.2:
            print("状态: 接近合理估值 - 轻度买入或持有")
        elif ahr999 < 1.5:
            print("状态: 偏高估值 - 谨慎持有")
        else:
            print("状态: 高估 - 考虑卖出")
    
    return {
        'current_price': current_price,
        'simple_ahr999': simplified_ahr999,
        'standard_ahr999': standard_ahr999,
        'timestamp': datetime.now()
    }

if __name__ == "__main__":
    print("使用CoinMarketCap API进行准确的AHR999指数计算...")
    result = get_accurate_analysis()