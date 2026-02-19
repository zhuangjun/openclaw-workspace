#!/usr/bin/env python3
"""
yfinance 财报数据获取测试脚本
测试获取利润表、资产负债表、现金流量表
"""
import yfinance as yf
import json
import sys

def test_financials(ticker="AAPL"):
    """测试获取指定股票的财务数据"""
    print(f"\n{'='*60}")
    print(f"📊 测试获取 {ticker} 财务数据")
    print(f"{'='*60}\n")
    
    try:
        # 创建 Ticker 对象
        stock = yf.Ticker(ticker)
        
        # 1. 获取基本信息
        print(f"【1. 基本信息】")
        info = stock.info
        print(f"  公司名称: {info.get('longName', 'N/A')}")
        print(f"  行业: {info.get('industry', 'N/A')}")
        print(f"  市值: ${info.get('marketCap', 0)/1e9:.2f}B")
        print(f"  市盈率(TTM): {info.get('trailingPE', 'N/A')}")
        print(f"   forward PE: {info.get('forwardPE', 'N/A')}")
        print(f"  市净率: {info.get('priceToBook', 'N/A')}")
        print(f"  股息率: {info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "  股息率: N/A")
        
        # 2. 获取年度利润表
        print(f"\n【2. 年度利润表 (最近4年)】")
        income_stmt = stock.income_stmt
        if income_stmt is not None and not income_stmt.empty:
            # 显示主要指标
            key_items = ['Total Revenue', 'Operating Income', 'Net Income', 'EBITDA']
            for item in key_items:
                if item in income_stmt.index:
                    values = income_stmt.loc[item]
                    print(f"  {item}:")
                    for col in values.index[:4]:
                        print(f"    {col.strftime('%Y')}: ${values[col]/1e9:.2f}B" if abs(values[col]) > 1e9 else f"    {col.strftime('%Y')}: ${values[col]/1e6:.2f}M")
        else:
            print("  暂无数据")
        
        # 3. 获取季度利润表
        print(f"\n【3. 季度利润表 (最近4季度)】")
        quarterly_income = stock.quarterly_income_stmt
        if quarterly_income is not None and not quarterly_income.empty:
            if 'Total Revenue' in quarterly_income.index:
                values = quarterly_income.loc['Total Revenue']
                print(f"  Total Revenue:")
                for col in values.index[:4]:
                    print(f"    Q{col.quarter} {col.year}: ${values[col]/1e9:.2f}B" if abs(values[col]) > 1e9 else f"    Q{col.quarter} {col.year}: ${values[col]/1e6:.2f}M")
        else:
            print("  暂无数据")
        
        # 4. 获取资产负债表
        print(f"\n【4. 年度资产负债表 (关键指标)】")
        balance_sheet = stock.balance_sheet
        if balance_sheet is not None and not balance_sheet.empty:
            key_items = ['Total Assets', 'Total Liabilities Net Minority Interest', 'Stockholders Equity']
            for item in key_items:
                if item in balance_sheet.index:
                    values = balance_sheet.loc[item]
                    latest_val = values.iloc[0]
                    print(f"  {item}: ${latest_val/1e9:.2f}B" if abs(latest_val) > 1e9 else f"  {item}: ${latest_val/1e6:.2f}M")
        else:
            print("  暂无数据")
        
        # 5. 获取现金流量表
        print(f"\n【5. 年度现金流量表 (关键指标)】")
        cashflow = stock.cashflow
        if cashflow is not None and not cashflow.empty:
            key_items = ['Operating Cash Flow', 'Capital Expenditure', 'Free Cash Flow']
            for item in key_items:
                if item in cashflow.index:
                    values = cashflow.loc[item]
                    latest_val = values.iloc[0]
                    print(f"  {item}: ${latest_val/1e9:.2f}B" if abs(latest_val) > 1e9 else f"  {item}: ${latest_val/1e6:.2f}M")
        else:
            print("  暂无数据")
        
        # 6. 获取分析师推荐
        print(f"\n【6. 分析师推荐】")
        recommendations = stock.recommendations
        if recommendations is not None and not recommendations.empty:
            recent = recommendations.tail(5)
            for idx, row in recent.iterrows():
                print(f"  {idx.strftime('%Y-%m-%d')}: {row.get('To Grade', 'N/A')} (from: {row.get('From Grade', 'N/A')})")
        else:
            print("  暂无数据")
        
        # 7. 获取收益预期
        print(f"\n【7. 收益日历】")
        earnings_dates = stock.earnings_dates
        if earnings_dates is not None and not earnings_dates.empty:
            future_earnings = earnings_dates[earnings_dates.index > pd.Timestamp.now()]
            if not future_earnings.empty:
                for idx, row in future_earnings.head(2).iterrows():
                    print(f"  {idx.strftime('%Y-%m-%d')}: EPS预期 ${row.get('EPS Estimate', 'N/A')}")
        else:
            print("  暂无数据")
            
        print(f"\n{'='*60}")
        print(f"✅ {ticker} 数据获取成功")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}\n")
        return False

if __name__ == "__main__":
    import pandas as pd
    
    # 测试美股
    test_financials("AAPL")
    
    # 测试另一支美股
    test_financials("MSFT")
    
    # 测试港股 (Yahoo格式)
    test_financials("3690.HK")
