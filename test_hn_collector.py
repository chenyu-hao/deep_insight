#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 HN 收集器和 API 接口
"""

import asyncio
import httpx
import json
from datetime import datetime
from app.services.hn_hot_collector import hn_hot_collector


async def test_fetch_source_news():
    """测试单个榜单的新闻获取"""
    print("=" * 80)
    print("测试1: 获取单个榜单新闻（HN Top Stories）")
    print("=" * 80)
    
    result = await hn_hot_collector.fetch_source_news("top", max_items=10)
    
    print(f"\n返回结构:")
    print(f"  source_id: {result.get('source_id')}")
    print(f"  source_name: {result.get('source_name')}")
    print(f"  category: {result.get('category')}")
    print(f"  status: {result.get('status')}")
    print(f"  news_count: {result.get('news_count')}")
    print(f"  timestamp: {result.get('timestamp')}")
    
    print(f"\n前5条新闻详情:")
    for item in result.get('news_items', [])[:5]:
        print(f"\n  [排名 {item['rank']}] {item['title'][:60]}")
        print(f"    URL: {item['url'][:70]}")
        print(f"    热度: {item['hot_value']}")
        print(f"    得分: {item['score']}, 评论: {item['descendants']}")
        print(f"    作者: {item['by']}, 发布时间: {item['time']}")


async def test_collect_news():
    """测试多榜单的新闻收集"""
    print("\n" + "=" * 80)
    print("测试2: 收集多个榜单新闻（Top + Best）")
    print("=" * 80)
    
    result = await hn_hot_collector.collect_news(
        source_ids=["top", "best"],
        max_items=20,
        force_refresh=True
    )
    
    print(f"\n返回结构:")
    print(f"  success: {result.get('success')}")
    print(f"  total_news: {result.get('total_news')}")
    print(f"  successful_sources: {result.get('successful_sources')}")
    print(f"  total_sources: {result.get('total_sources')}")
    print(f"  collection_time: {result.get('collection_time')}")
    
    print(f"\n新闻列表（前10条）:")
    for item in result.get('news_list', [])[:10]:
        print(f"\n  ID: {item['id']}")
        print(f"  排名: {item['rank']}, 来源: {item['source']}")
        print(f"  标题: {item['title'][:60]}")
        print(f"  热度: {item['hot_value']}")
        print(f"  得分: {item['score']}, 评论: {item['descendants']}")
        print(f"  作者: {item['author']}")


async def test_api_endpoint():
    """测试 API 接口"""
    print("\n" + "=" * 80)
    print("测试3: API 接口调用 /api/hotnews/hn")
    print("=" * 80)
    
    # 测试前30条
    print("\n3.1 测试前30条（limit=30, story_type=top）")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:8000/api/hotnews/hn",
                params={"limit": 30, "story_type": "top"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 成功获取")
                print(f"  total: {data.get('total')}")
                print(f"  source: {data.get('source')}")
                print(f"  story_type: {data.get('story_type')}")
                print(f"  collection_time: {data.get('collection_time')}")
                
                print(f"\n  前5条新闻:")
                for item in data.get('items', [])[:5]:
                    print(f"    [{item['rank']}] {item['title'][:50]}")
                    print(f"        热度: {item['hot_value']}")
            else:
                print(f"✗ 失败: {response.status_code}")
                print(f"  {response.text}")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 测试前50条
    print("\n3.2 测试前50条（limit=50, story_type=best）")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:8000/api/hotnews/hn",
                params={"limit": 50, "story_type": "best"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 成功获取")
                print(f"  total: {data.get('total')}")
                print(f"  story_type: {data.get('story_type')}")
                
                if data.get('items'):
                    print(f"\n  最后5条新闻:")
                    for item in data.get('items', [])[-5:]:
                        print(f"    [{item['rank']}] {item['title'][:50]}")
                        print(f"        热度: {item['hot_value']}")
            else:
                print(f"✗ 失败: {response.status_code}")
                print(f"  {response.text}")
    except Exception as e:
        print(f"✗ 错误: {e}")


async def test_output_format_comparison():
    """对比 TopHub 和 HN 的输出格式"""
    print("\n" + "=" * 80)
    print("测试4: 输出格式对比（TopHub vs HN）")
    print("=" * 80)
    
    from app.services.tophub_collector import tophub_collector
    
    # 获取 TopHub 数据
    print("\n4.1 TopHub 数据结构:")
    tophub_result = await tophub_collector.collect_news(source_ids=["hot"], force_refresh=True)
    if tophub_result.get('success') and tophub_result.get('news_list'):
        item = tophub_result['news_list'][0]
        print(f"  keys: {list(item.keys())}")
        print(f"  示例: {json.dumps(item, ensure_ascii=False, indent=2)[:300]}")
    
    # 获取 HN 数据
    print("\n4.2 HN 数据结构:")
    hn_result = await hn_hot_collector.collect_news(source_ids=["top"], max_items=5)
    if hn_result.get('success') and hn_result.get('news_list'):
        item = hn_result['news_list'][0]
        print(f"  keys: {list(item.keys())}")
        print(f"  示例: {json.dumps(item, ensure_ascii=False, indent=2)[:300]}")
    
    print("\n4.3 格式分析:")
    print("""
    共同字段:
      - id: 唯一标识 (source_id_rank)
      - title: 新闻标题
      - url: 链接
      - hot_value: 热度值 (字符串)
      - rank: 排名
      - source: 来源名称
      - source_id: 来源ID
      - category: 分类
    
    HN 特有字段:
      - score: 得分 (数字)
      - descendants: 评论数 (数字)
      - author: 作者
      - posted_time: 发布时间戳
    
    TopHub 特有字段:
      - platform: 平台 (仅全榜有)
    """)


async def main():
    """运行所有测试"""
    try:
        # 本地测试不需要服务器
        print("\n" + "=" * 80)
        print("HN 收集器本地测试")
        print("=" * 80)
        
        await test_fetch_source_news()
        await test_collect_news()
        await test_output_format_comparison()
        
        # API 测试需要服务器运行
        print("\n" + "=" * 80)
        print("API 接口测试（需要服务器运行）")
        print("=" * 80)
        print("\n请确保后端服务已启动: python -m app.main")
        print("然后取消注释下面的代码来测试 API 接口")
        # await test_api_endpoint()
        
        print("\n" + "=" * 80)
        print("所有测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
