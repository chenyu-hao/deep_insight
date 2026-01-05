#!/usr/bin/env python3
"""
测试 HN 与 HotView 的集成
验证后端能够正确处理 HN 平台的请求
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_hn_with_hotnews_collect():
    """测试通过 /hot-news/collect 端点获取 HN 新闻"""
    print("\n[TEST 1] 测试 /hot-news/collect 返回 HN 新闻")
    print("-" * 50)
    
    payload = {
        "platforms": ["hn"],
        "force_refresh": True
    }
    
    try:
        response = requests.post(f'{BASE_URL}/hot-news/collect', json=payload, timeout=10)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Success: {data.get('success')}")
        print(f"Total news: {data.get('total_news')}")
        print(f"From cache: {data.get('from_cache')}")
        
        news_list = data.get('news_list', [])
        if news_list:
            print(f"\n返回 {len(news_list)} 条 HN 新闻:")
            for i, news in enumerate(news_list[:3], 1):
                print(f"\n  [{i}] {news.get('title', 'N/A')[:60]}...")
                print(f"      热度: {news.get('hot_value', 'N/A')}")
                print(f"      来源: {news.get('source', 'N/A')}")
        else:
            print("❌ 未返回任何新闻")
            
        return response.status_code == 200 and data.get('success')
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
        print("⚠️  注意：此测试会获取 HN 新闻，耗时较长...")
        timeout=20


def test_hn_all_platforms():
    """测试获取所有平台（包括 HN）"""
    print("\n[TEST 2] 测试 /hot-news/collect 返回所有平台的新闻（包括 HN）")
    print("-" * 50)
    
    payload = {
        "platforms": ["all"],
        "force_refresh": False
    }
    
    try:
        response = requests.post(f'{BASE_URL}/hot-news/collect', json=payload, timeout=15)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Total news: {data.get('total_news')}")
        
        news_list = data.get('news_list', [])
        hn_count = sum(1 for n in news_list if n.get('source') == 'Hacker News')
        
        print(f"返回总数: {len(news_list)} 条新闻")
        print(f"其中 HN 新闻: {hn_count} 条")
        
        if hn_count > 0:
            print(f"\n✅ 成功包含 HN 新闻")
        else:
            print(f"⚠️  未检测到 HN 新闻（可能未加载）")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_supported_platforms():
    """测试获取支持的平台列表"""
    print("\n[TEST 3] 测试 /hot-news/platforms 端点")
    print("-" * 50)
    
    try:
        response = requests.get(f'{BASE_URL}/hot-news/platforms', timeout=5)
        data = response.json()
        
        platforms = data.get('platforms', [])
        hn_found = False
        
        print(f"支持的平台总数: {data.get('total_supported')}")
        
        for platform in platforms:
            if platform.get('source_id') == 'hn' or platform.get('name') == 'Hacker News':
                hn_found = True
                print(f"\n✅ 找到 HN 平台:")
                print(f"   名称: {platform.get('name')}")
                print(f"   类别: {platform.get('category')}")
                print(f"   优先级: {platform.get('priority')}")
                print(f"   描述: {platform.get('description', 'N/A')}")
                break
        
        if not hn_found:
            print("❌ 未找到 HN 平台")
            
        return response.status_code == 200 and hn_found
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_hn_direct_api():
    """测试直接访问 HN 专用端点"""
    print("\n[TEST 4] 测试 /hotnews/hn 端点（HN 专用接口）")
    print("-" * 50)
    
    try:
        response = requests.get(
            f'{BASE_URL}/hotnews/hn?limit=10&story_type=top&force_refresh=true',
            timeout=10
        )
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Success: {data.get('success')}")
        print(f"Total items: {data.get('total')}")
        print(f"Story type: {data.get('story_type')}")
        
        items = data.get('items', [])
        if items:
            print(f"\n返回 {len(items)} 条新闻:")
            for i, item in enumerate(items[:2], 1):
                print(f"\n  [{i}] {item.get('title', 'N/A')[:60]}...")
                print(f"      热度: {item.get('hot_value', 'N/A')}")
        
        return response.status_code == 200 and data.get('success')
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 50)
    print("HN 与 HotView 集成测试")
    print("=" * 50)
    
    results = []
    
    results.append(("HN 单独获取", test_hn_with_hotnews_collect()))
    results.append(("HN 在全平台中", test_hn_all_platforms()))
    results.append(("平台列表查询", test_supported_platforms()))
    results.append(("HN 专用接口", test_hn_direct_api()))
    
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！HN 已成功集成到 HotView")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")


if __name__ == '__main__':
    main()
