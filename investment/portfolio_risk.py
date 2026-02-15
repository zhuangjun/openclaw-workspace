#!/usr/bin/env python3
"""
投资组合风险分析工具 - Portfolio Risk Analysis Toolkit
计算 VaR、最大回撤、夏普比率、波动率等风险指标

用法:
    python portfolio_risk.py --symbol MSFT --days 252
    python portfolio_risk.py --portfolio-file data/portfolio.json
    python portfolio_risk.py --symbol MSFT --confidence 0.95 --method all
"""

import argparse
import json
import sys
import os
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict

try:
    import numpy as np
    import pandas as pd
    from scipy import stats
except ImportError:
    print("❌ 需要安装依赖: pip3 install pandas numpy scipy")
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


@dataclass
class RiskMetrics:
    """风险指标数据类"""
    symbol: str
    start_date: str
    end_date: str
    trading_days: int
    
    # 收益指标
    total_return: float  # 总收益率
    annualized_return: float  # 年化收益率
    daily_mean_return: float  # 日均收益率
    
    # 风险指标
    daily_volatility: float  # 日波动率
    annualized_volatility: float  # 年化波动率
    downside_volatility: float  # 下行波动率 (只计算负收益)
    
    # 调整收益指标
    sharpe_ratio: float  # 夏普比率
    sortino_ratio: float  # 索提诺比率 (只惩罚下行风险)
    calmar_ratio: float  # 卡玛比率 (收益/最大回撤)
    
    # 回撤指标
    max_drawdown: float  # 最大回撤
    max_drawdown_duration: int  # 最大回撤持续天数
    avg_drawdown: float  # 平均回撤
    
    # VaR 指标
    var_95: float  # 95% 置信度 VaR
    var_99: float  # 99% 置信度 VaR
    cvar_95: float  # 95% 置信度 CVaR (条件VaR/预期亏损)
    cvar_99: float  # 99% 置信度 CVaR
    
    # 分布特征
    skewness: float  # 偏度
    kurtosis: float  # 峰度
    jarque_bera_pvalue: float  # Jarque-Bera 正态性检验 p-value
    is_normal: bool  # 是否服从正态分布
    
    # 其他指标
    var_parametric_95: float  # 参数法 VaR (假设正态分布)
    var_cornish_fisher_95: float  # Cornish-Fisher VaR (修正偏度峰度)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        d = asdict(self)
        # 转换 numpy bool 为 Python bool
        d['is_normal'] = bool(d['is_normal'])
        return d
    
    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class RiskAnalyzer:
    """风险分析器"""
    
    # 无风险利率 (年化，使用美国国债收益率)
    RISK_FREE_RATE = 0.045  # 4.5%
    
    # 一年交易天数
    TRADING_DAYS = 252
    
    def __init__(self, use_demo: bool = False, risk_free_rate: Optional[float] = None):
        self.use_demo = use_demo
        self.ctx = None
        self.risk_free_rate = risk_free_rate or self.RISK_FREE_RATE
        
        if not use_demo and LONGPORT_AVAILABLE:
            try:
                self.config = Config.from_env()
                self.ctx = QuoteContext(self.config)
            except Exception as e:
                print(f"⚠️  LongPort API 配置失败: {e}")
                self.ctx = None
    
    def get_historical_data(self, symbol: str, days: int = 252) -> pd.DataFrame:
        """获取历史价格数据"""
        # 转换 symbol 格式
        api_symbol = symbol
        if '.' not in symbol and not symbol.endswith('.US'):
            if symbol.isalpha():
                api_symbol = f"{symbol}.US"
        
        # 尝试 LongPort API
        if self.ctx and LONGPORT_AVAILABLE and not self.use_demo:
            df = self._get_longport_data(api_symbol, days)
            if not df.empty and len(df) >= days * 0.8:
                return df
        
        # 尝试 Yahoo Finance
        if YFINANCE_AVAILABLE and not self.use_demo:
            df = self._get_yfinance_data(symbol, days)
            if not df.empty and len(df) >= days * 0.8:
                return df
        
        # 使用模拟数据
        print(f"📊 使用演示模式生成 {symbol} 的模拟数据...")
        return self._generate_demo_data(symbol, days)
    
    def _get_longport_data(self, symbol: str, count: int) -> pd.DataFrame:
        """从 LongPort API 获取数据"""
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
    
    def _get_yfinance_data(self, symbol: str, days: int) -> pd.DataFrame:
        """从 Yahoo Finance 获取数据"""
        yf_symbol = symbol
        if symbol.endswith('.HK'):
            yf_symbol = symbol
        elif '.' not in symbol and not symbol.isdigit():
            pass  # 美股直接使用
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days * 2)
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(start=start_date, end=end_date, interval='1d')
            
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
            
            # 限制数据量
            if len(df) > days:
                df = df.tail(days).reset_index(drop=True)
            
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def _generate_demo_data(self, symbol: str, days: int, 
                           annual_return: float = 0.10,
                           volatility: float = 0.25) -> pd.DataFrame:
        """生成模拟价格数据"""
        np.random.seed(hash(symbol) % 2**32)
        
        # 生成随机收益率
        daily_return = annual_return / self.TRADING_DAYS
        daily_vol = volatility / math.sqrt(self.TRADING_DAYS)
        
        returns = np.random.normal(daily_return, daily_vol, days)
        
        # 根据标的调整参数
        if symbol in ['BTC', 'ETH']:
            returns = np.random.normal(daily_return * 2, daily_vol * 2.5, days)
        elif symbol in ['GLD', 'XLU']:
            returns = np.random.normal(daily_return * 0.3, daily_vol * 0.5, days)
        
        # 计算价格序列
        start_price = 100
        prices = [start_price]
        for r in returns:
            prices.append(prices[-1] * (1 + r))
        prices = prices[1:]
        
        # 生成日期
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'close': prices,
            'volume': [int(np.random.uniform(1000000, 10000000)) for _ in prices]
        })
        
        return df
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.Series:
        """计算日收益率"""
        returns = df['close'].pct_change().dropna()
        return returns
    
    def calculate_var_historical(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        计算历史模拟法 VaR
        
        Args:
            returns: 收益率序列
            confidence: 置信度 (如 0.95 表示 95% 置信度)
        
        Returns:
            VaR 值 (负值表示损失)
        """
        return np.percentile(returns, (1 - confidence) * 100)
    
    def calculate_var_parametric(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        计算参数法 VaR (假设正态分布)
        
        VaR = μ - z * σ
        其中 z 是标准正态分布的分位数
        """
        mean = returns.mean()
        std = returns.std()
        z_score = stats.norm.ppf(1 - confidence)
        return mean + z_score * std
    
    def calculate_var_cornish_fisher(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        计算 Cornish-Fisher VaR
        修正正态分布假设，考虑偏度和峰度
        """
        mean = returns.mean()
        std = returns.std()
        skew = returns.skew()
        kurt = returns.kurtosis()
        
        z_score = stats.norm.ppf(1 - confidence)
        
        # Cornish-Fisher 修正
        z_cf = (z_score + 
                (z_score**2 - 1) * skew / 6 +
                (z_score**3 - 3 * z_score) * kurt / 24 -
                (2 * z_score**3 - 5 * z_score) * skew**2 / 36)
        
        return mean + z_cf * std
    
    def calculate_cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        计算 CVaR (条件VaR / 预期亏损)
        CVaR 是超过 VaR 阈值的平均损失
        """
        var = self.calculate_var_historical(returns, confidence)
        return returns[returns <= var].mean()
    
    def calculate_max_drawdown(self, prices: pd.Series) -> Tuple[float, int]:
        """
        计算最大回撤
        
        Returns:
            (最大回撤值, 最大回撤持续天数)
        """
        # 计算累计收益
        cumulative = (1 + prices.pct_change().fillna(0)).cumprod()
        
        # 计算历史最高点
        running_max = cumulative.expanding().max()
        
        # 计算回撤
        drawdown = (cumulative - running_max) / running_max
        
        # 最大回撤
        max_dd = drawdown.min()
        
        # 计算最大回撤持续天数
        is_in_drawdown = drawdown < 0
        max_duration = 0
        current_duration = 0
        
        for in_dd in is_in_drawdown:
            if in_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return max_dd, max_duration
    
    def calculate_downside_volatility(self, returns: pd.Series) -> float:
        """
        计算下行波动率 (只考虑负收益)
        """
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return 0
        return downside_returns.std()
    
    def analyze_symbol(self, symbol: str, days: int = 252) -> RiskMetrics:
        """
        分析单个资产的风险指标
        """
        # 获取数据
        df = self.get_historical_data(symbol, days)
        
        if df.empty or len(df) < 30:
            raise ValueError(f"无法获取 {symbol} 的足够历史数据")
        
        # 计算收益率
        returns = self.calculate_returns(df)
        prices = df['close']
        
        # 基础统计
        trading_days = len(returns)
        total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
        daily_mean = returns.mean()
        annualized_return = (1 + daily_mean) ** self.TRADING_DAYS - 1
        
        # 波动率
        daily_vol = returns.std()
        annualized_vol = daily_vol * math.sqrt(self.TRADING_DAYS)
        downside_vol = self.calculate_downside_volatility(returns)
        
        # 调整收益指标
        excess_return = annualized_return - self.risk_free_rate
        sharpe = excess_return / annualized_vol if annualized_vol > 0 else 0
        
        downside_vol_annual = downside_vol * math.sqrt(self.TRADING_DAYS)
        sortino = excess_return / downside_vol_annual if downside_vol_annual > 0 else 0
        
        # 回撤
        max_dd, max_dd_duration = self.calculate_max_drawdown(prices)
        
        # 计算所有回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdowns = (cumulative - running_max) / running_max
        avg_dd = drawdowns[drawdowns < 0].mean() if (drawdowns < 0).any() else 0
        
        calmar = annualized_return / abs(max_dd) if max_dd != 0 else 0
        
        # VaR 计算
        var_95 = self.calculate_var_historical(returns, 0.95)
        var_99 = self.calculate_var_historical(returns, 0.99)
        cvar_95 = self.calculate_cvar(returns, 0.95)
        cvar_99 = self.calculate_cvar(returns, 0.99)
        
        # 参数法 VaR
        var_parametric = self.calculate_var_parametric(returns, 0.95)
        var_cf = self.calculate_var_cornish_fisher(returns, 0.95)
        
        # 分布特征
        skew = returns.skew()
        kurt = returns.kurtosis()
        
        # Jarque-Bera 正态性检验
        jb_stat = len(returns) / 6 * (skew**2 + (kurt**2) / 4)
        jb_pvalue = 1 - stats.chi2.cdf(jb_stat, 2)
        is_normal = jb_pvalue > 0.05
        
        return RiskMetrics(
            symbol=symbol,
            start_date=df['date'].iloc[0].strftime('%Y-%m-%d'),
            end_date=df['date'].iloc[-1].strftime('%Y-%m-%d'),
            trading_days=trading_days,
            total_return=round(total_return, 4),
            annualized_return=round(annualized_return, 4),
            daily_mean_return=round(daily_mean, 6),
            daily_volatility=round(daily_vol, 6),
            annualized_volatility=round(annualized_vol, 4),
            downside_volatility=round(downside_vol, 6),
            sharpe_ratio=round(sharpe, 4),
            sortino_ratio=round(sortino, 4),
            calmar_ratio=round(calmar, 4),
            max_drawdown=round(max_dd, 4),
            max_drawdown_duration=max_dd_duration,
            avg_drawdown=round(avg_dd, 4),
            var_95=round(var_95, 6),
            var_99=round(var_99, 6),
            cvar_95=round(cvar_95, 6),
            cvar_99=round(cvar_99, 6),
            skewness=round(skew, 4),
            kurtosis=round(kurt, 4),
            jarque_bera_pvalue=round(jb_pvalue, 6),
            is_normal=is_normal,
            var_parametric_95=round(var_parametric, 6),
            var_cornish_fisher_95=round(var_cf, 6)
        )
    
    def analyze_portfolio(self, portfolio_file: str, days: int = 252) -> Dict:
        """
        分析整个投资组合的风险
        """
        with open(portfolio_file, 'r') as f:
            portfolio = json.load(f)
        
        results = []
        symbols = []
        weights = []
        positions = []
        
        total_value = portfolio.get('summary', {}).get('current_value', 0)
        
        # 提取持仓
        for category, data in portfolio.get('allocation', {}).items():
            if category == 'cash':
                continue
            for pos in data.get('positions', []):
                symbol = pos['symbol']
                weight = pos.get('value', 0) / total_value if total_value > 0 else 0
                if weight > 0:
                    symbols.append(symbol)
                    weights.append(weight)
                    positions.append(pos)
        
        # 归一化权重
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        
        # 获取每个资产的风险指标
        returns_matrix = []
        valid_symbols = []
        valid_weights = []
        valid_positions = []
        
        for i, symbol in enumerate(symbols):
            try:
                metrics = self.analyze_symbol(symbol, days)
                results.append(metrics)
                valid_symbols.append(symbol)
                valid_weights.append(weights[i])
                valid_positions.append(positions[i])
                
                # 获取收益率序列用于组合计算
                df = self.get_historical_data(symbol, days)
                returns = self.calculate_returns(df)
                returns_matrix.append(returns.values)
            except Exception as e:
                print(f"⚠️ 分析 {symbol} 失败: {e}")
        
        # 重新归一化有效权重
        total_valid_weight = sum(valid_weights)
        if total_valid_weight > 0:
            valid_weights = [w / total_valid_weight for w in valid_weights]
        
        # 计算组合风险
        portfolio_metrics = self._calculate_portfolio_metrics(
            valid_symbols, valid_weights, returns_matrix, results
        )
        
        return {
            'individual': [r.to_dict() for r in results],
            'portfolio': portfolio_metrics
        }
    
    def _calculate_portfolio_metrics(self, symbols: List[str], weights: List[float],
                                     returns_matrix: List[np.ndarray],
                                     individual_metrics: List[RiskMetrics]) -> Dict:
        """计算组合层面的风险指标"""
        
        if not returns_matrix or len(returns_matrix) < 2:
            return {}
        
        # 构建收益率矩阵
        min_len = min(len(r) for r in returns_matrix)
        aligned_returns = np.array([r[-min_len:] for r in returns_matrix])
        
        # 计算加权组合收益率
        weights_array = np.array(weights)
        portfolio_returns = np.dot(weights_array, aligned_returns)
        
        # 组合波动率
        portfolio_vol = np.std(portfolio_returns) * math.sqrt(self.TRADING_DAYS)
        
        # 组合年化收益
        portfolio_annual_return = np.mean(portfolio_returns) * self.TRADING_DAYS
        
        # 组合夏普比率
        excess_return = portfolio_annual_return - self.risk_free_rate
        portfolio_sharpe = excess_return / portfolio_vol if portfolio_vol > 0 else 0
        
        # 组合 VaR
        portfolio_var_95 = np.percentile(portfolio_returns, 5)
        portfolio_var_99 = np.percentile(portfolio_returns, 1)
        portfolio_cvar_95 = portfolio_returns[portfolio_returns <= portfolio_var_95].mean()
        
        # 相关性矩阵
        corr_matrix = np.corrcoef(aligned_returns)
        
        # 分散化效益
        weighted_vol = sum(w * m.annualized_volatility for w, m in zip(weights, individual_metrics))
        diversification_benefit = weighted_vol - portfolio_vol
        
        return {
            'annualized_return': round(portfolio_annual_return, 4),
            'annualized_volatility': round(portfolio_vol, 4),
            'sharpe_ratio': round(portfolio_sharpe, 4),
            'var_95_daily': round(portfolio_var_95, 6),
            'var_99_daily': round(portfolio_var_99, 6),
            'cvar_95_daily': round(portfolio_cvar_95, 6),
            'diversification_benefit': round(diversification_benefit, 4),
            'correlation_matrix': {
                symbols[i]: {symbols[j]: round(corr_matrix[i][j], 4) 
                           for j in range(len(symbols))}
                for i in range(len(symbols))
            }
        }


def print_risk_report(metrics: RiskMetrics, format: str = 'table'):
    """打印风险分析报告"""
    
    if format == 'json':
        print(metrics.to_json())
        return
    
    print(f"\n{'='*60}")
    print(f"📊 风险分析报告: {metrics.symbol}")
    print(f"{'='*60}")
    print(f"分析期间: {metrics.start_date} 至 {metrics.end_date}")
    print(f"交易天数: {metrics.trading_days}")
    
    print(f"\n📈 收益指标")
    print(f"  总收益率:        {metrics.total_return*100:>8.2f}%")
    print(f"  年化收益率:      {metrics.annualized_return*100:>8.2f}%")
    
    print(f"\n⚠️  风险指标")
    print(f"  年化波动率:      {metrics.annualized_volatility*100:>8.2f}%")
    print(f"  下行波动率:      {metrics.downside_volatility*math.sqrt(252)*100:>8.2f}%")
    print(f"  最大回撤:        {metrics.max_drawdown*100:>8.2f}%")
    print(f"  回撤持续天数:    {metrics.max_drawdown_duration:>8} 天")
    print(f"  平均回撤:        {metrics.avg_drawdown*100:>8.2f}%")
    
    print(f"\n📊 调整风险收益比")
    print(f"  夏普比率:        {metrics.sharpe_ratio:>8.3f}")
    print(f"  索提诺比率:      {metrics.sortino_ratio:>8.3f}")
    print(f"  卡玛比率:        {metrics.calmar_ratio:>8.3f}")
    
    print(f"\n💰 VaR 风险价值")
    print(f"  历史 VaR (95%):  {metrics.var_95*100:>8.3f}% (日度)")
    print(f"  历史 VaR (99%):  {metrics.var_99*100:>8.3f}% (日度)")
    print(f"  CVaR (95%):      {metrics.cvar_95*100:>8.3f}% (日度)")
    print(f"  参数 VaR (95%):  {metrics.var_parametric_95*100:>8.3f}% (日度)")
    print(f"  CF VaR (95%):    {metrics.var_cornish_fisher_95*100:>8.3f}% (日度)")
    
    # 解释 VaR
    var_95_pct = abs(metrics.var_95) * 100
    print(f"\n💡 VaR 解读:")
    print(f"  在95%的交易日，损失不会超过 {var_95_pct:.2f}%")
    print(f"  如果投资10万元，正常日亏损不超过 {var_95_pct*1000:.0f}元")
    
    print(f"\n📊 收益分布特征")
    print(f"  偏度:            {metrics.skewness:>8.3f} {'(左偏⚠️)' if metrics.skewness < -0.5 else '(右偏)' if metrics.skewness > 0.5 else '(对称)'}")
    print(f"  峰度:            {metrics.kurtosis:>8.3f} {'(肥尾⚠️)' if metrics.kurtosis > 1 else '(正常)'}")
    print(f"  JB检验p值:       {metrics.jarque_bera_pvalue:>8.6f} {'(正态)' if metrics.is_normal else '(非正态)'}")
    
    # 风险评级
    risk_score = calculate_risk_score(metrics)
    print(f"\n🏷️  综合风险评级: {risk_score}")
    print(f"{'='*60}\n")


def calculate_risk_score(metrics: RiskMetrics) -> str:
    """计算综合风险评级"""
    score = 0
    
    # 波动率评分
    vol = metrics.annualized_volatility
    if vol > 0.5: score += 4
    elif vol > 0.35: score += 3
    elif vol > 0.2: score += 2
    else: score += 1
    
    # 最大回撤评分
    dd = abs(metrics.max_drawdown)
    if dd > 0.4: score += 4
    elif dd > 0.25: score += 3
    elif dd > 0.15: score += 2
    else: score += 1
    
    # VaR 评分
    var = abs(metrics.var_95)
    if var > 0.05: score += 3
    elif var > 0.03: score += 2
    else: score += 1
    
    if score >= 9: return "🔴 高风险"
    elif score >= 6: return "🟡 中高风险"
    elif score >= 4: return "🟢 中等风险"
    else: return "🔵 低风险"


def main():
    parser = argparse.ArgumentParser(description='投资组合风险分析工具')
    parser.add_argument('--symbol', '-s', help='股票代码 (如 MSFT, 700.HK)')
    parser.add_argument('--portfolio-file', '-p', help='投资组合 JSON 文件路径')
    parser.add_argument('--days', '-d', type=int, default=252, help='历史数据天数 (默认252)')
    parser.add_argument('--risk-free-rate', '-r', type=float, default=0.045, help='无风险利率 (默认4.5%%)')
    parser.add_argument('--demo', action='store_true', help='使用演示数据')
    parser.add_argument('--output', '-o', choices=['table', 'json'], default='table', help='输出格式')
    
    args = parser.parse_args()
    
    if not args.symbol and not args.portfolio_file:
        parser.print_help()
        sys.exit(1)
    
    analyzer = RiskAnalyzer(use_demo=args.demo, risk_free_rate=args.risk_free_rate)
    
    try:
        if args.portfolio_file:
            result = analyzer.analyze_portfolio(args.portfolio_file, args.days)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            metrics = analyzer.analyze_symbol(args.symbol, args.days)
            print_risk_report(metrics, args.output)
    
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
