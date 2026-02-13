#!/usr/bin/env python3
"""
技术分析指标工具 - Technical Analysis Toolkit
计算移动平均线、RSI、MACD、布林带等常用技术指标

用法:
    python technical_analysis.py --symbol MSFT --days 90
    python technical_analysis.py --symbol 700.HK --days 60 --output json
    python technical_analysis.py --symbol MSFT --demo  # 演示模式(使用模拟数据)
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import numpy as np
    import pandas as pd
except ImportError:
    print("❌ 需要安装依赖: pip3 install pandas numpy")
    sys.exit(1)

# 尝试导入 LongPort SDK
LONGPORT_AVAILABLE = False
try:
    from longport.openapi import QuoteContext, Config, Period
    LONGPORT_AVAILABLE = True
except ImportError:
    pass

# 尝试导入 yfinance 作为备选
YFINANCE_AVAILABLE = False
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    pass


class TechnicalAnalyzer:
    """技术分析指标计算器"""
    
    def __init__(self, use_demo: bool = False):
        self.use_demo = use_demo
        self.ctx = None
        
        if not use_demo and LONGPORT_AVAILABLE:
            try:
                self.config = Config.from_env()
                self.ctx = QuoteContext(self.config)
            except Exception as e:
                print(f"⚠️  LongPort API 配置失败: {e}")
                print(f"💡 将使用备选数据源或演示模式")
                self.ctx = None
    
    def get_historical_data(self, symbol: str, period: str = "1d", 
                           count: int = 100) -> pd.DataFrame:
        """
        获取历史K线数据
        
        优先级:
        1. LongPort API (如果配置正确)
        2. Yahoo Finance (如果安装 yfinance)
        3. 模拟数据 (演示模式)
        
        Args:
            symbol: 股票代码 (如 'MSFT', '700.HK')
            period: K线周期 ("1d", "1wk", etc.)
            count: 获取的K线数量
        
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        # 尝试 LongPort API
        if self.ctx and LONGPORT_AVAILABLE and not self.use_demo:
            df = self._get_longport_data(symbol, count)
            if not df.empty:
                return df
        
        # 尝试 Yahoo Finance
        if YFINANCE_AVAILABLE and not self.use_demo:
            df = self._get_yfinance_data(symbol, period, count)
            if not df.empty:
                return df
        
        # 使用模拟数据
        print(f"📊 使用演示模式生成 {symbol} 的模拟数据...")
        return self._generate_demo_data(symbol, count)
    
    def _get_longport_data(self, symbol: str, count: int) -> pd.DataFrame:
        """从 LongPort API 获取数据"""
        # 转换 symbol 格式
        if '.' not in symbol and not symbol.endswith('.US'):
            if symbol.isalpha():
                symbol = f"{symbol}.US"
        
        try:
            candles = self.ctx.history_candles(symbol, period=Period.Day, count=count)
        except Exception as e:
            return pd.DataFrame()
        
        if not candles:
            return pd.DataFrame()
        
        data = []
        for candle in candles:
            data.append({
                'date': candle.timestamp,
                'open': float(candle.open),
                'high': float(candle.high),
                'low': float(candle.low),
                'close': float(candle.close),
                'volume': int(candle.volume)
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def _get_yfinance_data(self, symbol: str, period: str, count: int) -> pd.DataFrame:
        """从 Yahoo Finance 获取数据"""
        # 转换 symbol 格式
        yf_symbol = symbol
        if symbol.endswith('.HK'):
            yf_symbol = symbol.replace('.HK', '.HK')
        elif '.' not in symbol:
            # 美股
            pass
        
        try:
            # 计算开始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=count * 2)  # 多一些余量
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(start=start_date, end=end_date, interval=period)
            
            if hist.empty:
                return pd.DataFrame()
            
            df = pd.DataFrame({
                'date': hist.index,
                'open': hist['Open'].values,
                'high': hist['High'].values,
                'low': hist['Low'].values,
                'close': hist['Close'].values,
                'volume': hist['Volume'].values
            })
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # 限制数量
            if len(df) > count:
                df = df.tail(count).reset_index(drop=True)
            
            return df
            
        except Exception as e:
            return pd.DataFrame()
    
    def _generate_demo_data(self, symbol: str, count: int, 
                           start_price: float = 100.0) -> pd.DataFrame:
        """生成模拟的股价数据用于演示"""
        np.random.seed(hash(symbol) % 2**32)  # 使相同symbol生成相同序列
        
        dates = pd.date_range(end=datetime.now(), periods=count, freq='D')
        dates = dates[dates.dayofweek < 5]  # 只保留工作日
        
        # 生成随机游走价格
        returns = np.random.normal(0.0005, 0.02, len(dates))  # 均值0.05%, 标准差2%
        prices = start_price * np.exp(np.cumsum(returns))
        
        # 生成OHLC数据
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            volatility = 0.015
            high = close * (1 + abs(np.random.normal(0, volatility)))
            low = close * (1 - abs(np.random.normal(0, volatility)))
            open_price = prices[i-1] if i > 0 else close
            volume = int(np.random.normal(10000000, 3000000))
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': max(volume, 1000000)
            })
        
        return pd.DataFrame(data)
    
    def calculate_ma(self, df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """计算移动平均线 (Moving Average)"""
        for period in periods:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    def calculate_ema(self, df: pd.DataFrame, periods: List[int] = [12, 26]) -> pd.DataFrame:
        """计算指数移动平均线 (Exponential Moving Average)"""
        for period in periods:
            df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算 RSI (Relative Strength Index)
        RSI = 100 - (100 / (1 + RS))
        RS = 平均上涨 / 平均下跌
        """
        delta = df['close'].diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        # 计算平均上涨和平均下跌
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # 计算 RS 和 RSI
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, 
                       signal: int = 9) -> pd.DataFrame:
        """
        计算 MACD (Moving Average Convergence Divergence)
        MACD Line = EMA(12) - EMA(26)
        Signal Line = EMA(9) of MACD Line
        Histogram = MACD Line - Signal Line
        """
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    def calculate_bollinger(self, df: pd.DataFrame, period: int = 20, 
                           std_dev: float = 2.0) -> pd.DataFrame:
        """
        计算布林带 (Bollinger Bands)
        中轨 = MA(20)
        上轨 = MA(20) + 2 * 标准差
        下轨 = MA(20) - 2 * 标准差
        """
        df['BB_Middle'] = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * std_dev)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Percent'] = (df['close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        return df
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算 ATR (Average True Range) - 平均真实波幅
        用于衡量波动性
        """
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=period).mean()
        
        return df
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算成交量相关指标"""
        # 成交量移动平均
        df['Volume_MA20'] = df['volume'].rolling(window=20).mean()
        
        # 成交量比率 (当前成交量 / 20日均量)
        df['Volume_Ratio'] = df['volume'] / df['Volume_MA20']
        
        # OBV (On Balance Volume)
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        df['OBV'] = obv
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> Dict:
        """
        基于技术指标生成交易信号
        """
        if df.empty or len(df) < 30:
            return {"error": "数据不足，无法生成信号"}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        signals = {
            "timestamp": datetime.now().isoformat(),
            "price": {
                "current": round(latest['close'], 2),
                "open": round(latest['open'], 2),
                "high": round(latest['high'], 2),
                "low": round(latest['low'], 2),
                "volume": int(latest['volume'])
            },
            "moving_averages": {},
            "rsi": {},
            "macd": {},
            "bollinger": {},
            "overall_signal": "NEUTRAL",
            "confidence": 0
        }
        
        # 移动平均线信号
        ma_signals = []
        if 'MA5' in latest and 'MA20' in latest:
            signals['moving_averages']['MA5'] = round(latest['MA5'], 2)
            signals['moving_averages']['MA20'] = round(latest['MA20'], 2)
            signals['moving_averages']['MA60'] = round(latest.get('MA60', 0), 2)
            
            if latest['MA5'] > latest['MA20']:
                ma_signals.append("BULLISH")  # 金叉趋势
            else:
                ma_signals.append("BEARISH")  # 死叉趋势
            
            # 价格在MA上方还是下方
            if latest['close'] > latest['MA20']:
                signals['moving_averages']['trend'] = "ABOVE_MA20"
            else:
                signals['moving_averages']['trend'] = "BELOW_MA20"
        
        # RSI 信号
        if 'RSI' in latest and not pd.isna(latest['RSI']):
            rsi = latest['RSI']
            signals['rsi']['value'] = round(rsi, 2)
            
            if rsi > 70:
                signals['rsi']['signal'] = "OVERBOUGHT"
                signals['rsi']['suggestion'] = "考虑卖出"
            elif rsi < 30:
                signals['rsi']['signal'] = "OVERSOLD"
                signals['rsi']['suggestion'] = "考虑买入"
            else:
                signals['rsi']['signal'] = "NEUTRAL"
                signals['rsi']['suggestion'] = "观望"
        
        # MACD 信号
        if 'MACD' in latest and not pd.isna(latest['MACD']):
            signals['macd']['macd'] = round(latest['MACD'], 4)
            signals['macd']['signal'] = round(latest['MACD_Signal'], 4)
            signals['macd']['histogram'] = round(latest['MACD_Histogram'], 4)
            
            # MACD 金叉/死叉
            if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
                signals['macd']['cross'] = "GOLDEN_CROSS"
                signals['macd']['suggestion'] = "买入信号"
            elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
                signals['macd']['cross'] = "DEAD_CROSS"
                signals['macd']['suggestion'] = "卖出信号"
            elif latest['MACD'] > latest['MACD_Signal']:
                signals['macd']['cross'] = "ABOVE_SIGNAL"
                signals['macd']['suggestion'] = "多头趋势"
            else:
                signals['macd']['cross'] = "BELOW_SIGNAL"
                signals['macd']['suggestion'] = "空头趋势"
        
        # 布林带信号
        if 'BB_Upper' in latest and not pd.isna(latest['BB_Upper']):
            signals['bollinger']['upper'] = round(latest['BB_Upper'], 2)
            signals['bollinger']['middle'] = round(latest['BB_Middle'], 2)
            signals['bollinger']['lower'] = round(latest['BB_Lower'], 2)
            signals['bollinger']['percent'] = round(latest['BB_Percent'] * 100, 2)
            
            if latest['close'] > latest['BB_Upper']:
                signals['bollinger']['position'] = "ABOVE_UPPER"
                signals['bollinger']['suggestion'] = "超买区域"
            elif latest['close'] < latest['BB_Lower']:
                signals['bollinger']['position'] = "BELOW_LOWER"
                signals['bollinger']['suggestion'] = "超卖区域"
            else:
                signals['bollinger']['position'] = "WITHIN_BANDS"
                signals['bollinger']['suggestion'] = "正常区间"
        
        # 综合评分
        score = 0
        factors = 0
        
        # MA 评分
        if ma_signals:
            score += 1 if ma_signals[0] == "BULLISH" else -1
            factors += 1
        
        # RSI 评分
        if 'RSI' in latest and not pd.isna(latest['RSI']):
            if latest['RSI'] < 30:
                score += 1  # 超卖，可能反弹
            elif latest['RSI'] > 70:
                score -= 1  # 超买，可能回调
            factors += 1
        
        # MACD 评分
        if 'MACD' in latest and not pd.isna(latest['MACD']):
            if latest['MACD'] > latest['MACD_Signal']:
                score += 1
            else:
                score -= 1
            factors += 1
        
        # 布林带评分
        if 'BB_Percent' in latest and not pd.isna(latest['BB_Percent']):
            if latest['BB_Percent'] < 0.1:
                score += 1  # 接近下轨，可能反弹
            elif latest['BB_Percent'] > 0.9:
                score -= 1  # 接近上轨，可能回调
            factors += 1
        
        # 确定总体信号
        if factors > 0:
            normalized_score = score / factors
            signals['score'] = round(normalized_score, 2)
            
            if normalized_score > 0.3:
                signals['overall_signal'] = "BULLISH"
                signals['suggestion'] = "看多"
            elif normalized_score < -0.3:
                signals['overall_signal'] = "BEARISH"
                signals['suggestion'] = "看空"
            else:
                signals['overall_signal'] = "NEUTRAL"
                signals['suggestion'] = "观望"
            
            signals['confidence'] = round(abs(normalized_score) * 100, 1)
        
        return signals
    
    def analyze(self, symbol: str, days: int = 90, output_format: str = "text") -> str:
        """
        执行完整的技术分析
        
        Args:
            symbol: 股票代码
            days: 分析天数
            output_format: 输出格式 (text, json)
        """
        print(f"📊 正在分析 {symbol} 的技术指标...")
        print(f"📅 获取近 {days} 天历史数据...")
        
        # 获取历史数据 (需要多一些数据用于计算指标)
        df = self.get_historical_data(symbol, count=days + 60)
        
        if df.empty:
            return json.dumps({"error": f"无法获取 {symbol} 的数据"}) if output_format == "json" else f"❌ 无法获取 {symbol} 的数据"
        
        print(f"✅ 获取到 {len(df)} 条数据")
        
        # 计算指标
        print("🔄 计算技术指标...")
        df = self.calculate_ma(df)
        df = self.calculate_ema(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_bollinger(df)
        df = self.calculate_atr(df)
        df = self.calculate_volume_indicators(df)
        
        # 截取最近的数据
        df_recent = df.tail(days).reset_index(drop=True)
        
        # 生成信号
        signals = self.generate_signals(df_recent)
        
        if output_format == "json":
            return json.dumps(signals, indent=2, ensure_ascii=False)
        
        # 文本格式输出
        output = []
        output.append("=" * 65)
        output.append(f"📈 {symbol} 技术分析报告")
        output.append("=" * 65)
        output.append(f"\n📅 分析时间: {signals['timestamp'][:19]}")
        output.append(f"💰 当前价格: ${signals['price']['current']}")
        output.append(f"📊 成交量: {signals['price']['volume']:,}")
        
        # 移动平均线
        if signals['moving_averages']:
            output.append(f"\n📈 移动平均线:")
            ma = signals['moving_averages']
            output.append(f"   MA5:  ${ma.get('MA5', 'N/A'):>8}")
            output.append(f"   MA20: ${ma.get('MA20', 'N/A'):>8}")
            output.append(f"   MA60: ${ma.get('MA60', 'N/A'):>8}")
            output.append(f"   趋势: {ma.get('trend', 'N/A')}")
        
        # RSI
        if signals['rsi']:
            output.append(f"\n⚡ RSI指标:")
            rsi = signals['rsi']
            output.append(f"   数值: {rsi.get('value', 'N/A')}")
            output.append(f"   信号: {rsi.get('signal', 'N/A')}")
            output.append(f"   建议: {rsi.get('suggestion', 'N/A')}")
        
        # MACD
        if signals['macd']:
            output.append(f"\n🔄 MACD指标:")
            macd = signals['macd']
            output.append(f"   MACD: {macd.get('macd', 'N/A')}")
            output.append(f"   信号线: {macd.get('signal', 'N/A')}")
            output.append(f"   柱状图: {macd.get('histogram', 'N/A')}")
            output.append(f"   交叉: {macd.get('cross', 'N/A')}")
            output.append(f"   建议: {macd.get('suggestion', 'N/A')}")
        
        # 布林带
        if signals['bollinger']:
            output.append(f"\n📊 布林带:")
            bb = signals['bollinger']
            output.append(f"   上轨: ${bb.get('upper', 'N/A')}")
            output.append(f"   中轨: ${bb.get('middle', 'N/A')}")
            output.append(f"   下轨: ${bb.get('lower', 'N/A')}")
            output.append(f"   位置: {bb.get('percent', 'N/A')}%")
            output.append(f"   状态: {bb.get('suggestion', 'N/A')}")
        
        # 综合信号
        output.append(f"\n" + "=" * 65)
        output.append(f"🎯 综合评估")
        output.append(f"=" * 65)
        
        signal_icon = {
            "BULLISH": "🟢 看多",
            "BEARISH": "🔴 看空",
            "NEUTRAL": "⚪ 观望"
        }
        
        output.append(f"\n总体信号: {signal_icon.get(signals['overall_signal'], signals['overall_signal'])}")
        output.append(f"置信度: {signals['confidence']}%")
        if 'score' in signals:
            output.append(f"评分: {signals['score']}")
        output.append(f"建议: {signals.get('suggestion', 'N/A')}")
        
        if self.use_demo:
            output.append(f"\n⚠️  注意: 当前使用演示模式(模拟数据)")
        
        output.append("=" * 65)
        
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='技术分析指标工具')
    parser.add_argument('--symbol', '-s', required=True, help='股票代码 (如 MSFT, 700.HK)')
    parser.add_argument('--days', '-d', type=int, default=90, help='分析天数 (默认: 90)')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text', 
                       help='输出格式 (默认: text)')
    parser.add_argument('--demo', action='store_true', 
                       help='演示模式(使用模拟数据，无需API)')
    parser.add_argument('--save', help='保存结果到文件')
    
    args = parser.parse_args()
    
    # 创建分析器并执行分析
    analyzer = TechnicalAnalyzer(use_demo=args.demo)
    result = analyzer.analyze(args.symbol, args.days, args.output)
    
    print(result)
    
    # 保存到文件
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n💾 结果已保存到: {args.save}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
