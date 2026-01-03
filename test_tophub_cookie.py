#!/usr/bin/env python3
"""
测试提取的 Cookie 是否有效
"""

import asyncio
import httpx
from bs4 import BeautifulSoup

async def test_cookie():
    """测试 Cookie 是否能绕过 403"""
    
    cookie_str = "Hm_lvt_3b1e939f6e789219d8629de8a519eab9=1767331129; HMACCOUNT=255604C70285323D; Hm_lpvt_3b1e939f6e789219d8629de8a519eab9=1767414466"
    
    url = "https://tophub.today/hot"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh-HK;q=0.9,zh;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://tophub.today/",
        "Cookie": cookie_str,
        "Sec-Ch-Ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
    }
    
    print(f"测试 TopHub Cookie...")
    print(f"URL: {url}")
    print(f"Cookie: {cookie_str[:50]}...\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 检查是否是安全验证页面
                if "安全验证" in response.text:
                    print("❌ 仍然是安全验证页面，Cookie 可能已过期")
                    return False
                
                # 尝试解析热榜数据
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.find_all('li', class_='child-item')
                
                if items:
                    print(f"✅ 成功！找到 {len(items)} 条热榜数据")
                    print(f"\n示例数据:")
                    for i, item in enumerate(items[:3], 1):
                        title_a = item.select_one('p.medium-txt a')
                        if title_a:
                            print(f"  [{i}] {title_a.get_text(strip=True)[:60]}...")
                    
                    print(f"\n✅ Cookie 有效！TopHub 数据可以正常拉取")
                    print("   后端服务将使用此 Cookie 绕过 403")
                    return True
                else:
                    print("⚠️  页面返回 200 但未找到数据")
                    return False
                    
            elif response.status_code == 403:
                print("❌ 仍然返回 403，Cookie 无效或需要更多验证")
                return False
            else:
                print(f"⚠️  非预期状态码: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

async def main():
    success = await test_cookie()
    
    if success:
        print("\n" + "="*60)
        print("✅ Cookie 验证成功！")
        print("="*60)
        print("\n下一步:")
        print("  1. 重启后端服务")
        print("  2. 后端会自动使用 tophub_cookies.txt 中的 Cookie")
        print("  3. TopHub 数据应该能正常拉取了")
    else:
        print("\n" + "="*60)
        print("❌ Cookie 验证失败")
        print("="*60)
        print("\n可能原因:")
        print("  1. Cookie 已过期")
        print("  2. 需要额外的验证步骤")
        print("  3. TopHub 检测到脚本特征")

if __name__ == '__main__':
    asyncio.run(main())
