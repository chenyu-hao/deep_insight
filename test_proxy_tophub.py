#!/usr/bin/env python3
"""
测试通过代理拉取 TopHub 数据
"""

import os
import asyncio
import httpx
from bs4 import BeautifulSoup

async def test_with_proxy():
    """测试通过代理访问 TopHub"""
    # 设置代理
    proxy_url = "http://127.0.0.1:7897"
    
    url = "https://tophub.today/hot"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://tophub.today/",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    
    print(f"\n尝试通过代理 {proxy_url} 访问 TopHub...")
    print(f"URL: {url}")
    
    try:
        # httpx 代理使用 httpx.HTTPTransport 或直接传 proxy 参数
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            proxy=proxy_url
        ) as client:
            response = await client.get(url, headers=headers)
            
            print(f"\n✅ 连接成功")
            print(f"状态码: {response.status_code}")
            print(f"响应大小: {len(response.text)} 字节")
            
            if response.status_code == 200:
                # 简单解析看看能否获取数据
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.find_all('li', class_='child-item')
                print(f"✅ 成功解析，找到 {len(items)} 条热榜数据")
                
                if items:
                    # 显示第一条
                    first = items[0]
                    title_a = first.select_one('p.medium-txt a')
                    if title_a:
                        print(f"\n示例: {title_a.get_text(strip=True)[:80]}")
                
                return True
            elif response.status_code == 403:
                print(f"❌ 仍然返回 403，代理可能未生效或 IP 依然被封")
                return False
            else:
                print(f"⚠️  非预期状态码: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        print(f"   可能原因: 代理服务未启动或端口错误")
        return False

async def main():
    success = await test_with_proxy()
    if success:
        print("\n✅ 代理工作正常，TopHub 数据可正常拉取")
        print("   后端已配置使用代理，重启服务即可生效")
    else:
        print("\n❌ 代理测试失败")
        print("   请检查:")
        print("   1. 代理服务是否已启动")
        print("   2. 端口是否正确 (当前: 7897)")
        print("   3. 是否需要身份验证")

if __name__ == '__main__':
    asyncio.run(main())
