#!/usr/bin/env python3
"""
Gemini Deep Research 自动化 - 可靠版本
使用 Playwright 直接控制 Chrome，无需扩展
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

class GeminiResearcher:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        
    def start(self):
        """启动浏览器"""
        print("🚀 启动 Chrome...")
        
        p = sync_playwright().start()
        
        # 使用系统 Chrome
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        self.browser = p.chromium.launch(
            headless=self.headless,
            executable_path=chrome_path,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.page = self.browser.new_page(viewport={'width': 1280, 'height': 800})
        
        print("🌐 访问 Gemini...")
        self.page.goto('https://gemini.google.com/app', timeout=60000)
        
        # 等待页面基本加载
        time.sleep(5)
        
        print("✅ 浏览器就绪")
        return True
    
    def run_research(self, query: str, timeout: int = 1200):
        """执行 Deep Research"""
        print(f"\n🔬 开始研究: {query[:50]}...")
        print(f"   超时: {timeout}秒\n")
        
        try:
            # 1. 找到输入框
            print("⌨️  输入问题...")
            input_box = self.page.locator('[contenteditable="true"]').first
            input_box.click(timeout=10000)
            input_box.fill(query, timeout=10000)
            time.sleep(2)
            
            # 2. 启用 Deep Research
            print("🔧 启用 Deep Research...")
            try:
                tools_btn = self.page.locator('button:has-text("工具")').first
                tools_btn.click(timeout=5000)
                time.sleep(1)
                
                dr_btn = self.page.locator('text=Deep Research').first
                dr_btn.click(timeout=5000)
                time.sleep(1)
                print("✅ Deep Research 已启用")
            except Exception as e:
                print(f"⚠️  启用 Deep Research 可能已自动启用或出错: {e}")
            
            # 3. 发送
            print("📤 发送请求...")
            send_btn = self.page.locator('button[aria-label="发送"]').first
            send_btn.click(timeout=10000)
            
            # 4. 轮询等待
            print("\n⏳ 等待研究完成...")
            start_time = time.time()
            check_interval = 10
            
            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                
                # 获取页面文本检查状态
                try:
                    page_text = self.page.inner_text('body', timeout=5000)
                    
                    if "已完成" in page_text:
                        print(f"\n✅ 研究完成！耗时 {elapsed}秒")
                        return True
                    elif "分析结果中" in page_text:
                        print(f"⏳ [{elapsed}s] 分析结果中...")
                    elif "正在研究" in page_text or "Researching" in page_text:
                        print(f"🔍 [{elapsed}s] 研究中...")
                    else:
                        print(f"🤔 [{elapsed}s] 处理中...")
                        
                except:
                    print(f"⏳ [{elapsed}s] 等待响应...")
                
                time.sleep(check_interval)
            
            print(f"\n⏰ 超时！({timeout}秒)")
            return False
            
        except Exception as e:
            print(f"\n❌ 执行出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_result(self, output_file: str):
        """保存结果"""
        print(f"\n💾 保存结果...")
        
        # 保存 HTML
        content = self.page.content()
        Path(output_file).write_text(content, encoding='utf-8')
        
        # 保存截图
        screenshot_file = output_file.replace('.html', '.png')
        self.page.screenshot(path=screenshot_file, full_page=True)
        
        print(f"✅ HTML: {output_file}")
        print(f"✅ 截图: {screenshot_file}")
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            print("\n👋 浏览器已关闭")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gemini Deep Research 自动化')
    parser.add_argument('--query', '-q', required=True, help='研究问题')
    parser.add_argument('--output', '-o', default='./research_result.html', help='输出文件')
    parser.add_argument('--timeout', '-t', type=int, default=1200, help='超时时间（秒）')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    
    args = parser.parse_args()
    
    researcher = GeminiResearcher(headless=args.headless)
    
    try:
        researcher.start()
        success = researcher.run_research(args.query, args.timeout)
        researcher.save_result(args.output)
        
        if success:
            print("\n🎉 任务成功完成！")
            return 0
        else:
            print("\n⚠️  任务超时")
            return 1
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        researcher.close()

if __name__ == '__main__':
    sys.exit(main())
