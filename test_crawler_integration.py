"""
Test script for MediaCrawler integration
Tests the crawler service with a sample topic
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.media_crawler_service import crawler_service


async def test_single_platform():
    """Test crawling a single platform"""
    print("=" * 60)
    print("🧪 Testing Single Platform Crawler")
    print("=" * 60)
    
    platform = "wb"  # Start with Weibo as it's more stable
    keywords = "武汉大学"
    
    print(f"\n📌 Platform: {platform}")
    print(f"🔍 Keywords: {keywords}")
    print("\n⏳ Starting crawl...\n")
    
    try:
        results = await crawler_service.crawl_platform(
            platform=platform,
            keywords=keywords,
            max_items=10,  # Limit to 10 items for testing
            timeout=180  # 3 minutes timeout
        )
        
        print(f"\n✅ Crawl completed!")
        print(f"📊 Results: {len(results)} items found\n")
        
        if results:
            print("📝 Sample items:")
            for i, item in enumerate(results[:3], 1):
                print(f"\n--- Item {i} ---")
                print(f"Platform: {item.get('platform')}")
                print(f"Title: {item.get('title', '')[:50]}...")
                print(f"Content: {item.get('content', '')[:100]}...")
                print(f"Author: {item.get('author', {}).get('nickname', 'Unknown')}")
                print(f"Interactions: {item.get('interactions', {})}")
                print(f"URL: {item.get('url', '')}")
        else:
            print("⚠️ No results found. This could be due to:")
            print("  1. No content matching the keywords")
            print("  2. Login/authentication issues")
            print("  3. Network/timeout issues")
            print("  4. Platform API changes")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_platforms():
    """Test crawling multiple platforms concurrently"""
    print("\n" + "=" * 60)
    print("🧪 Testing Multiple Platforms Crawler")
    print("=" * 60)
    
    platforms = ["wb", "bili"]  # Test with Weibo and Bilibili first
    keywords = "武汉大学"
    
    print(f"\n📌 Platforms: {platforms}")
    print(f"🔍 Keywords: {keywords}")
    print("\n⏳ Starting concurrent crawl...\n")
    
    try:
        results = await crawler_service.crawl_multiple_platforms(
            platforms=platforms,
            keywords=keywords,
            max_items_per_platform=5,  # Limit for testing
            timeout_per_platform=180,
            max_concurrent=2
        )
        
        print(f"\n✅ Concurrent crawl completed!")
        
        total_items = 0
        for platform, items in results.items():
            count = len(items)
            total_items += count
            print(f"  {platform}: {count} items")
        
        print(f"\n📊 Total: {total_items} items from {len(results)} platforms\n")
        
        if total_items > 0:
            print("📝 Sample from each platform:")
            for platform, items in results.items():
                if items:
                    item = items[0]
                    print(f"\n--- {platform.upper()} ---")
                    print(f"Title: {item.get('title', '')[:50]}...")
                    print(f"Author: {item.get('author', {}).get('nickname', 'Unknown')}")
        
        return total_items > 0
        
    except Exception as e:
        print(f"\n❌ Error during concurrent crawl: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_workflow_integration():
    """Test the full workflow integration"""
    print("\n" + "=" * 60)
    print("🧪 Testing Workflow Integration")
    print("=" * 60)
    
    from app.services.workflow import app_graph
    
    topic = "武汉大学"
    platforms = ["wb"]  # Use Weibo for workflow test
    
    print(f"\n📌 Topic: {topic}")
    print(f"📌 Platforms: {platforms}")
    print("\n⏳ Running workflow...\n")
    
    try:
        initial_state = {
            "topic": topic,
            "platforms": platforms,
            "urls": [],
            "messages": [],
            "crawler_data": [],
            "platform_data": {}
        }
        
        # Run workflow with streaming
        step_count = 0
        async for event in app_graph.astream(initial_state):
            step_count += 1
            for node_name, state_update in event.items():
                messages = state_update.get("messages", [])
                if messages:
                    print(f"  [{node_name}] {messages[-1][:100]}...")
                
                # Check if crawler data was collected
                if node_name == "crawler_agent":
                    crawler_data = state_update.get("crawler_data", [])
                    if crawler_data:
                        print(f"  ✅ Crawler collected {len(crawler_data)} items")
        
        print(f"\n✅ Workflow completed in {step_count} steps")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during workflow: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "🚀 MediaCrawler Integration Tests" + "\n")
    
    results = []
    
    # Test 1: Single platform
    print("\n" + "─" * 60)
    result1 = await test_single_platform()
    results.append(("Single Platform", result1))
    
    # Test 2: Multiple platforms (only if single platform works)
    if result1:
        print("\n" + "─" * 60)
        result2 = await test_multiple_platforms()
        results.append(("Multiple Platforms", result2))
    else:
        print("\n⚠️ Skipping multiple platforms test (single platform failed)")
        results.append(("Multiple Platforms", False))
    
    # Test 3: Workflow integration (only if crawler works)
    if result1:
        print("\n" + "─" * 60)
        result3 = await test_workflow_integration()
        results.append(("Workflow Integration", result3))
    else:
        print("\n⚠️ Skipping workflow test (crawler failed)")
        results.append(("Workflow Integration", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed"))
    print("=" * 60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
