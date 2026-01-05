#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 HN 热榜 API 集成
"""

import httpx
import json

def test_hn_api():
    """测试 HN API"""
    print("=" * 80)
    print("测试 HN 热榜 API 集成")
    print("=" * 80)
    
    base_url = "http://127.0.0.1:8000/api/hotnews"
    
    # 测试 HN Top
    print("\n[1] 测试 HN Top Stories...")
    try:
        response = httpx.get(base_url, params={"limit": 3, "source": "hn_top"}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态码: {response.status_code}")
            print(f"✓ 返回: {len(data.get('items', []))} 条")
            print(f"✓ 来源: {data.get('source')}")
            print("\n  示例数据:")
            for i, item in enumerate(data.get('items', [])[:2], 1):
                print(f"    [{i}] {item['title']}")
                print(f"        热度: {item['hot_value']}")
                print(f"        URL: {item['url'][:60]}...")
        else:
            print(f"✗ 状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 测试 HN Best
    print("\n[2] 测试 HN Best Stories...")
    try:
        response = httpx.get(base_url, params={"limit": 3, "source": "hn_best"}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态码: {response.status_code}")
            print(f"✓ 返回: {len(data.get('items', []))} 条")
            print(f"✓ 来源: {data.get('source')}")
            print("\n  示例数据:")
            for i, item in enumerate(data.get('items', [])[:2], 1):
                print(f"    [{i}] {item['title']}")
                print(f"        热度: {item['hot_value']}")
                print(f"        URL: {item['url'][:60]}...")
        else:
            print(f"✗ 状态码: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    # 测试 TopHub（确保不影响原有功能）
    print("\n[3] 测试 TopHub 全榜（验证兼容性）...")
    try:
        response = httpx.get(base_url, params={"limit": 3, "source": "hot"}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态码: {response.status_code}")
            print(f"✓ 返回: {len(data.get('items', []))} 条")
            print(f"✓ 来源: {data.get('source')}")
        else:
            print(f"✗ 状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")
    
    print("\n" + "=" * 80)
    print("✓ API 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_hn_api()
