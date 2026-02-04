def interpret_ahr999_value(ahr999_value):
    """
    解释AHR999指数值的含义
    """
    print("="*60)
    print("AHR999指数深度解析")
    print("="*60)
    print(f"当前AHR999指数: {ahr999_value:.3f}")
    print()
    
    if ahr999_value < 0.4:
        category = "强烈低估"
        signal = "强力买入"
        description = "比特币价格远低于其历史公允价值，是极佳的买入时机"
        action = "强烈建议买入，可能是历史级买入机会"
    elif ahr999_value < 0.8:
        category = "低估"
        signal = "买入"
        description = "比特币价格低于其历史公允价值，是良好的买入时机"
        action = "建议买入，估值偏低"
    elif ahr999_value < 1.2:
        category = "接近合理估值"
        signal = "持有/轻度买入"
        description = "比特币价格接近其历史公允价值"
        action = "可考虑持有或轻度买入"
    elif ahr999_value < 1.5:
        category = "偏高估值"
        signal = "谨慎持有"
        description = "比特币价格略高于其历史公允价值"
        action = "建议谨慎持有，等待回调"
    else:
        category = "高估"
        signal = "卖出"
        description = "比特币价格远高于其历史公允价值"
        action = "建议卖出或减仓，等待更好时机"
    
    print(f"状态: {category}")
    print(f"交易信号: {signal}")
    print(f"描述: {description}")
    print(f"操作建议: {action}")
    print()
    
    print("AHR999指数详解:")
    print("- AHR999 = (BTC价格 / MA200) * (BTC价格 / (0.382*MA200 + 0.618*MA200历史高点))")
    print("- 该指标衡量比特币在熊市中的恢复程度")
    print("- 由投资者@ahr999发明，广泛用于比特币估值判断")
    print()
    
    print("各区间详解:")
    print("• <0.4: 极度低估区域，通常出现在熊市末期，是历史级买入机会")
    print("• 0.4-0.8: 低估区域，适合分批买入")
    print("• 0.8-1.2: 合理估值区域，市场相对平衡")
    print("• 1.2-1.5: 偏高估值区域，需谨慎操作")
    print("• >1.5: 明显高估区域，建议获利了结")
    print()

def calculate_required_values_for_target_ahr999(current_price, target_ahr999):
    """
    计算达到目标AHR999值所需的历史价格参数
    """
    print(f"基于当前价格 ${current_price:,.2f} 计算:")
    print(f"要达到AHR999 = {target_ahr999:.3f}，需要200日均线约为: ${current_price/target_ahr999:,.2f}")
    print()

def current_market_analysis():
    """
    当前市场分析（基于AHR999=0.42）
    """
    current_price = 78000  # 当前比特币价格约78,000美元
    ahr999_value = 0.42  # 您提到的当前AHR999值
    
    print("当前市场分析")
    print("="*60)
    print(f"当前比特币价格: ${current_price:,.2f}")
    print(f"当前AHR999指数: {ahr999_value:.3f}")
    print()
    
    interpret_ahr999_value(ahr999_value)
    
    print("当前市场环境分析:")
    print("✓ 估值层面: 比特币处于强烈低估状态")
    print("✓ 恐惧贪婪指数: 14 (极度恐惧)，进一步确认底部特征")
    print("✓ 双重信号: 估值+情绪双重确认买入时机")
    print()
    
    print("交易策略建议:")
    print("1. 方向: 买入")
    print("2. 强度: 强力 (双信号确认)")
    print("3. 仓位: 可考虑分批建仓，避免一次性满仓")
    print("4. 风险管理: 设置适当止损，控制风险敞口")
    print()
    
    print("历史参考:")
    print("- AHR999 < 0.4的历史时期: 2018年底熊市、2020年3月疫情、2022年熊市")
    print("- 这些时期后续都出现了显著的牛市行情")
    print("- 当前情况与上述历史时期相似，具备长期投资价值")
    print()
    
    print("风险提示:")
    print("• 尽管技术指标显示强力买入信号，加密市场波动极大")
    print("• 建议仅投入可承受损失的资金")
    print("• 注意市场可能继续下跌的风险")
    print("• 实施适当的资金管理和风险控制策略")

def additional_market_context():
    """
    额外的市场背景信息
    """
    print("市场背景补充:")
    print("="*60)
    print("AHR999指数发明者观点:")
    print("- 该指标特别关注比特币在熊市中的表现")
    print("- 当AHR999 < 0.4时，通常表示比特币已从ATH回撤足够幅度")
    print("- 并且回到了历史成本区，具备长期投资价值")
    print()
    
    print("使用注意事项:")
    print("• AHR999是估值指标，非短期预测工具")
    print("• 应结合其他技术指标和基本面分析")
    print("• 市场可能在底部区域震荡较长时间")
    print("• 长期持有需有足够耐心和风险承受能力")

if __name__ == "__main__":
    current_market_analysis()
    print()
    additional_market_context()