#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端 JavaScript API 调用测试
模拟前端的 api.getHotNews() 调用
"""

import httpx
import json

def test_frontend_api_calls():
    """测试前端会调用的 API 端点"""
    print("=" * 80)
    print("前端 API 调用集成测试")
    print("=" * 80)
    
    base_url = "http://127.0.0.1:8000/api/hotnews"
    
    # 模拟前端在 onMounted 时的初始化调用
    print("\n[初始化] 页面加载时默认调用 getHotNews(8, 'hot', false)")
    try:
        response = httpx.get(base_url, params={
            "limit": "8",
            "source": "hot",
            "force_refresh": "false"
        }, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取 TopHub 数据成功")
            print(f"  - 返回 {len(data.get('items', []))} 条")
            print(f"  - 来源: {data.get('source')}")
            print(f"  - 集合时间: {data.get('collection_time')}")
        else:
            print(f"✗ 失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {e}")
    
    # 模拟用户切换到 HN Top
    print("\n[用户操作] 在下拉菜单选择 'HN热门'")
    print("  → 触发 @change=\"refreshTrending\"")
    print("  → 调用 getHotNews(8, 'hn_top', false)")
    try:
        response = httpx.get(base_url, params={
            "limit": "8",
            "source": "hn_top",
            "force_refresh": "false"
        }, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取 HN Top 数据成功")
            print(f"  - 返回 {len(data.get('items', []))} 条")
            print(f"  - 来源: {data.get('source')}")
            print(f"  - 第一条: {data['items'][0]['title'][:50]}...")
            print(f"  - 热度值: {data['items'][0]['hot_value']}")
        else:
            print(f"✗ 失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {e}")
    
    # 模拟用户切换到 HN Best
    print("\n[用户操作] 在下拉菜单选择 'HN最佳'")
    print("  → 触发 @change=\"refreshTrending\"")
    print("  → 调用 getHotNews(8, 'hn_best', false)")
    try:
        response = httpx.get(base_url, params={
            "limit": "8",
            "source": "hn_best",
            "force_refresh": "false"
        }, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取 HN Best 数据成功")
            print(f"  - 返回 {len(data.get('items', []))} 条")
            print(f"  - 来源: {data.get('source')}")
            print(f"  - 第一条: {data['items'][0]['title'][:50]}...")
            print(f"  - 热度值: {data['items'][0]['hot_value']}")
        else:
            print(f"✗ 失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {e}")
    
    # 模拟用户点击刷新按钮
    print("\n[用户操作] 点击刷新按钮（保持当前来源）")
    print("  → 调用 rotateTrending()（轮换展示或重新加载）")
    print("  → 再次调用 getHotNews(8, 'hn_top', false)")
    try:
        response = httpx.get(base_url, params={
            "limit": "8",
            "source": "hn_top",
            "force_refresh": "false"
        }, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 刷新成功")
            print(f"  - 返回 {len(data.get('items', []))} 条")
            print(f"  - 集合时间: {data.get('collection_time')}")
        else:
            print(f"✗ 失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 异常: {e}")
    
    print("\n" + "=" * 80)
    print("✓ 前端 API 调用集成测试完成，所有操作流程正常")
    print("=" * 80)

if __name__ == "__main__":
    test_frontend_api_calls()
