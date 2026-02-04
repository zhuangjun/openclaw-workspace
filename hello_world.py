#!/usr/bin/env python3
"""
一个简单的Python示例程序
展示了基本的编程功能
"""

def greet(name):
    """向指定名称的人问候"""
    return f"Hello, {name}! Welcome to OpenClaw programming."

def calculate_sum(a, b):
    """计算两个数字的和"""
    return a + b

def main():
    """主函数"""
    print("欢迎来到编程示例!")
    
    # 基本问候
    name = input("请输入您的姓名: ")
    greeting = greet(name)
    print(greeting)
    
    # 简单计算
    print("\n让我们做些简单的数学计算:")
    num1 = float(input("请输入第一个数字: "))
    num2 = float(input("请输入第二个数字: "))
    
    result = calculate_sum(num1, num2)
    print(f"{num1} + {num2} = {result}")
    
    print("\n编程任务完成!")

if __name__ == "__main__":
    main()