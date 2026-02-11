#!/bin/bash
# Playwright 简化测试 - 仅验证基本功能

echo "🧪 Playwright 功能测试"
echo "======================"
echo ""

# 1. 检查 Python
echo "✓ Python: $(python3 --version)"

# 2. 检查 Playwright
echo "✓ Playwright: $(pip3 show playwright | grep Version)"

# 3. 检查浏览器
echo ""
echo "🔍 检查 Chrome..."
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    echo "✓ Chrome 已安装"
else
    echo "❌ Chrome 未找到"
fi

# 4. 创建简单测试脚本
echo ""
echo "📝 创建测试脚本..."
cat > /tmp/test_playwright.py << 'PYEOF'
from playwright.sync_api import sync_playwright
import sys

print("🚀 启动浏览器...")

try:
    with sync_playwright() as p:
        # 使用系统 Chrome
        browser = p.chromium.launch(
            headless=True,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        
        print("✅ 浏览器启动成功")
        
        page = browser.new_page()
        print("📄 新页面创建成功")
        
        # 访问简单页面
        page.goto("https://www.google.com", timeout=30000)
        print("✅ 页面加载成功")
        
        title = page.title()
        print(f"📋 页面标题: {title}")
        
        browser.close()
        print("👋 浏览器已关闭")
        
        print("\n🎉 Playwright 测试通过！")
        sys.exit(0)
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

# 5. 运行测试
echo ""
echo "▶️ 运行测试..."
python3 /tmp/test_playwright.py 2>&1

EXIT_CODE=$?

echo ""
echo "======================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 测试通过！Playwright 可以正常工作"
    echo ""
    echo "明天可以使用此方案自动执行 Deep Research"
else
    echo "❌ 测试失败"
    echo ""
    echo "建议：使用现有的 browser 工具方案"
fi
