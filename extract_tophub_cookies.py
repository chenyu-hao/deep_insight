#!/usr/bin/env python3
"""
TopHub Cookie 管理工具
从浏览器提取 Cookie 并保存，供脚本使用
"""

import json
from pathlib import Path

def save_cookies_from_browser():
    """从浏览器手动复制 Cookie"""
    print("=" * 60)
    print("TopHub Cookie 提取工具")
    print("=" * 60)
    print("\n步骤：")
    print("1. 在浏览器中访问 https://tophub.today/hot")
    print("2. 按 F12 打开开发者工具")
    print("3. 切换到 Application(应用) 或 Storage(存储) 标签")
    print("4. 左侧找到 Cookies → https://tophub.today")
    print("5. 复制所有 Cookie（格式: name=value; name2=value2）")
    print("\n或者直接复制 Request Headers 中的 Cookie 行\n")
    print("-" * 60)
    
    cookie_str = input("请粘贴 Cookie 字符串: ").strip()
    
    if not cookie_str:
        print("❌ Cookie 为空，退出")
        return False
    
    # 保存到文件
    cookies_file = Path("tophub_cookies.txt")
    cookies_file.write_text(cookie_str, encoding='utf-8')
    
    print(f"\n✅ Cookie 已保存到: {cookies_file}")
    print("   后端服务将自动使用这些 Cookie")
    print("\n提示: Cookie 通常有效期为几天到几周")
    print("      如果以后又遇到 403，重新提取即可")
    
    return True

if __name__ == '__main__':
    save_cookies_from_browser()
