import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Tuple

class EnhancedBitcoinTradingStrategy:
    """
    增强版比特币交易策略，包含恐惧贪婪指数和ahr999指数
    """
    
    def __init__(self):
        self.price_api_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        self.fear_greed_api = "https://api.alternative.me/fng/"
        self.signals = []
        
    def get_bitcoin_data(self, days: int = 365) -> pd.DataFrame:
        """
        获取比特币价格数据
        """
        url = f"{self.price_api_url}?vs_currency=usd&days={days}&interval=daily"
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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
            print(f"获取比特币数据错误: {e}")
            # 如果API调用失败，返回一个模拟的数据框用于演示
            if days == 1:
                # 对于只需要一天数据的情况，尝试获取当前价格
                try:
                    current_price_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", headers=headers)
                    current_price_data = current_price_response.json()
                    current_price = current_price_data['bitcoin']['usd']
                    
                    df = pd.DataFrame({
                        'timestamp': [datetime.now()],
                        'price': [current_price]
                    })
                    return df
                except:
                    pass
            return pd.DataFrame()
    
    def get_fear_greed_index(self) -> Dict:
        """
        获取恐惧贪婪指数
        """
        try:
            response = requests.get(self.fear_greed_api)
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
            return {}
    
    def calculate_ahr999_index(self, price: float) -> float:
        """
        计算ahr999指数
        ahr999 = (BTC_price / MA200) * (BTC_price / (0.382 * MA200 + 0.618 * MA200_high))
        简化计算方式：ahr999 = BTC_price / (MA200 * threshold)
        当ahr999 < 1.2时，被认为是低估区域（抄底区域）
        当ahr999 > 1.5时，被认为是高估区域（顶部区域）
        """
        try:
            # 获取更长期的数据来计算200日均线
            df = self.get_bitcoin_data(400)  # 获取超过200天的数据
            
            if df.empty or len(df) < 200:
                return None
                
            # 计算200日移动平均线
            df['ma200'] = df['price'].rolling(window=200).mean()
            latest_ma200 = df['ma200'].iloc[-1]
            
            if pd.isna(latest_ma200) or latest_ma200 == 0:
                return None
                
            # 计算ahr999指数
            ahr999 = price / latest_ma200
            
            return ahr999
        except Exception as e:
            print(f"计算ahr999指数错误: {e}")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        """
        # 简单移动平均线
        df['sma_20'] = df['price'].rolling(window=20).mean()
        df['sma_50'] = df['price'].rolling(window=50).mean()
        
        # 指数移动平均线
        df['ema_12'] = df['price'].ewm(span=12).mean()
        df['ema_26'] = df['price'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI (相对强弱指数)
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['bb_middle'] = df['price'].rolling(window=20).mean()
        bb_std = df['price'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df
    
    def get_market_sentiment_analysis(self) -> Dict:
        """
        获取市场情绪分析（恐惧贪婪指数 + ahr999指数）
        """
        fear_greed = self.get_fear_greed_index()
        latest_data = self.get_bitcoin_data(days=1)
        
        if latest_data.empty:
            return {'error': '无法获取最新价格数据'}
        
        current_price = latest_data.iloc[-1]['price']
        ahr999 = self.calculate_ahr999_index(current_price)
        
        sentiment_analysis = {
            'fear_greed': fear_greed,
            'ahr999': ahr999,
            'current_price': current_price,
            'timestamp': datetime.now()
        }
        
        # 分析情绪指标
        if fear_greed:
            fg_value = fear_greed.get('value', 50)
            fg_class = fear_greed.get('classification', 'Neutral')
            
            # 根据恐惧贪婪指数给出建议
            if fg_value < 20:  # 极度恐惧
                sentiment_analysis['fear_greed_recommendation'] = '可能的买入机会 (极度恐惧)'
            elif fg_value < 40:  # 恐惧
                sentiment_analysis['fear_greed_recommendation'] = '谨慎买入 (恐惧)'
            elif fg_value > 70:  # 极度贪婪
                sentiment_analysis['fear_greed_recommendation'] = '考虑卖出 (极度贪婪)'
            elif fg_value > 50:  # 贪婪
                sentiment_analysis['fear_greed_recommendation'] = '谨慎持有 (贪婪)'
            else:  # 中性到恐惧
                sentiment_analysis['fear_greed_recommendation'] = '观望或逐步建仓'
        
        # 分析ahr999指数
        if ahr999 is not None:
            if ahr999 < 0.4:  # 显著低估
                sentiment_analysis['ahr999_recommendation'] = '强烈买入信号 (显著低估)'
            elif ahr999 < 0.8:  # 低估
                sentiment_analysis['ahr999_recommendation'] = '买入信号 (低估)'
            elif ahr999 > 1.2:  # 高估
                sentiment_analysis['ahr999_recommendation'] = '卖出信号 (高估)'
            else:
                sentiment_analysis['ahr999_recommendation'] = '中性 (合理估值)'
        
        return sentiment_analysis
    
    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        基于技术指标生成买卖信号
        """
        signals = []
        
        for i in range(1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            signal = {
                'date': current['timestamp'],
                'price': current['price'],
                'signal': None,
                'reason': ''
            }
            
            # 买入信号
            if (
                # 价格上穿SMA-20
                previous['price'] <= previous['sma_20'] and current['price'] > current['sma_20'] and
                # RSI显示超卖
                current['rsi'] < 35 and
                # MACD看涨交叉
                previous['macd'] <= previous['macd_signal'] and current['macd'] > current['macd_signal']
            ):
                signal['signal'] = 'BUY'
                signal['reason'] = '价格上穿SMA-20, RSI超卖, MACD看涨'
            
            # 额外买入条件：RSI背离
            elif current['rsi'] < 30 and current['price'] < current['bb_lower']:
                signal['signal'] = 'BUY'
                signal['reason'] = 'RSI超卖 + 价格近布林带下轨'
                
            # 卖出信号
            elif (
                # 价格下破SMA-20
                previous['price'] >= previous['sma_20'] and current['price'] < current['sma_20'] and
                # RSI显示超买
                current['rsi'] > 65 and
                # MACD看跌交叉
                previous['macd'] >= previous['macd_signal'] and current['macd'] < current['macd_signal']
            ):
                signal['signal'] = 'SELL'
                signal['reason'] = '价格下破SMA-20, RSI超买, MACD看跌'
                
            # 额外卖出条件：RSI背离
            elif current['rsi'] > 70 and current['price'] > current['bb_upper']:
                signal['signal'] = 'SELL'
                signal['reason'] = 'RSI超买 + 价格近布林带上轨'
            
            if signal['signal']:
                signals.append(signal)
        
        return signals
    
    def generate_enhanced_signals(self) -> Dict:
        """
        生成综合信号（技术指标 + 恐惧贪婪指数 + ahr999指数）
        """
        # 获取技术指标信号
        df = self.get_bitcoin_data(days=90)  # 获取3个月数据
        if df.empty:
            return {'error': '无法获取数据'}
        
        df = self.calculate_indicators(df)
        tech_signals = self.generate_signals(df)
        
        # 获取市场情绪分析
        sentiment = self.get_market_sentiment_analysis()
        
        # 综合分析
        enhanced_signal = {
            'technical_analysis': {},
            'sentiment_analysis': sentiment,
            'recommendation': 'HOLD',
            'confidence_level': 'medium',
            'reasoning': []
        }
        
        # 获取最新的技术数据
        latest_data = df.iloc[-1]
        current_price = latest_data['price']
        
        enhanced_signal['technical_analysis'] = {
            'current_price': current_price,
            'rsi': round(latest_data['rsi'], 2) if not pd.isna(latest_data['rsi']) else None,
            'sma_20': round(latest_data['sma_20'], 2) if not pd.isna(latest_data['sma_20']) else None,
            'sma_50': round(latest_data['sma_50'], 2) if not pd.isna(latest_data['sma_50']) else None,
            'macd': round(latest_data['macd'], 4) if not pd.isna(latest_data['macd']) else None,
            'macd_signal': round(latest_data['macd_signal'], 4) if not pd.isna(latest_data['macd_signal']) else None,
            'bb_upper': round(latest_data['bb_upper'], 2) if not pd.isna(latest_data['bb_upper']) else None,
            'bb_lower': round(latest_data['bb_lower'], 2) if not pd.isna(latest_data['bb_lower']) else None,
            'latest_tech_signal': tech_signals[-1] if tech_signals else None
        }
        
        # 根据综合指标确定最终推荐
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        # 检查技术指标
        if tech_signals and tech_signals[-1]['signal'] == 'BUY':
            buy_signals += 1
            reasons.append(f"技术指标: {tech_signals[-1]['reason']}")
        elif tech_signals and tech_signals[-1]['signal'] == 'SELL':
            sell_signals += 1
            reasons.append(f"技术指标: {tech_signals[-1]['reason']}")
        
        # 检查恐惧贪婪指数
        if 'fear_greed_recommendation' in sentiment:
            fg_rec = sentiment['fear_greed_recommendation']
            if '买入' in fg_rec:
                buy_signals += 1
                reasons.append(f"恐惧贪婪指数: {fg_rec}")
            elif '卖出' in fg_rec:
                sell_signals += 1
                reasons.append(f"恐惧贪婪指数: {fg_rec}")
        
        # 检查ahr999指数
        if 'ahr999_recommendation' in sentiment:
            ahr_rec = sentiment['ahr999_recommendation']
            if '买入' in ahr_rec:
                buy_signals += 1
                reasons.append(f"AHR999指数: {ahr_rec}")
            elif '卖出' in ahr_rec:
                sell_signals += 1
                reasons.append(f"AHR999指数: {ahr_rec}")
        
        enhanced_signal['reasoning'] = reasons
        
        # 确定最终推荐
        if buy_signals > sell_signals:
            enhanced_signal['recommendation'] = 'BUY'
            if buy_signals >= 2:
                enhanced_signal['confidence_level'] = 'high'
            else:
                enhanced_signal['confidence_level'] = 'medium'
        elif sell_signals > buy_signals:
            enhanced_signal['recommendation'] = 'SELL'
            if sell_signals >= 2:
                enhanced_signal['confidence_level'] = 'high'
            else:
                enhanced_signal['confidence_level'] = 'medium'
        else:
            enhanced_signal['recommendation'] = 'HOLD'
            enhanced_signal['confidence_level'] = 'low'
        
        return enhanced_signal

def check_enhanced_daily_signals():
    """
    检查每日信号并发送警报
    """
    strategy = EnhancedBitcoinTradingStrategy()
    enhanced_signal = strategy.generate_enhanced_signals()
    
    if 'error' in enhanced_signal:
        return f"错误: {enhanced_signal['error']}"
    
    recommendation = enhanced_signal['recommendation']
    confidence = enhanced_signal['confidence_level']
    
    if recommendation in ['BUY', 'SELL']:
        # 构建详细警报信息
        ta = enhanced_signal['technical_analysis']
        sa = enhanced_signal['sentiment_analysis']
        
        alert_message = f"""
🚨 增强版比特币交易警报 🚨

日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
推荐: {recommendation} ({confidence.upper()} 置信度)
价格: ${ta['current_price']:.2f}

=== 技术指标 ===
RSI: {ta['rsi']} ({'超卖' if ta['rsi'] < 30 else '超买' if ta['rsi'] > 70 else '中性'})
SMA-20: ${ta['sma_20']:.2f}
SMA-50: ${ta['sma_50']:.2f}
MACD: {ta['macd']} (信号: {ta['macd_signal']})

=== 市场情绪指标 ===
恐惧贪婪指数: {sa.get('fear_greed', {}).get('value', 'N/A')} - {sa.get('fear_greed', {}).get('classification', 'N/A')}
情绪推荐: {sa.get('fear_greed_recommendation', 'N/A')}
AHR999指数: {sa.get('ahr999') if sa.get('ahr999') is not None else 'N/A':.3f}
AHR999推荐: {sa.get('ahr999_recommendation', 'N/A')}

=== 决策理由 ===
"""
        for reason in enhanced_signal['reasoning']:
            alert_message += f"- {reason}\n"
        
        alert_message += "\n请结合自身风险承受能力谨慎决策！"
        return alert_message.strip()
    else:
        # 提供市场概览
        ta = enhanced_signal['technical_analysis']
        sa = enhanced_signal['sentiment_analysis']
        
        overview_message = f"""
📈 比特币每日市场概览 📈

日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
当前价格: ${ta['current_price']:.2f}
推荐: {recommendation} ({confidence.upper()} 置信度)

=== 技术指标 ===
RSI: {ta['rsi']} ({'超卖' if ta['rsi'] < 30 else '超买' if ta['rsi'] > 70 else '中性'})
SMA-20: ${ta['sma_20']:.2f}
SMA-50: ${ta['sma_50']:.2f}
MACD: {ta['macd']} (信号: {ta['macd_signal']})

=== 市场情绪指标 ===
恐惧贪婪指数: {sa.get('fear_greed', {}).get('value', 'N/A')} - {sa.get('fear_greed', {}).get('classification', 'N/A')}
情绪推荐: {sa.get('fear_greed_recommendation', 'N/A')}
AHR999指数: {sa.get('ahr999') if sa.get('ahr999') is not None else 'N/A':.3f}
AHR999推荐: {sa.get('ahr999_recommendation', 'N/A')}

今日无明确买卖信号，建议继续观察。
        """
        return overview_message.strip()

# 示例使用
if __name__ == "__main__":
    strategy = EnhancedBitcoinTradingStrategy()
    
    print("正在获取增强版市场分析...")
    result = check_enhanced_daily_signals()
    print(result)