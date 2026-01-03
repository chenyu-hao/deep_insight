#!/usr/bin/env python3
"""
诊断 403 响应的具体内容，判断是否是 Cloudflare
"""

import asyncio
import httpx

async def diagnose():
    """诊断 TopHub 返回的 403"""
    
    url = "https://tophub.today/hot"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    
    print("诊断 TopHub 403 响应...")
    print(f"URL: {url}\n")
    
    try:
        # 不用代理，直接访问
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            print(f"状态码: {response.status_code}")
            print(f"响应头:")
            for key, value in response.headers.items():
                if key.lower() in ['server', 'cf-ray', 'cf-cache-status', 'content-type', 'set-cookie']:
                    print(f"  {key}: {value}")
            
            print(f"\n响应内容前 500 字符:")
            content = response.text[:500]
            print(content)
            
            # 检查是否是 Cloudflare
            if 'cloudflare' in response.text.lower():
                print("\n✅ 诊断: 这是 Cloudflare 的 403 响应")
                print("   原因: TopHub 部署了 Cloudflare，需要通过 JavaScript 挑战")
                print("   解决: 需要用真浏览器（Selenium/Playwright）或专门的 CF 绕过库")
            elif 'cf-ray' in response.headers:
                print("\n✅ 诊断: 这是 Cloudflare 返回的响应（cf-ray header）")
                print("   原因: Cloudflare 的 Bot Challenge 页面")
                print("   解决: 需要用真浏览器或专门的 Cloudflare 绕过工具")
            else:
                print("\n⚠️  诊断: 这是普通的 403，可能是 IP 黑名单")
                print("   原因: TopHub 直接拒绝了请求")
                print("   解决: 换 IP 或用代理")
    
    except Exception as e:
        print(f"❌ 错误: {e}")

asyncio.run(diagnose())
