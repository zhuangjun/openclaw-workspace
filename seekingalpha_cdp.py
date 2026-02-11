#!/usr/bin/env python3
"""
SeekingAlpha 登录并获取 Trending Analysis 文章
使用已运行的 Chrome 实例 (CDP)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import sys

# 账号信息
ACCOUNTS = [
    {"email": "jmsgm@zoey29.me", "password": "zxc123456"},
    {"email": "ewofzyx84@mailto.plus", "password": "Goersa%weu28"}
]

def create_driver_cdp():
    """连接到已运行的Chrome实例"""
    print("连接到已运行的Chrome实例...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:18800")
    
    driver = webdriver.Chrome(options=chrome_options)
    print("连接成功")
    return driver

def login(driver, email, password):
    """尝试登录"""
    print(f"\n尝试登录: {email}")
    
    driver.get("https://seekingalpha.com/account/login")
    time.sleep(4)
    
    try:
        print("查找输入框...")
        
        # 查找邮箱输入框
        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        print("找到邮箱输入框")
        
        # 查找密码输入框
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        print("找到密码输入框")
        
        # 输入账号密码
        email_input.clear()
        email_input.send_keys(email)
        time.sleep(0.5)
        
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(0.5)
        
        print("已输入账号密码")
        
        # 查找并点击登录按钮
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()
            print("点击登录按钮")
        except:
            password_input.submit()
            print("使用表单提交")
        
        time.sleep(5)
        
        # 检查登录结果
        current_url = driver.current_url
        print(f"当前URL: {current_url}")
        
        if "login" not in current_url:
            print("登录成功！")
            return True
        else:
            print("登录失败")
            return False
            
    except Exception as e:
        print(f"登录出错: {e}")
        return False

def get_articles(driver):
    """获取文章"""
    print("\n访问 Trending Analysis...")
    driver.get("https://seekingalpha.com/trending-analysis")
    time.sleep(6)
    
    articles = []
    
    try:
        wait = WebDriverWait(driver, 15)
        
        # 尝试多种选择器
        selectors = ["article", "[data-test-id='post-list-item']", ".post-list-item"]
        article_elems = []
        
        for sel in selectors:
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, sel)))
                article_elems = driver.find_elements(By.CSS_SELECTOR, sel)
                if len(article_elems) > 0:
                    print(f"找到 {len(article_elems)} 篇文章")
                    break
            except:
                continue
        
        if not article_elems:
            print("未找到文章")
            # 保存页面源码用于调试
            with open("/tmp/sa_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("页面源码已保存")
            return articles
        
        # 提取前3篇文章
        for i, elem in enumerate(article_elems[:3]):
            try:
                # 查找标题
                title = ""
                title_elem = None
                for sel in ["h2", "h3", "h4", "a"]:
                    try:
                        title_elem = elem.find_element(By.CSS_SELECTOR, sel)
                        title = title_elem.text.strip()
                        if title:
                            break
                    except:
                        continue
                
                # 查找链接
                link = ""
                try:
                    if title_elem and title_elem.tag_name == "a":
                        link = title_elem.get_attribute("href")
                    else:
                        link_elem = elem.find_element(By.CSS_SELECTOR, "a")
                        link = link_elem.get_attribute("href")
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
                print(f"处理第{i+1}篇文章出错: {e}")
        
        return articles
        
    except Exception as e:
        print(f"获取文章出错: {e}")
        return []

def main():
    driver = None
    try:
        driver = create_driver_cdp()
        
        # 尝试登录
        logged_in = False
        for acc in ACCOUNTS:
            if login(driver, acc["email"], acc["password"]):
                logged_in = True
                break
            time.sleep(2)
        
        if not logged_in:
            print("\n所有账号登录失败")
            return
        
        # 获取文章
        articles = get_articles(driver)
        
        # 输出结果
        print("\n" + "="*60)
        print("Trending Analysis 文章列表")
        print("="*60)
        
        for i, art in enumerate(articles[:3], 1):
            print(f"\n{i}. {art['title']}")
            print(f"   - {art['link']}")
            if art['summary']:
                summary = art['summary'][:150] + "..." if len(art['summary']) > 150 else art['summary']
                print(f"   - {summary}")
            else:
                print(f"   - (无摘要)")
        
        if not articles:
            print("\n未获取到文章")
        
        # 保持浏览器打开
        print("\n任务完成，浏览器保持打开状态")
        
    except Exception as e:
        print(f"程序出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
