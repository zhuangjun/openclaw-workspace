#!/usr/bin/env python3
"""
SeekingAlpha 登录并获取 Trending Analysis 文章 - 改进版
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import sys
import time

# 立即刷新输出
sys.stdout.flush()

# 账号信息
ACCOUNTS = [
    {"email": "jmsgm@zoey29.me", "password": "zxc123456"},
    {"email": "ewofzyx84@mailto.plus", "password": "Goersa%weu28"}
]

def create_driver():
    """创建Chrome浏览器实例"""
    print("启动浏览器...", flush=True)
    chrome_options = Options()
    # 暂时不使用headless以便调试
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    print("浏览器启动成功", flush=True)
    return driver

def try_login(driver, email, password):
    """尝试登录"""
    print(f"\n尝试登录: {email}", flush=True)
    
    driver.get("https://seekingalpha.com/account/login")
    time.sleep(4)
    
    try:
        # 查找输入框
        print("查找输入框...", flush=True)
        
        # 截图查看页面状态
        driver.save_screenshot("/tmp/sa_login_1.png")
        
        # 尝试多种方式查找邮箱输入框
        email_input = None
        selectors = ["input[type='email']", "input[name='email']", "input#email"]
        for sel in selectors:
            try:
                email_input = driver.find_element(By.CSS_SELECTOR, sel)
                print(f"找到邮箱输入框: {sel}", flush=True)
                break
            except:
                continue
        
        if not email_input:
            # 遍历所有input
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                if inp.get_attribute("type") == "email":
                    email_input = inp
                    print("通过type找到邮箱输入框", flush=True)
                    break
        
        if not email_input:
            print("未找到邮箱输入框", flush=True)
            return False
        
        # 查找密码输入框
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        print("找到密码输入框", flush=True)
        
        # 输入账号密码
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(0.5)
        
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(0.5)
        
        print("已输入账号密码", flush=True)
        
        # 查找并点击登录按钮
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()
            print("点击登录按钮", flush=True)
        except:
            # 尝试回车提交
            password_input.submit()
            print("使用表单提交", flush=True)
        
        time.sleep(5)
        
        # 检查登录结果
        current_url = driver.current_url
        print(f"当前URL: {current_url}", flush=True)
        
        driver.save_screenshot("/tmp/sa_after_login.png")
        
        if "login" not in current_url:
            print("登录成功！", flush=True)
            return True
        else:
            print("登录失败，仍在登录页面", flush=True)
            return False
            
    except Exception as e:
        print(f"登录出错: {e}", flush=True)
        driver.save_screenshot("/tmp/sa_error.png")
        return False

def get_articles(driver):
    """获取文章"""
    print("\n访问 Trending Analysis...", flush=True)
    driver.get("https://seekingalpha.com/trending-analysis")
    time.sleep(6)
    
    driver.save_screenshot("/tmp/sa_trending.png")
    
    articles = []
    
    try:
        # 等待文章加载
        wait = WebDriverWait(driver, 15)
        
        # 尝试多种选择器
        article_selectors = [
            "article",
            "[data-test-id='post-list-item']",
            ".post-list-item",
            "[class*='PostListItem']"
        ]
        
        article_elems = []
        for sel in article_selectors:
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, sel)))
                article_elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if len(article_elems) > 0:
                    print(f"找到 {len(article_elems)} 篇文章使用选择器: {sel}", flush=True)
                    break
            except:
                continue
        
        if not article_elems:
            print("未找到文章，保存页面源码...", flush=True)
            with open("/tmp/sa_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return articles
        
        # 提取前3篇文章
        for i, elem in enumerate(article_elems[:3]):
            try:
                # 查找标题
                title = ""
                try:
                    title_elem = elem.find_element(By.CSS_SELECTOR, "h2, h3, h4")
                    title = title_elem.text.strip()
                except:
                    pass
                
                # 查找链接
                link = ""
                try:
                    link_elem = elem.find_element(By.CSS_SELECTOR, "a")
                    link = link_elem.get_attribute("href")
                    if not title:
                        title = link_elem.text.strip()
                except:
                    pass
                
                # 查找摘要
                summary = ""
                try:
                    summary_elem = elem.find_element(By.CSS_SELECTOR, "p")
                    summary = summary_elem.text.strip()
                except:
                    pass
                
                if title:
                    articles.append({
                        "title": title,
                        "link": link,
                        "summary": summary
                    })
                    
            except Exception as e:
                print(f"处理第{i+1}篇文章出错: {e}", flush=True)
        
        return articles
        
    except Exception as e:
        print(f"获取文章出错: {e}", flush=True)
        return []

def main():
    driver = None
    try:
        driver = create_driver()
        
        # 尝试登录
        logged_in = False
        for acc in ACCOUNTS:
            if try_login(driver, acc["email"], acc["password"]):
                logged_in = True
                break
            time.sleep(2)
        
        if not logged_in:
            print("\n所有账号登录失败", flush=True)
            return
        
        # 获取文章
        articles = get_articles(driver)
        
        # 输出结果
        print("\n" + "="*60, flush=True)
        print("Trending Analysis 文章列表", flush=True)
        print("="*60, flush=True)
        
        for i, art in enumerate(articles[:3], 1):
            print(f"\n{i}. {art['title']}", flush=True)
            print(f"   - {art['link']}", flush=True)
            if art['summary']:
                summary = art['summary'][:150] + "..." if len(art['summary']) > 150 else art['summary']
                print(f"   - {summary}", flush=True)
            else:
                print(f"   - (无摘要)", flush=True)
        
        if not articles:
            print("\n未获取到文章", flush=True)
        
        # 保持浏览器打开以便查看
        print("\n等待15秒后关闭...", flush=True)
        time.sleep(15)
        
    except Exception as e:
        print(f"程序出错: {e}", flush=True)
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭", flush=True)

if __name__ == "__main__":
    main()
