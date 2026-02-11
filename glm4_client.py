#!/usr/bin/env python3
"""
OpenCode/GLM-4.7 API 客户端
直接调用智谱AI API
"""

import requests
import json
from datetime import datetime

API_KEY = "255407f65ec7478fa70f96a3935ce0c8.V8dUFkBjDDATnFGE"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def call_glm4(system_prompt, user_prompt, temperature=0.7):
    """调用GLM-4.7模型"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "glm-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"API错误: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"API调用异常: {e}")
        return None


# ===== 每日投资晨报 =====
DAILY_REPORT_PROMPT = """你是一个专业的投资分析师。请基于当前市场情况，生成一份每日投资晨报。

请包含以下内容：
1. 美股大盘分析（标普500、纳指、道指走势）
2. MAG7科技巨头动态
3. 港股市场概况
4. 重点关注的行业和主题
5. 具体的投资机会（给出具体股票代码和理由）
6. 风险提醒

请用中文回答，格式清晰，给出具体股票代码。"""

def run_daily_market_report():
    """生成每日投资晨报"""
    print(f"[{datetime.now()}] 开始生成每日投资晨报...")
    
    result = call_glm4(
        DAILY_REPORT_PROMPT,
        "请生成今日投资晨报，包括市场分析和3-5个具体股票推荐及理由"
    )
    
    return result


# ===== 戴维斯双击扫描 =====
DAVIS_DOUBLE_PROMPT = """你是价值投资专家，专注于寻找"戴维斯双击"机会。

戴维斯双击定义：
1. 低估值（PE、PB低于历史平均）
2. 盈利增长（未来有明确增长 catalyst）
3. 市值大于50亿美元
4. 暂时被低估但基本面改善

请分析当前市场，找出1-2只符合戴维斯双击条件的美国大型股票。
对于每只股票，请提供：
- 股票代码和名称
- 当前估值指标
- 盈利增长 catalyst
- 为什么被低估
- 预期收益率

用中文回答。"""

def run_davis_double_scan():
    """戴维斯双击股票扫描"""
    print(f"[{datetime.now()}] 开始戴维斯双击扫描...")
    
    result = call_glm4(
        DAVIS_DOUBLE_PROMPT,
        "请找出当前符合戴维斯双击条件的1-2只美股，详细分析其估值和增长逻辑"
    )
    
    return result


# ===== 比特币追踪 =====
BITCOIN_PROMPT = """你是加密货币分析师，专注于比特币（BTC）技术分析。

请分析：
1. BTC当前价格走势
2. 关键支撑位和阻力位
3. 技术指标信号
4. 资金流向和市场情绪
5. 短期交易建议

用中文回答，给出具体价格点位。"""

def run_bitcoin_tracker():
    """比特币追踪分析"""
    print(f"[{datetime.now()}] 开始比特币追踪分析...")
    
    result = call_glm4(
        BITCOIN_PROMPT,
        "请分析比特币当前走势，给出关键价位、技术信号和交易建议"
    )
    
    return result


if __name__ == "__main__":
    # 测试
    print("="*50)
    print("GLM-4.7 API客户端测试")
    print("="*50)
    
    # 测试每日晨报
    print("\n[测试] 每日投资晨报:")
    report = run_daily_market_report()
    if report:
        print(report[:300] + "...")
    
    # 测试戴维斯双击
    print("\n[测试] 戴维斯双击扫描:")
    scan = run_davis_double_scan()
    if scan:
        print(scan[:300] + "...")
    
    # 测试比特币
    print("\n[测试] 比特币追踪:")
    btc = run_bitcoin_tracker()
    if btc:
        print(btc[:300] + "...")
