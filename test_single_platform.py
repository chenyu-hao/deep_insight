#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试热榜平台筛选功能（使用 force_refresh）
"""

import asyncio
import httpx
import sys

# 设置输出编码为 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


async def test_single_platform():
    """测试单个平台（微博）"""
    base_url = "http://127.0.0.1:8000/api"
    
    print("=" * 100)
    print("测试单个平台热榜（微博）- 强制刷新")
    print("=" * 100)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("\n[1] 测试微博热榜 (source=KqndgxeLl9, force_refresh=true)")
        try:
            response = await client.get(
                f"{base_url}/hotnews",
                params={"limit": 10, "source": "KqndgxeLl9", "force_refresh": "true"}
            )
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            print(f"  OK 成功获取 {len(items)} 条数据")
            print(f"  from_cache: {data.get('from_cache')}")
            
            if items:
                print(f"\n  前 5 条新闻:")
                for i, item in enumerate(items[:5], 1):
                    title = item.get("title", "")[:60]
                    hot_value = item.get("hot_value", "N/A")
                    source = item.get("source", "")
                    source_id = item.get("source_id", "")
                    platform = item.get("platform", "")
                    print(f"    {i}. {title}")
                    print(f"       热度: {hot_value}, 来源: {source}, source_id: {source_id}, platform: {platform}")
                        
        except Exception as e:
            print(f"  ERROR 错误: {e}")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    asyncio.run(test_single_platform())
