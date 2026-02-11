#!/usr/bin/env python3
"""
Gemini Deep Research 自动化控制器
使用 Playwright 直接控制 Chrome，无需扩展
"""

import asyncio
import json
import time
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("请先安装 Playwright: pip install playwright")
    print("然后运行: playwright install chromium")
    sys.exit(1)

class GeminiDeepResearch:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        self.context = None
        
    async def start(self):
        """启动浏览器"""
        print("🚀 启动 Chrome...")
        playwright = await async_playwright().start()
        
        # 启动 Chrome（使用已登录的用户数据）
        # 尝试使用系统安装的 Chrome
        import subprocess
        chrome_path = subprocess.run(
            ["ls", "-1", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            capture_output=True, text=True
        ).stdout.strip() or None
        
        launch_options = {
            'headless': self.headless,
            'args': ['--disable-blink-features=AutomationControlled']
        }
        
        if chrome_path:
            launch_options['executable_path'] = chrome_path
            print(f"   使用系统 Chrome: {chrome_path}")
        
        self.browser = await playwright.chromium.launch(**launch_options)
        
        # 创建新页面
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        self.page = await self.context.new_page()
        
        # 访问 Gemini
        print("🌐 访问 Gemini...")
        try:
            await self.page.goto('https://gemini.google.com/app', timeout=60000)
            # 等待页面加载（最多30秒）
            await self.page.wait_for_load_state('networkidle', timeout=30000)
        except Exception as e:
            print(f"⚠️ 页面加载超时，继续尝试... ({e})")
        
        await asyncio.sleep(3)
        
        print("✅ 浏览器启动成功")
        return True
    
    async def run_research(self, query: str, timeout: int = 1200):
        """
        执行 Deep Research
        
        Args:
            query: 研究问题
            timeout: 超时时间（秒）
        """
        print(f"\n🔬 开始 Deep Research")
        print(f"   问题: {query[:50]}...")
        print(f"   超时: {timeout}秒\n")
        
        # 1. 找到输入框并输入
        input_box = await self.page.wait_for_selector('[contenteditable="true"]', timeout=10000)
        await input_box.click()
        await input_box.fill(query)
        await asyncio.sleep(1)
        
        # 2. 启用 Deep Research（点击工具按钮）
        try:
            tools_btn = await self.page.wait_for_selector('button:has-text("工具")', timeout=5000)
            await tools_btn.click()
            await asyncio.sleep(1)
            
            # 点击 Deep Research
            dr_btn = await self.page.wait_for_selector('text=Deep Research', timeout=5000)
            await dr_btn.click()
            await asyncio.sleep(1)
        except:
            print("⚠️ 可能已经是 Deep Research 模式")
        
        # 3. 发送
        send_btn = await self.page.wait_for_selector('button[aria-label="发送"]', timeout=5000)
        await send_btn.click()
        
        # 4. 轮询等待完成
        print("⏳ 等待研究完成...")
        start_time = time.time()
        check_interval = 10
        
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            
            # 检查状态
            try:
                page_content = await self.page.content()
                
                if "已完成" in page_content or "completed" in page_content.lower():
                    print(f"\n✅ 研究完成！耗时 {elapsed}秒")
                    return True
                elif "分析结果中" in page_content:
                    print(f"⏳ [{elapsed}s] 分析结果中...")
                elif "正在研究" in page_content or "Researching" in page_content:
                    print(f"🔍 [{elapsed}s] 研究中...")
                else:
                    print(f"🤔 [{elapsed}s] 处理中...")
                    
            except Exception as e:
                print(f"⚠️ 检查状态出错: {e}")
            
            await asyncio.sleep(check_interval)
        
        print(f"\n⏰ 超时！({timeout}秒)")
        return False
    
    async def save_result(self, output_file: str):
        """保存研究结果"""
        print(f"\n💾 保存结果到: {output_file}")
        
        # 获取页面内容
        content = await self.page.content()
        
        # 保存为 HTML
        Path(output_file).write_text(content, encoding='utf-8')
        
        # 同时保存截图
        screenshot_file = output_file.replace('.html', '.png')
        await self.page.screenshot(path=screenshot_file, full_page=True)
        
        print(f"✅ 已保存: {output_file}")
        print(f"✅ 截图: {screenshot_file}")
        
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("\n👋 浏览器已关闭")

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gemini Deep Research 自动化')
    parser.add_argument('--query', '-q', required=True, help='研究问题')
    parser.add_argument('--output', '-o', default='./research_result.html', help='输出文件')
    parser.add_argument('--timeout', '-t', type=int, default=1200, help='超时时间（秒）')
    parser.add_argument('--headless', action='store_true', help='无头模式（不显示窗口）')
    
    args = parser.parse_args()
    
    # 创建研究器
    researcher = GeminiDeepResearch(headless=args.headless)
    
    try:
        # 启动
        await researcher.start()
        
        # 执行研究
        success = await researcher.run_research(args.query, args.timeout)
        
        # 保存结果
        await researcher.save_result(args.output)
        
        if success:
            print("\n🎉 任务完成！")
            return 0
        else:
            print("\n⚠️ 任务超时")
            return 1
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        await researcher.close()

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
