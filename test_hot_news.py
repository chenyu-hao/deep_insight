#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试热点新闻收集功能
支持测试所有平台或指定平台
"""

import asyncio
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.services.hot_news_collector import hot_news_collector, SOURCE_NAMES


async def test_collect_news(sources=None, top_n=10):
    """
    测试收集新闻
    
    Args:
        sources: 指定的新闻源列表，None表示使用所有支持的源
        top_n: 每个平台显示前N条热点，默认10条
    """
    print("=" * 80)
    print("测试热点新闻收集功能")
    print("=" * 80)
    
    # 如果没有指定源，使用所有支持的源
    if sources is None:
        sources = list(SOURCE_NAMES.keys())
        print(f"将测试所有 {len(sources)} 个平台:")
        for source in sources:
            print(f"  - {SOURCE_NAMES.get(source, source)}")
    else:
        print(f"将测试 {len(sources)} 个指定平台:")
        for source in sources:
            print(f"  - {SOURCE_NAMES.get(source, source)}")
    
    print()
    
    result = await hot_news_collector.collect_news(sources=sources)
    
    print("\n" + "=" * 80)
    print("收集结果:")
    print("=" * 80)
    print(f"成功: {result['success']}")
    print(f"总新闻数: {result.get('total_news', 0)}")
    print(f"成功源数: {result.get('successful_sources', 0)}/{result.get('total_sources', 0)}")
    
    if result['success'] and result.get('news_list'):
        # 按平台分组显示
        from collections import defaultdict
        news_by_platform = defaultdict(list)
        
        for news in result['news_list']:
            platform = news.get('source_name', '未知平台')
            news_by_platform[platform].append(news)
        
        # 按平台显示热点排行
        print("\n" + "=" * 80)
        print("各平台热点排行:")
        print("=" * 80)
        
        for platform, news_list in sorted(news_by_platform.items()):
            # 按排名排序
            sorted_news = sorted(news_list, key=lambda x: x.get('rank', 999))
            
            print(f"\n【{platform}】热点排行 (共 {len(sorted_news)} 条):")
            print("-" * 80)
            # 显示每个平台的前N条（或全部，如果少于N条）
            display_count = min(top_n, len(sorted_news))
            for news in sorted_news[:display_count]:
                title = news.get('title', '无标题')
                url = news.get('url', '')
                rank = news.get('rank', 0)
                print(f"  {rank:2d}. {title}")
                if url:
                    print(f"      🔗 {url}")
            if len(sorted_news) > display_count:
                print(f"  ... 还有 {len(sorted_news) - display_count} 条新闻")
    
    return result


def main():
    """主函数，支持命令行参数"""
    parser = argparse.ArgumentParser(description="测试热点新闻收集功能")
    parser.add_argument(
        "--sources", 
        nargs="+", 
        help="指定要测试的新闻源（不指定则测试所有平台）",
        choices=list(SOURCE_NAMES.keys())
    )
    parser.add_argument(
        "--top", 
        type=int, 
        default=10, 
        help="每个平台显示前N条热点（默认10条）"
    )
    parser.add_argument(
        "--list-sources", 
        action="store_true", 
        help="列出所有支持的新闻源"
    )
    
    args = parser.parse_args()
    
    # 列出所有支持的源
    if args.list_sources:
        print("支持的新闻源平台:")
        for source, name in SOURCE_NAMES.items():
            print(f"  {source:<25} {name}")
        return
    
    # 运行测试
    asyncio.run(test_collect_news(sources=args.sources, top_n=args.top))


if __name__ == "__main__":
    main()
