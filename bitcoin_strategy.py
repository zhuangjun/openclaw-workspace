import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Tuple

class BitcoinTradingStrategy:
    """
    A Bitcoin trading strategy that analyzes daily price data to generate buy/sell signals
    """
    
    def __init__(self):
        self.api_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        self.signals = []
        
    def get_bitcoin_data(self, days: int = 365) -> pd.DataFrame:
        """
        Fetch Bitcoin price data from CoinGecko API
        """
        url = f"{self.api_url}?vs_currency=usd&days={days}&interval=daily"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Convert to DataFrame
            prices = [item[1] for item in data['prices']]
            timestamps = [datetime.fromtimestamp(item[0]/1000) for item in data['prices']]
            
            df = pd.DataFrame({
                'timestamp': timestamps,
                'price': prices
            })
            
            return df
        except Exception as e:
            print(f"Error fetching Bitcoin data: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for trading signals
        """
        # Simple Moving Averages
        df['sma_20'] = df['price'].rolling(window=20).mean()
        df['sma_50'] = df['price'].rolling(window=50).mean()
        
        # Exponential Moving Average
        df['ema_12'] = df['price'].ewm(span=12).mean()
        df['ema_26'] = df['price'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI (Relative Strength Index)
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['price'].rolling(window=20).mean()
        bb_std = df['price'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volume (we'll simulate volume based on price changes for now)
        df['volume'] = abs(df['price'].diff()) * 1000000  # Simulated volume
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> List[Dict]:
        """
        Generate buy/sell signals based on technical indicators
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
            
            # Buy signals
            if (
                # Price crossing above SMA-20
                previous['price'] <= previous['sma_20'] and current['price'] > current['sma_20'] and
                # RSI showing oversold condition
                current['rsi'] < 35 and
                # MACD bullish crossover
                previous['macd'] <= previous['macd_signal'] and current['macd'] > current['macd_signal']
            ):
                signal['signal'] = 'BUY'
                signal['reason'] = 'Price above SMA-20, RSI oversold, MACD bullish'
            
            # Additional buy condition: RSI divergence
            elif current['rsi'] < 30 and current['price'] < current['bb_lower']:
                signal['signal'] = 'BUY'
                signal['reason'] = 'RSI oversold + Price near lower Bollinger Band'
                
            # Sell signals
            elif (
                # Price crossing below SMA-20
                previous['price'] >= previous['sma_20'] and current['price'] < current['sma_20'] and
                # RSI showing overbought condition
                current['rsi'] > 65 and
                # MACD bearish crossover
                previous['macd'] >= previous['macd_signal'] and current['macd'] < current['macd_signal']
            ):
                signal['signal'] = 'SELL'
                signal['reason'] = 'Price below SMA-20, RSI overbought, MACD bearish'
                
            # Additional sell condition: RSI divergence
            elif current['rsi'] > 70 and current['price'] > current['bb_upper']:
                signal['signal'] = 'SELL'
                signal['reason'] = 'RSI overbought + Price near upper Bollinger Band'
            
            if signal['signal']:
                signals.append(signal)
        
        return signals
    
    def get_latest_signal(self) -> Dict:
        """
        Get the most recent buy/sell signal
        """
        df = self.get_bitcoin_data(days=90)  # Get 3 months of data
        if df.empty:
            return {'error': 'Could not fetch data'}
        
        df = self.calculate_indicators(df)
        signals = self.generate_signals(df)
        
        if signals:
            return signals[-1]  # Return the latest signal
        else:
            # Even if no explicit buy/sell signal, return current market state
            latest_data = df.iloc[-1]
            return {
                'date': latest_data['timestamp'],
                'price': latest_data['price'],
                'rsi': latest_data['rsi'],
                'sma_20': latest_data['sma_20'],
                'sma_50': latest_data['sma_50'],
                'macd': latest_data['macd'],
                'signal': 'HOLD',
                'reason': 'No clear buy/sell signal at this time'
            }
    
    def analyze_market(self) -> Dict:
        """
        Perform comprehensive market analysis
        """
        df = self.get_bitcoin_data(days=180)  # 6 months of data
        if df.empty:
            return {'error': 'Could not fetch data'}
        
        df = self.calculate_indicators(df)
        signals = self.generate_signals(df)
        
        # Get latest values
        latest = df.iloc[-1]
        
        analysis = {
            'current_price': latest['price'],
            'date': latest['timestamp'],
            'rsi': round(latest['rsi'], 2),
            'sma_20': round(latest['sma_20'], 2) if not pd.isna(latest['sma_20']) else None,
            'sma_50': round(latest['sma_50'], 2) if not pd.isna(latest['sma_50']) else None,
            'macd': round(latest['macd'], 4),
            'macd_signal': round(latest['macd_signal'], 4),
            'bb_upper': round(latest['bb_upper'], 2),
            'bb_lower': round(latest['bb_lower'], 2),
            'latest_signal': signals[-1] if signals else None,
            'recent_signals': signals[-5:] if len(signals) >= 5 else signals  # Last 5 signals
        }
        
        return analysis

def check_daily_signals():
    """
    Function to check for daily signals and send alerts
    """
    strategy = BitcoinTradingStrategy()
    latest_signal = strategy.get_latest_signal()
    
    if 'error' in latest_signal:
        return f"Error: {latest_signal['error']}"
    
    if latest_signal['signal'] in ['BUY', 'SELL']:
        alert_message = f"""
🚨 BITCOIN TRADING ALERT 🚨

Date: {latest_signal['date'].strftime('%Y-%m-%d')}
Signal: {latest_signal['signal']}
Price: ${latest_signal['price']:.2f}
Reason: {latest_signal['reason']}

Consider taking action based on your trading strategy!
        """
        return alert_message.strip()
    else:
        # Provide market overview even if no signal
        analysis = strategy.analyze_market()
        if 'error' in analysis:
            return f"Market Overview Error: {analysis['error']}"
        
        # Format the overview message with proper handling of potential None values
        sma_20_str = f"${analysis['sma_20']:.2f}" if analysis['sma_20'] is not None else "N/A"
        sma_50_str = f"${analysis['sma_50']:.2f}" if analysis['sma_50'] is not None else "N/A"
        
        overview_message = f"""
📈 BITCOIN DAILY MARKET OVERVIEW 📈

Date: {analysis['date'].strftime('%Y-%m-%d')}
Current Price: ${analysis['current_price']:.2f}
RSI: {analysis['rsi']} ({'Oversold' if analysis['rsi'] < 30 else 'Overbought' if analysis['rsi'] > 70 else 'Neutral'})
SMA-20: {sma_20_str}
SMA-50: {sma_50_str}
MACD: {analysis['macd']} (Signal: {analysis['macd_signal']})

Status: No immediate buy/sell signal at this time
        """
        return overview_message.strip()

# Example usage
if __name__ == "__main__":
    strategy = BitcoinTradingStrategy()
    
    # Print current market analysis
    analysis = strategy.analyze_market()
    print("Current Market Analysis:")
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    print("\nChecking for signals...")
    result = check_daily_signals()
    print(result)