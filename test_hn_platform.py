#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 HN 热榜作为平台的完整集成
"""

import asyncio
from app.services.crawler_router_service import crawler_router_service


async def test_hn_hot_as_platform():
    """测试 HN 热榜作为平台的完整流程"""
    print("=" * 80)
    print("测试 HN 热榜作为爬虫平台集成")
    print("=" * 80)
    
    # 测试支持的平台列表
    print("\n[1] 支持的平台列表:")
    platforms = crawler_router_service.supported_platforms
    print(f"  {', '.join(platforms)}")
    
    # 测试 HN 热榜爬虫
    print("\n[2] 测试爬取 HN 热门故事（hn_hot）...")
    try:
        results = await crawler_router_service.crawl_platform(
            platform="hn_hot",
            keywords="test",  # HN热榜不使用关键字，只是占位符
            max_items=5,
            timeout=30
        )
        print(f"✓ 成功获取 {len(results)} 条数据")
        if results:
            print(f"\n  第一条数据:")
            item = results[0]
            print(f"    标题: {item.get('title', '')[:50]}...")
            print(f"    热度: {item.get('hot_value', '')} points")
            print(f"    URL: {item.get('url', '')[:60]}...")
            print(f"    平台: {item.get('platform', '')}")
            print(f"    评论数: {item.get('comments', 0)}")
    except Exception as e:
        print(f"✗ 失败: {e}")
    
    # 测试 HN 最佳故事
    print("\n[3] 测试爬取 HN 最佳故事（hn_best）...")
    try:
        results = await crawler_router_service.crawl_platform(
            platform="hn_best",
            keywords="test",
            max_items=5,
            timeout=30
        )
        print(f"✓ 成功获取 {len(results)} 条数据")
        if results:
            print(f"\n  第一条数据:")
            item = results[0]
            print(f"    标题: {item.get('title', '')[:50]}...")
            print(f"    热度: {item.get('hot_value', '')} points")
            print(f"    平台: {item.get('platform', '')}")
    except Exception as e:
        print(f"✗ 失败: {e}")
    
    # 测试 HN 搜索（原有功能）
    print("\n[4] 测试 HN 搜索功能（保证向后兼容）...")
    try:
        results = await crawler_router_service.crawl_platform(
            platform="hn",
            keywords="AI",
            max_items=3,
            timeout=30
        )
        print(f"✓ 成功获取 {len(results)} 条搜索结果")
        if results:
            print(f"\n  第一条:")
            item = results[0]
            print(f"    标题: {item.get('title', '')[:50]}...")
            print(f"    平台: {item.get('platform', '')}")
    except Exception as e:
        print(f"✗ 失败: {e}")
    
    # 测试平台标准化
    print("\n[5] 测试平台名称标准化:")
    for input_name in ["hn_top", "hn_best", "hn_hot"]:
        normalized = crawler_router_service.normalize_platform(input_name)
        print(f"  {input_name} → {normalized}")
    
    print("\n" + "=" * 80)
    print("✓ HN 热榜作为平台的集成测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_hn_hot_as_platform())
