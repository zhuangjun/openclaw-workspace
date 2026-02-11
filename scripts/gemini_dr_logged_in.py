#!/usr/bin/env python3
"""
Gemini Deep Research 自动化 - 使用已登录的 Chrome
通过连接现有的 Chrome 实例或复用用户数据
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
        """启动浏览器 - 尝试使用已登录的 Chrome"""
        print("🚀 启动 Chrome...")
        
        p = sync_playwright().start()
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # 方法1: 尝试连接已运行的 Chrome（需要远程调试端口）
        # 先检查是否有 Chrome 在运行
        try:
            result = subprocess.run(
                ["pgrep", "-f", "Google Chrome"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ 检测到 Chrome 正在运行")
                print("⚠️  请确保已点击 OpenClaw 扩展图标连接浏览器")
        except:
            pass
        
        # 方法2: 使用用户数据目录（保留登录状态）
        user_data_dir = Path.home() / "Library/Application Support/Google/Chrome"
        
        if user_data_dir.exists():
            print(f"   使用用户数据: {user_data_dir}")
            # 使用持久上下文（保留登录状态）
            self.browser = p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=self.headless,
                executable_path=chrome_path,
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1400, 'height': 900}
            )
            self.page = self.browser.new_page()
        else:
            print("⚠️  未找到用户数据，使用普通模式")
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
                print("⚠️  未检测到登录状态，可能需要手动登录")
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
            
            # 2. 查找并点击 Deep Research 按钮
            print("🔧 启用 Deep Research...")
            
            # 先点击工具按钮
            try:
                # 尝试多种选择器
                tool_btn = None
                for selector in [
                    'button:has-text("工具")',
                    'button[aria-label*="工具"]', 
                    '[data-testid="tool-button"]'
                ]:
                    try:
                        btn = self.page.locator(selector).first
                        if btn.is_visible(timeout=3000):
                            tool_btn = btn
                            break
                    except:
                        continue
                
                if tool_btn:
                    tool_btn.click()
                    time.sleep(2)
                    print("   打开工具菜单")
                    
                    # 点击 Deep Research
                    try:
                        dr_btn = self.page.locator('text=Deep Research').first
                        dr_btn.click(timeout=5000)
                        time.sleep(2)
                        print("✅ Deep Research 已启用")
                    except:
                        print("⚠️  未找到 Deep Research 选项")
                else:
                    print("⚠️  未找到工具按钮，可能已自动启用")
                    
            except Exception as e:
                print(f"⚠️  启用 Deep Research 过程: {e}")
            
            # 3. 发送
            print("📤 发送请求...")
            try:
                send_btn = self.page.locator('button[aria-label="发送"]').first
                send_btn.click(timeout=5000)
            except:
                self.page.keyboard.press('Enter')
            
            time.sleep(3)
            
            # 4. 等待研究计划
            print("\n⏳ 等待 Deep Research 计划...")
            start_time = time.time()
            
            # 等待研究计划出现（通常几秒后）
            plan_appeared = False
            for _ in range(10):  # 等待最多50秒
                try:
                    page_text = self.page.inner_text('body', timeout=3000)
                    if "研究网站" in page_text or "Researching" in page_text or "开始研究" in page_text:
                        print("✅ 检测到 Deep Research 计划")
                        plan_appeared = True
                        break
                except:
                    pass
                time.sleep(5)
            
            if not plan_appeared:
                print("⚠️  未检测到 Deep Research 计划，可能：")
                print("   1. 问题太简单，不需要 Deep Research")
                print("   2. Deep Research 未正确启用")
                print("   3. Gemini 正在直接回答")
            
            # 5. 轮询等待完成
            print("\n⏳ 等待研究完成...")
            last_status = ""
            check_count = 0
            
            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                check_count += 1
                
                # 每30秒输出一次状态
                if check_count % 3 == 0:
                    try:
                        page_text = self.page.inner_text('body', timeout=5000)
                        
                        # 检测完成状态
                        if "已完成" in page_text or "completed" in page_text.lower():
                            if last_status != "完成":
                                print(f"\n✅ [{elapsed}s] 研究完成！")
                                last_status = "完成"
                                return True
                        elif "分析结果中" in page_text or "正在分析" in page_text:
                            if last_status != "分析中":
                                print(f"⏳ [{elapsed}s] 分析结果中...")
                                last_status = "分析中"
                        elif "正在研究" in page_text or "Researching" in page_text:
                            if last_status != "研究中":
                                print(f"🔍 [{elapsed}s] 正在研究网站...")
                                last_status = "研究中"
                        elif "来源" in page_text:
                            # 有来源引用说明 Deep Research 已执行
                            print(f"📝 [{elapsed}s] 内容生成中 (检测到来源引用)...")
                            last_status = "生成中"
                        else:
                            print(f"⏳ [{elapsed}s] 处理中...")
                            
                    except:
                        print(f"⏳ [{elapsed}s] 等待中...")
                
                time.sleep(10)
            
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
        
        # 检查是否有 Deep Research 特征
        if "来源" in content:
            print("✅ 检测到 Deep Research 来源引用")
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            # 持久上下文不需要关闭浏览器，但需要关闭上下文
            if hasattr(self.browser, 'close'):
                self.browser.close()
            print("\n👋 浏览器已关闭")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gemini Deep Research 自动化（已登录版）')
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
            print("\n🎉 Deep Research 成功完成！")
            return 0
        else:
            print("\n⚠️  Deep Research 超时或未完成")
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
