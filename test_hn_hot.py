#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 HN 热榜功能
"""

import asyncio
from app.services.hn_hot_collector import hn_hot_collector
from loguru import logger

logger.enable("app")

async def test_hn_hot():
    """测试 HN 热榜收集"""
    print("=" * 80)
    print("测试 HN 热榜功能")
    print("=" * 80)
    
    # 测试 Top Stories
    print("\n[1] 测试 Top Stories...")
    result_top = await hn_hot_collector.collect_news(story_type="top", max_items=5)
    print(f"✓ 状态: {result_top.get('status')}")
    print(f"✓ 获取了 {result_top.get('news_count')} 条新闻")
    if result_top.get('news_items'):
        for i, item in enumerate(result_top['news_items'][:3], 1):
            print(f"\n  [{i}] {item['title']}")
            print(f"      分数: {item['score']} | 评论: {item['descendants']}")
            print(f"      链接: {item['url'][:60]}...")
    
    # 测试 Best Stories
    print("\n\n[2] 测试 Best Stories...")
    result_best = await hn_hot_collector.collect_news(story_type="best", max_items=5)
    print(f"✓ 状态: {result_best.get('status')}")
    print(f"✓ 获取了 {result_best.get('news_count')} 条新闻")
    if result_best.get('news_items'):
        for i, item in enumerate(result_best['news_items'][:3], 1):
            print(f"\n  [{i}] {item['title']}")
            print(f"      分数: {item['score']} | 评论: {item['descendants']}")
            print(f"      链接: {item['url'][:60]}...")
    
    print("\n" + "=" * 80)
    print("✓ 测试完成！HN 热榜功能正常运作")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_hn_hot())
