#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试热榜平台筛选功能
验证不同 source 参数能正确返回对应平台的热榜数据
"""

import asyncio
import httpx


async def test_hot_platform_filtering():
    """测试所有热榜平台筛选"""
    base_url = "http://127.0.0.1:8000/api"
    
    # 测试所有平台
    platforms = {
        "hot": "全部",
        "KqndgxeLl9": "微博",
        "mproPpoq6O": "知乎",
        "74KvxwokxM": "B站",
        "Jb0vmloB1G": "百度",
        "Om4ejxvxEN": "贴吧",
        "DpQvNABoNE": "抖音",
        "MZd7PrPerO": "快手",
        "hn_hot": "HN热门",
    }
    
    print("=" * 100)
    print("测试热榜平台筛选功能")
    print("=" * 100)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for source_id, platform_name in platforms.items():
            print(f"\n[{platform_name}] 测试 source={source_id}")
            try:
                response = await client.get(
                    f"{base_url}/hotnews",
                    params={"limit": 5, "source": source_id, "force_refresh": False}
                )
                response.raise_for_status()
                data = response.json()
                
                items = data.get("items", [])
                print(f"  ✓ 成功获取 {len(items)} 条数据")
                
                if items:
                    print(f"  示例:")
                    for i, item in enumerate(items[:3], 1):
                        title = item.get("title", "")[:50]
                        hot_value = item.get("hot_value", "N/A")
                        platform = item.get("platform", item.get("source", ""))
                        print(f"    {i}. {title}... (热度: {hot_value}, 平台: {platform})")
                        
                # 验证 HN 平台数据包含 platform 字段
                if source_id == "hn_hot" and items:
                    has_platform = all("platform" in item or "source" in item for item in items)
                    if has_platform:
                        print(f"  ✓ HN 数据包含 platform/source 字段")
                    else:
                        print(f"  ✗ 警告: HN 数据缺少 platform/source 字段")
                        
            except Exception as e:
                print(f"  ✗ 错误: {e}")
    
    print("\n" + "=" * 100)
    print("测试完成")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(test_hot_platform_filtering())
