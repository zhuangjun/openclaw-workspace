#!/usr/bin/env python3
"""
Gemini Deep Research 自动化 - 连接现有 Chrome
"""

import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

class GeminiDeepResearch:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        
    def start(self):
        """启动浏览器 - 连接现有 Chrome 或启动新实例"""
        print("🚀 启动 Chrome...")
        
        p = sync_playwright().start()
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # 检查 Chrome 是否已在运行
        chrome_running = False
        try:
            result = subprocess.run(
                ["pgrep", "-f", "Google Chrome"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                chrome_running = True
                print("✅ 检测到 Chrome 正在运行")
        except:
            pass
        
        if chrome_running:
            # 方法1: 使用 CDP 连接现有 Chrome
            print("🔌 尝试连接现有 Chrome...")
            try:
                # 先尝试默认端口
                self.browser = p.chromium.connect_over_cdp("http://localhost:9222")
                print("✅ 通过 CDP 连接到 Chrome")
                
                # 使用已有页面或创建新页面
                contexts = self.browser.contexts
                if contexts:
                    pages = contexts[0].pages
                    if pages:
                        self.page = pages[0]
                        print("✅ 使用现有页面")
                    else:
                        self.page = contexts[0].new_page()
                else:
                    self.page = self.browser.new_page()
                    
            except Exception as e:
                print(f"⚠️  无法连接现有 Chrome: {e}")
                print("   将启动新的 Chrome 实例")
                chrome_running = False
        
        if not chrome_running:
            # 方法2: 启动新的 Chrome
            print("🆕 启动新的 Chrome 实例...")
            self.browser = p.chromium.launch(
                headless=self.headless,
                executable_path=chrome_path,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.page = self.browser.new_page(viewport={'width': 1400, 'height': 900})
        
        print("🌐 访问 Gemini...")
        self.page.goto('https://gemini.google.com/app', timeout=60000)
        time.sleep(5)
        
        # 检查登录状态
        try:
            page_text = self.page.inner_text('body', timeout=5000)
            if "登录" in page_text or "Sign in" in page_text:
                print("⚠️  未检测到登录状态")
                print("   如果 Chrome 已登录，请尝试点击 OpenClaw 扩展图标")
            else:
                print("✅ 已检测到登录状态")
        except:
            pass
        
        print("✅ 浏览器就绪")
        return True
    
    def run_research(self, query: str, timeout: int = 1200):
        """执行 Deep Research"""
        print(f"\n🔬 开始 Deep Research")
        print(f"   问题: {query[:60]}...")
        print(f"   超时: {timeout}秒\n")
        
        try:
            # 1. 输入问题
            print("⌨️  输入问题...")
            input_box = self.page.locator('[contenteditable="true"]').first
            input_box.click(timeout=10000)
            input_box.fill(query, timeout=10000)
            time.sleep(2)
            
            # 2. 启用 Deep Research
            print("🔧 启用 Deep Research...")
            try:
                # 点击工具按钮
                tool_btn = self.page.locator('button:has-text("工具")').first
                tool_btn.click(timeout=5000)
                time.sleep(2)
                print("   打开工具菜单")
                
                # 点击 Deep Research
                dr_btn = self.page.locator('text=Deep Research').first
                dr_btn.click(timeout=5000)
                time.sleep(2)
                print("✅ Deep Research 已启用")
            except Exception as e:
                print(f"⚠️  启用 Deep Research: {e}")
            
            # 3. 发送
            print("📤 发送请求...")
            try:
                send_btn = self.page.locator('button[aria-label="发送"]').first
                send_btn.click(timeout=5000)
            except:
                self.page.keyboard.press('Enter')
            
            time.sleep(3)
            
            # 4. 轮询等待
            print("\n⏳ 等待 Deep Research 完成...")
            start_time = time.time()
            last_status = ""
            
            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                
                try:
                    page_text = self.page.inner_text('body', timeout=5000)
                    
                    if "已完成" in page_text or "completed" in page_text.lower():
                        print(f"\n✅ [{elapsed}s] 研究完成！")
                        return True
                    elif "分析结果中" in page_text or "分析中" in page_text:
                        if last_status != "分析中":
                            print(f"⏳ [{elapsed}s] 分析结果中...")
                            last_status = "分析中"
                    elif "正在研究" in page_text or "Researching" in page_text:
                        if last_status != "研究中":
                            print(f"🔍 [{elapsed}s] 正在研究...")
                            last_status = "研究中"
                    elif "来源" in page_text:
                        if last_status != "生成中":
                            print(f"📝 [{elapsed}s] 内容生成中...")
                            last_status = "生成中"
                    elif elapsed % 30 == 0:
                        print(f"⏳ [{elapsed}s] 处理中...")
                            
                except:
                    if elapsed % 30 == 0:
                        print(f"⏳ [{elapsed}s] 等待中...")
                
                time.sleep(10)
            
            print(f"\n⏰ 超时！({timeout}秒)")
            return False
            
        except Exception as e:
            print(f"\n❌ 执行出错: {e}")
            return False
    
    def save_result(self, output_file: str):
        """保存结果"""
        print(f"\n💾 保存结果...")
        
        content = self.page.content()
        Path(output_file).write_text(content, encoding='utf-8')
        
        screenshot_file = output_file.replace('.html', '.png')
        self.page.screenshot(path=screenshot_file, full_page=True)
        
        print(f"✅ HTML: {output_file}")
        print(f"✅ 截图: {screenshot_file}")
        
        if "来源" in content:
            print("✅ 检测到 Deep Research 来源")
    
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
    
    researcher = GeminiDeepResearch(headless=args.headless)
    
    try:
        researcher.start()
        success = researcher.run_research(args.query, args.timeout)
        researcher.save_result(args.output)
        
        if success:
            print("\n🎉 完成！")
            return 0
        else:
            print("\n⚠️  超时")
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
