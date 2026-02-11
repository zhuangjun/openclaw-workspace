#!/bin/bash
# 安装 Playwright 自动化环境

echo "🚀 安装 Playwright..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 请先安装 Python 3"
    exit 1
fi

# 安装 playwright
pip3 install playwright

# 安装 Chromium 浏览器
playwright install chromium

echo "✅ 安装完成！"
echo ""
echo "测试运行："
echo "  python3 scripts/gemini_research.py -q '1+1=?' -o ./test.html"
