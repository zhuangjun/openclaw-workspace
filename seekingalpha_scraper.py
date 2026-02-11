#!/usr/bin/env python3
"""
SeekingAlpha 登录并获取 Trending Analysis 文章
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# 账号信息
ACCOUNTS = [
    {"email": "jmsgm@zoey29.me", "password": "zxc123456"},
    {"email": "ewofzyx84@mailto.plus", "password": "Goersa%weu28"}
]

LOGIN_URL = "https://seekingalpha.com/account/login"
TRENDING_URL = "https://seekingalpha.com/trending-analysis"

def create_driver():
    """创建Chrome浏览器实例"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 调试时可以注释掉
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login(driver, email, password):
    """尝试登录SeekingAlpha"""
    print(f"尝试使用账号 {email} 登录...")
    driver.get(LOGIN_URL)
    time.sleep(3)
    
    try:
        # 等待页面加载
        wait = WebDriverWait(driver, 15)
        
        # 查找邮箱输入框 - 尝试多种可能的选择器
        email_selectors = [
            "input[name='email']",
            "input[type='email']",
            "input[id='email']",
            "input[placeholder*='email' i]",
            "input[data-testid*='email' i]"
        ]
        
        email_input = None
        for selector in email_selectors:
            try:
                email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"找到邮箱输入框: {selector}")
                break
            except:
                continue
        
        if not email_input:
            print("未找到邮箱输入框，尝试查找所有input元素...")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                input_type = inp.get_attribute("type") or ""
                input_name = inp.get_attribute("name") or ""
                if input_type == "email" or "email" in input_name.lower():
                    email_input = inp
                    print(f"通过遍历找到邮箱输入框: name={input_name}, type={input_type}")
                    break
        
        if not email_input:
            print("无法找到邮箱输入框")
            return False
        
        # 查找密码输入框
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "input[id='password']"
        ]
        
        password_input = None
        for selector in password_selectors:
            try:
                password_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"找到密码输入框: {selector}")
                break
            except:
                continue
        
        if not password_input:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                if inp.get_attribute("type") == "password":
                    password_input = inp
                    print("通过遍历找到密码输入框")
                    break
        
        if not password_input:
            print("无法找到密码输入框")
            return False
        
        # 输入账号密码
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(0.5)
        
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(0.5)
        
        # 查找登录按钮
        button_selectors = [
            "button[type='submit']",
            "button:contains('Sign')",
            "button:contains('Log')",
            "button[data-testid*='login' i]",
            "button[data-testid*='submit' i]"
        ]
        
        login_button = None
        for selector in button_selectors:
            try:
                if ":contains" in selector:
                    # 使用XPath处理包含文本的按钮
                    text = selector.split("'")[1]
                    xpath = f"//button[contains(text(), '{text}')]"
                    login_button = driver.find_element(By.XPATH, xpath)
                else:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"找到登录按钮: {selector}")
                break
            except:
                continue
        
        if not login_button:
            # 查找所有按钮
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                btn_text = btn.text.lower()
                if any(keyword in btn_text for keyword in ["sign", "log", "submit", "continue"]):
                    login_button = btn
                    print(f"通过遍历找到登录按钮: {btn_text}")
                    break
        
        if login_button:
            login_button.click()
            print("点击登录按钮")
        else:
            # 尝试按回车键
            password_input.submit()
            print("使用表单提交")
        
        time.sleep(5)
        
        # 检查是否登录成功
        # 通过检查URL或页面元素来判断
        current_url = driver.current_url
        print(f"当前URL: {current_url}")
        
        # 如果URL不包含login，说明登录成功
        if "login" not in current_url:
            print("登录成功！")
            return True
        
        # 检查是否有错误信息
        error_selectors = [
            "[data-testid*='error' i]",
            ".error",
            ".alert-danger",
            "[role='alert']"
        ]
        
        for selector in error_selectors:
            try:
                error_elem = driver.find_element(By.CSS_SELECTOR, selector)
                error_text = error_elem.text
                if error_text:
                    print(f"登录错误: {error_text}")
            except:
                pass
        
        return False
        
    except Exception as e:
        print(f"登录过程出错: {e}")
        return False

def get_trending_articles(driver):
    """获取trending analysis文章"""
    print("\n访问 Trending Analysis 页面...")
    driver.get(TRENDING_URL)
    time.sleep(5)
    
    articles = []
    
    try:
        wait = WebDriverWait(driver, 20)
        
        # 等待文章列表加载 - 尝试多种选择器
        article_selectors = [
            "[data-test-id='post-list-item']",
            "article",
            ".post-list-item",
            "[data-testid='article-item']",
            ".article-item",
            "[class*='article']",
            "[class*='Article']"
        ]
        
        article_elements = []
        for selector in article_selectors:
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                article_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(article_elements) >= 3:
                    print(f"找到文章元素: {selector}, 数量: {len(article_elements)}")
                    break
            except:
                continue
        
        if not article_elements:
            print("未找到文章元素，尝试查找所有链接...")
            # 尝试查找所有链接
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"页面共有 {len(links)} 个链接")
            
            # 保存页面源码用于调试
            with open("/tmp/sa_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("页面源码已保存到 /tmp/sa_page.html")
        
        # 处理找到的文章元素
        for i, article in enumerate(article_elements[:3]):
            try:
                # 查找标题
                title_elem = None
                title_selectors = ["h2", "h3", "h4", ".title", "[data-testid='title']", "a"]
                for sel in title_selectors:
                    try:
                        title_elem = article.find_element(By.CSS_SELECTOR, sel)
                        if title_elem.text.strip():
                            break
                    except:
                        continue
                
                title = title_elem.text.strip() if title_elem else f"文章 {i+1}"
                
                # 查找链接
                link = ""
                try:
                    if title_elem and title_elem.tag_name == "a":
                        link = title_elem.get_attribute("href")
                    else:
                        link_elem = article.find_element(By.CSS_SELECTOR, "a")
                        link = link_elem.get_attribute("href")
                except:
                    link = ""
                
                # 查找概要
                summary = ""
                summary_selectors = [".summary", ".description", "p", "[data-testid='summary']"]
                for sel in summary_selectors:
                    try:
                        summary_elem = article.find_element(By.CSS_SELECTOR, sel)
                        summary = summary_elem.text.strip()
                        if summary:
                            break
                    except:
                        continue
                
                articles.append({
                    "title": title,
                    "link": link,
                    "summary": summary
                })
                
            except Exception as e:
                print(f"处理第{i+1}篇文章时出错: {e}")
                continue
        
        return articles
        
    except Exception as e:
        print(f"获取文章时出错: {e}")
        return []

def main():
    driver = None
    try:
        driver = create_driver()
        print("浏览器已启动")
        
        # 尝试登录
        logged_in = False
        for account in ACCOUNTS:
            if login(driver, account["email"], account["password"]):
                logged_in = True
                break
            else:
                print(f"账号 {account['email']} 登录失败，尝试下一个账号...")
                time.sleep(2)
        
        if not logged_in:
            print("所有账号登录失败")
            return
        
        # 获取文章
        articles = get_trending_articles(driver)
        
        # 输出结果
        print("\n" + "="*60)
        print("Trending Analysis 文章列表")
        print("="*60)
        
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   - {article['link']}")
            if article['summary']:
                print(f"   - {article['summary'][:200]}..." if len(article['summary']) > 200 else f"   - {article['summary']}")
            else:
                print(f"   - (无摘要)")
        
        if not articles:
            print("未获取到文章")
        
        # 保持浏览器打开一会儿以便查看
        print("\n等待10秒后关闭...")
        time.sleep(10)
        
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        if driver:
            driver.quit()
            print("浏览器已关闭")

if __name__ == "__main__":
    main()
