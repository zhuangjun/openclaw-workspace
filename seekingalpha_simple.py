#!/usr/bin/env python3
"""
SeekingAlpha 登录并获取 Trending Analysis 文章 - 最简化版本
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# 账号信息
ACCOUNTS = [
    {"email": "jmsgm@zoey29.me", "password": "zxc123456"},
    {"email": "ewofzyx84@mailto.plus", "password": "Goersa%weu28"}
]

def main():
    # 启动浏览器
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 访问登录页面
        print("访问登录页面...")
        driver.get("https://seekingalpha.com/account/login")
        time.sleep(5)
        
        # 找到输入字段
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input#email"))
        )
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        
        # 尝试多个登录按钮选择器
        login_button = None
        for selector in ["button[type='submit']", "button"]:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
                if "log" in login_button.text.lower() or "sign" in login_button.text.lower() or login_button.get_attribute("type") == "submit":
                    break
            except:
                continue
        
        if not login_button:
            raise Exception("找不到登录按钮")
        
        # 尝试第一个账号
        success = False
        for account in ACCOUNTS:
            print(f"尝试登录账号: {account['email']}")
            
            # 清空并输入账号密码
            email_input.clear()
            email_input.send_keys(account['email'])
            time.sleep(0.5)
            
            password_input.clear()
            password_input.send_keys(account['password'])
            time.sleep(0.5)
            
            # 点击登录
            login_button.click()
            print("已点击登录按钮")
            
            time.sleep(5)
            
            # 检查是否登录成功
            current_url = driver.current_url
            print(f"当前URL: {current_url}")
            
            if "login" not in current_url.lower():
                print("登录成功!")
                success = True
                break
            else:
                print("登录失败，尝试下一个账号")
                time.sleep(2)
        
        if not success:
            print("所有账号登录失败")
            return
        
        # 访问 trending-analysis 页面
        print("访问 trending-analysis 页面...")
        driver.get("https://seekingalpha.com/trending-analysis")
        time.sleep(5)
        
        # 查找文章
        articles = []
        try:
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article, .post-list-item, [data-test-id='post-list-item']"))
            )
            
            # 查找文章元素
            article_elements = driver.find_elements(By.CSS_SELECTOR, "article, .post-list-item, [data-test-id='post-list-item']")
            
            print(f"找到 {len(article_elements)} 个文章元素")
            
            for i, elem in enumerate(article_elements[:3]):  # 只取前3个
                try:
                    # 查找标题
                    title_elem = None
                    for sel in ["h1", "h2", "h3", "h4", "a"]:
                        try:
                            title_elem = elem.find_element(By.CSS_SELECTOR, sel)
                            if title_elem.text.strip():
                                break
                        except:
                            continue
                    
                    title = title_elem.text.strip() if title_elem and title_elem.text.strip() else f"文章 {i+1}"
                    
                    # 查找链接
                    link = ""
                    if title_elem and title_elem.tag_name == "a":
                        link = title_elem.get_attribute("href")
                    else:
                        try:
                            link_elem = elem.find_element(By.CSS_SELECTOR, "a")
                            link = link_elem.get_attribute("href")
                        except:
                            pass
                    
                    # 查找摘要
                    summary = ""
                    for sel in ["p", ".summary", ".excerpt", ".description"]:
                        try:
                            summary_elem = elem.find_element(By.CSS_SELECTOR, sel)
                            if summary_elem.text.strip():
                                summary = summary_elem.text.strip()
                                break
                        except:
                            continue
                    
                    articles.append({
                        "title": title,
                        "link": link,
                        "summary": summary
                    })
                    
                except Exception as e:
                    print(f"提取第 {i+1} 篇文章时出错: {e}")
                    continue
        
        except Exception as e:
            print(f"查找文章时出错: {e}")
        
        # 输出结果
        print("\n" + "="*60)
        print("Trending Analysis 文章列表")
        print("="*60)
        
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   - 链接: {article['link']}")
            if article['summary']:
                print(f"   - 概要: {article['summary'][:200]}{'...' if len(article['summary']) > 200 else ''}")
            else:
                print(f"   - 概要: (无摘要)")
        
        if not articles:
            print("\n未获取到文章")
        
        print("\n浏览器将在30秒后关闭...")
        time.sleep(30)
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键关闭浏览器...")
    finally:
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    main()