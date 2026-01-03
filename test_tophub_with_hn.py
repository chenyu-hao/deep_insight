#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 TopHub 热榜是否包含 HN 数据
"""

import asyncio
from app.services.tophub_collector import tophub_collector
from loguru import logger

logger.enable("app")

async def test():
    """测试热榜收集"""
    print("=" * 80)
    print("测试热榜收集（包含 HN）")
    print("=" * 80)
    
    # 测试全量收集
    print("\n[1] 收集所有平台的热榜...")
    result = await tophub_collector.collect_news(source_ids=None, force_refresh=True)
    
    if result.get("success"):
        print(f"\n✓ 收集成功")
        print(f"  - 总榜单数: {result.get('total_sources')}")
        print(f"  - 成功数: {result.get('successful_sources')}")
        print(f"  - 总新闻数: {result.get('total_news')}")
        
        # 统计各平台
        news_list = result.get('news_list', [])
        sources = {}
        for news in news_list:
            source = news.get('source', '未知')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n平台分布：")
        for source, count in sorted(sources.items()):
            print(f"  - {source}: {count} 条")
        
        # 查找 HN 数据
        hn_news = [n for n in news_list if "HN" in n.get('source', '')]
        if hn_news:
            print(f"\n✓ HN 数据已包含 ({len(hn_news)} 条):")
            for n in hn_news[:3]:
                print(f"  - {n['title'][:50]}... (热度: {n['hot_value']})")
        else:
            print(f"\n✗ 未找到 HN 数据")
    else:
        print(f"✗ 收集失败: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test())
