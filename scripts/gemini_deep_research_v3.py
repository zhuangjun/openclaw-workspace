#!/usr/bin/env python3
"""
Gemini Deep Research 自动化 - 强制启用 Deep Research 版本
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

class GeminiDeepResearch:
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.page = None
        
    def start(self):
        """启动浏览器"""
        print("🚀 启动 Chrome...")
        
        p = sync_playwright().start()
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        self.browser = p.chromium.launch(
            headless=self.headless,
            executable_path=chrome_path,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.page = self.browser.new_page(viewport={'width': 1400, 'height': 900})
        
        print("🌐 访问 Gemini...")
        self.page.goto('https://gemini.google.com/app', timeout=60000)
        time.sleep(5)
        print("✅ 浏览器就绪")
        return True
    
    def enable_deep_research(self):
        """显式启用 Deep Research"""
        print("🔧 启用 Deep Research...")
        
        try:
            # 点击输入框旁边的工具按钮
            # 先找到输入框区域
            input_area = self.page.locator('.input-area, .chat-input, [contenteditable="true"]').first
            
            # 查找工具按钮（通常在输入框附近）
            # 尝试多种选择器
            tool_selectors = [
                'button:has-text("工具")',
                'button[aria-label*="工具"]', 
                'button:has(.tool-icon)',
                '[data-test-id="tool-button"]',
                'button:has-text("Deep Research")',
                '[aria-label="Deep Research"]'
            ]
            
            for selector in tool_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        print(f"   找到工具按钮: {selector}")
                        btn.click()
                        time.sleep(2)
                        
                        # 查找 Deep Research 选项
                        dr_selectors = [
                            'text=Deep Research',
                            '[data-test-id="deep-research"]',
                            'menuitem:has-text("Deep Research")'
                        ]
                        
                        for dr_sel in dr_selectors:
                            try:
                                dr_btn = self.page.locator(dr_sel).first
                                if dr_btn.is_visible(timeout=2000):
                                    print(f"   启用 Deep Research: {dr_sel}")
                                    dr_btn.click()
                                    time.sleep(2)
                                    print("✅ Deep Research 已启用")
                                    return True
                            except:
                                continue
                        
                        # 如果没找到 Deep Research 选项，可能已经启用，点击其他地方关闭菜单
                        self.page.keyboard.press('Escape')
                        time.sleep(1)
                        
                except:
                    continue
            
            print("⚠️  未找到 Deep Research 按钮，可能已自动启用或不可用")
            return False
            
        except Exception as e:
            print(f"⚠️  启用 Deep Research 出错: {e}")
            return False
    
    def run_research(self, query: str, timeout: int = 300):
        """执行 Deep Research"""
        print(f"\n🔬 开始 Deep Research")
        print(f"   问题: {query[:60]}...")
        print(f"   超时: {timeout}秒\n")
        
        try:
            # 1. 找到输入框并输入
            print("⌨️  输入问题...")
            input_box = self.page.locator('[contenteditable="true"]').first
            input_box.click(timeout=10000)
            input_box.fill(query, timeout=10000)
            time.sleep(2)
            
            # 2. 启用 Deep Research
            self.enable_deep_research()
            
            # 3. 发送
            print("📤 发送请求...")
            # 尝试多种发送方式
            try:
                send_btn = self.page.locator('button[aria-label="发送"]').first
                send_btn.click(timeout=5000)
            except:
                # 回车发送
                self.page.keyboard.press('Enter')
            
            time.sleep(3)
            
            # 4. 轮询等待 - 检测 Deep Research 特有的状态
            print("\n⏳ 等待 Deep Research 完成...")
            start_time = time.time()
            check_interval = 10
            last_status = ""
            
            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                
                try:
                    # 获取页面文本
                    page_text = self.page.inner_text('body', timeout=5000)
                    
                    # Deep Research 特有的状态检测
                    if "研究完成" in page_text or "分析完成" in page_text or "completed" in page_text.lower():
                        if last_status != "完成":
                            print(f"\n✅ [{elapsed}s] Deep Research 完成！")
                            last_status = "完成"
                            return True
                    elif "正在研究" in page_text or "Researching" in page_text or "研究中" in page_text:
                        if last_status != "研究中":
                            print(f"🔍 [{elapsed}s] Deep Research 进行中...")
                            last_status = "研究中"
                    elif "分析结果" in page_text or "Analyzing" in page_text:
                        if last_status != "分析中":
                            print(f"⏳ [{elapsed}s] 分析结果中...")
                            last_status = "分析中"
                    elif "来源" in page_text and ("网站" in page_text or "网页" in page_text):
                        # 检测到 Deep Research 特有的"来源"引用
                        if last_status != "研究中":
                            print(f"🔍 [{elapsed}s] Deep Research 进行中 (检测到来源引用)...")
                            last_status = "研究中"
                    else:
                        # 检查是否有生成的内容
                        if len(page_text) > 500 and "Gemini" in page_text and elapsed > 20:
                            if last_status != "生成中":
                                print(f"📝 [{elapsed}s] 内容生成中...")
                                last_status = "生成中"
                        elif elapsed % 30 == 0:
                            print(f"⏳ [{elapsed}s] 等待中...")
                    
                except Exception as e:
                    if elapsed % 30 == 0:
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
        
        # 保存文本提取
        try:
            text_content = self.page.inner_text('body')
            text_file = output_file.replace('.html', '.txt')
            Path(text_file).write_text(text_content, encoding='utf-8')
            print(f"✅ 文本: {text_file}")
        except:
            pass
        
        print(f"✅ HTML: {output_file}")
        print(f"✅ 截图: {screenshot_file}")
        
        # 检查是否有 Deep Research 特征
        if "来源" in content and ("网站" in content or "参考" in content):
            print("✅ 检测到 Deep Research 引用来源")
    
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
    parser.add_argument('--timeout', '-t', type=int, default=300, help='超时时间（秒）')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    
    args = parser.parse_args()
    
    researcher = GeminiDeepResearch(headless=args.headless)
    
    try:
        researcher.start()
        success = researcher.run_research(args.query, args.timeout)
        researcher.save_result(args.output)
        
        if success:
            print("\n🎉 Deep Research 成功完成！")
            return 0
        else:
            print("\n⚠️  Deep Research 超时，但可能已有部分结果")
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
