#!/usr/bin/env python3
"""
市场情绪指标获取工具
支持: VIX, CNN Fear & Greed Index, 加密货币恐惧贪婪指数
"""

import requests
import yfinance as yf
import json
from datetime import datetime
from typing import Dict, Optional, Union

class MarketSentiment:
    """市场情绪指标获取类"""
    
    # CNN Fear & Greed API
    CNN_FG_API = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    
    # Alternative.me Crypto Fear & Greed API
    CRYPTO_FG_API = "https://api.alternative.me/fng/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_vix(self) -> Dict:
        """
        获取 VIX 波动率指数数据
        
        Returns:
            Dict: 包含当前值、前收盘、历史数据
        """
        try:
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="5d")
            info = vix.info
            
            if hist.empty:
                return {"error": "无法获取 VIX 数据"}
            
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
            
            # 解读 VIX 水平
            if current < 20:
                interpretation = "平静 (Complacent)"
            elif current < 25:
                interpretation = "正常 (Normal)"
            elif current < 30:
                interpretation = "担忧 (Worried)"
            else:
                interpretation = "恐慌 (Fear)"
            
            return {
                "symbol": "^VIX",
                "name": "CBOE波动率指数",
                "current": round(current, 2),
                "previous_close": round(prev_close, 2),
                "change": round(current - prev_close, 2),
                "change_percent": round((current - prev_close) / prev_close * 100, 2),
                "interpretation": interpretation,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"获取 VIX 数据失败: {str(e)}"}
    
    def get_fear_greed_index(self) -> Dict:
        """
        获取 CNN Fear & Greed Index
        
        Returns:
            Dict: 恐惧贪婪指数数据
        """
        try:
            response = self.session.get(self.CNN_FG_API, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            fear_greed = data.get('fear_and_greed', {})
            
            score = fear_greed.get('score', 0)
            rating = fear_greed.get('rating', 'Unknown')
            
            # 获取历史数据
            historical = data.get('fear_and_greed_historical', {}).get('data', [])
            
            prev_close = score
            week_ago = score
            month_ago = score
            year_ago = score
            
            if historical:
                # 找最接近的数据点
                now_ts = datetime.now().timestamp() * 1000
                
                for item in historical:
                    item_ts = item.get('x', 0)
                    item_score = item.get('y', score)
                    
                    # 前收盘 (1天前)
                    if now_ts - item_ts < 86400000 * 2 and now_ts - item_ts > 86400000 * 0.5:
                        prev_close = item_score
                    # 1周前
                    elif now_ts - item_ts < 86400000 * 8 and now_ts - item_ts > 86400000 * 6:
                        week_ago = item_score
                    # 1月前
                    elif now_ts - item_ts < 86400000 * 32 and now_ts - item_ts > 86400000 * 28:
                        month_ago = item_score
                    # 1年前
                    elif now_ts - item_ts < 86400000 * 370 and now_ts - item_ts > 86400000 * 350:
                        year_ago = item_score
            
            # 获取各指标详情
            components = {}
            for key in ['market_momentum_sp500', 'market_momentum_sp125', 
                       'stock_price_strength', 'stock_price_breadth',
                       'put_call_options', 'market_volatility_vix',
                       'junk_bond_demand', 'safe_haven_demand']:
                if key in data:
                    comp = data[key]
                    components[key] = {
                        'score': comp.get('score'),
                        'rating': comp.get('rating'),
                        'text': comp.get('text', '')
                    }
            
            return {
                "index": "CNN Fear & Greed",
                "current_score": score,
                "rating": rating,
                "previous_close": prev_close,
                "week_ago": week_ago,
                "month_ago": month_ago,
                "year_ago": year_ago,
                "components": components,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"获取 Fear & Greed Index 失败: {str(e)}"}
    
    def get_crypto_fear_greed(self, limit: int = 1) -> Dict:
        """
        获取加密货币恐惧贪婪指数
        
        Args:
            limit: 返回历史数据条数 (默认1条最新)
            
        Returns:
            Dict: 加密货币恐惧贪婪指数数据
        """
        try:
            params = {'limit': limit}
            response = self.session.get(self.CRYPTO_FG_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'data' not in data or not data['data']:
                return {"error": "无法获取加密货币恐惧贪婪指数"}
            
            items = []
            for item in data['data']:
                value = int(item.get('value', 0))
                classification = item.get('value_classification', 'Unknown')
                timestamp = int(item.get('timestamp', 0))
                
                items.append({
                    'value': value,
                    'classification': classification,
                    'date': datetime.fromtimestamp(timestamp).isoformat()
                })
            
            return {
                "index": "Crypto Fear & Greed",
                "data": items,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"获取加密货币恐惧贪婪指数失败: {str(e)}"}
    
    def get_all_sentiment(self) -> Dict:
        """
        获取所有市场情绪指标
        
        Returns:
            Dict: 综合市场情绪数据
        """
        return {
            "vix": self.get_vix(),
            "fear_greed": self.get_fear_greed_index(),
            "crypto_fear_greed": self.get_crypto_fear_greed(),
            "generated_at": datetime.now().isoformat()
        }


def format_sentiment_report(data: Dict) -> str:
    """格式化市场情绪报告"""
    lines = ["📊 市场情绪指标报告", "=" * 40, ""]
    
    # VIX
    vix = data.get('vix', {})
    if 'error' not in vix:
        lines.append(f"📈 VIX 波动率指数")
        lines.append(f"   当前值: {vix.get('current')} ({vix.get('interpretation')})")
        lines.append(f"   前收盘: {vix.get('previous_close')}")
        change = vix.get('change', 0)
        change_pct = vix.get('change_percent', 0)
        sign = "+" if change >= 0 else ""
        lines.append(f"   变动: {sign}{change} ({sign}{change_pct}%)")
        lines.append("")
    
    # Fear & Greed
    fg = data.get('fear_greed', {})
    if 'error' not in fg:
        lines.append(f"😨😰 CNN Fear & Greed Index")
        lines.append(f"   当前: {fg.get('current_score')} - {fg.get('rating')}")
        lines.append(f"   前收盘: {fg.get('previous_close')}")
        lines.append(f"   1周前: {fg.get('week_ago')}")
        lines.append(f"   1月前: {fg.get('month_ago')}")
        lines.append(f"   1年前: {fg.get('year_ago')}")
        lines.append("")
        
        # 各指标详情
        components = fg.get('components', {})
        if components:
            lines.append("   分项指标:")
            name_map = {
                'market_momentum_sp500': '市场动量(S&P500)',
                'market_momentum_sp125': '市场动量(S&P125)',
                'stock_price_strength': '股价强度',
                'stock_price_breadth': '股价宽度',
                'put_call_options': '期权买卖比',
                'market_volatility_vix': '市场波动率',
                'junk_bond_demand': '垃圾债需求',
                'safe_haven_demand': '避险需求'
            }
            for key, comp in components.items():
                name = name_map.get(key, key)
                lines.append(f"      {name}: {comp.get('rating')}")
        lines.append("")
    
    # Crypto Fear & Greed
    crypto = data.get('crypto_fear_greed', {})
    if 'error' not in crypto:
        lines.append(f"₿ 加密货币恐惧贪婪指数")
        data_items = crypto.get('data', [])
        if data_items:
            item = data_items[0]
            lines.append(f"   当前: {item.get('value')} - {item.get('classification')}")
        lines.append("")
    
    # 解读
    lines.append("📋 解读指南:")
    lines.append("   VIX: <20平静, 20-30担忧, >30恐慌")
    lines.append("   Fear & Greed: 0-24极度恐惧, 25-44恐惧, 45-55中性,")
    lines.append("                 56-75贪婪, 76-100极度贪婪")
    lines.append("")
    
    return "\n".join(lines)


def main():
    """主函数 - CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='市场情绪指标获取工具')
    parser.add_argument('--vix', action='store_true', help='仅获取 VIX 数据')
    parser.add_argument('--fear-greed', action='store_true', help='仅获取 Fear & Greed Index')
    parser.add_argument('--crypto', action='store_true', help='仅获取加密货币恐惧贪婪指数')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    sentiment = MarketSentiment()
    
    # 如果没有指定具体指标，获取全部
    if not (args.vix or args.fear_greed or args.crypto):
        data = sentiment.get_all_sentiment()
    else:
        data = {}
        if args.vix:
            data['vix'] = sentiment.get_vix()
        if args.fear_greed:
            data['fear_greed'] = sentiment.get_fear_greed_index()
        if args.crypto:
            data['crypto_fear_greed'] = sentiment.get_crypto_fear_greed()
        data['generated_at'] = datetime.now().isoformat()
    
    # 输出
    if args.json:
        output = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        output = format_sentiment_report(data)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"数据已保存到: {args.output}")
    else:
        print(output)
    
    return data


if __name__ == "__main__":
    main()
