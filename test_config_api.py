#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 API 返回的平台配置
"""

import httpx
import json


def test_config_api():
    """测试 /api/config 是否返回新平台"""
    print("=" * 80)
    print("测试 API 配置端点")
    print("=" * 80)
    
    try:
        response = httpx.get("http://127.0.0.1:8000/api/config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ 成功获取配置")
            
            # 显示所有可用平台
            if "platforms" in data:
                print(f"\n平台列表 ({len(data['platforms'])} 个):")
                for p in data["platforms"]:
                    print(f"  - {p}")
            
            # 显示爬虫限制
            if "crawler_limits" in data:
                print(f"\n爬虫限制配置:")
                for platform, limits in sorted(data["crawler_limits"].items()):
                    print(f"  {platform}: max_items={limits.get('max_items')}, max_comments={limits.get('max_comments')}")
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 异常: {e}")


if __name__ == "__main__":
    test_config_api()
