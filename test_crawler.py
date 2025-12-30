import asyncio
import sys
import os

# Add the project root to sys.path so we can import app modules
sys.path.append(os.getcwd())

from app.services.media_crawler import crawler_client

async def test_crawler():
    print("🧪 Testing MediaCrawler Integration...")
    
    # Test parameters
    # You can change this to "bili", "dy", "wb", "zhihu" etc.
    platform = "xhs" 
    keyword = "人工智能"
    
    print(f"🎯 Target: {platform}, Keyword: {keyword}")
    
    try:
        # Check if API is reachable first
        print("📡 Checking MediaCrawler API status...")
        status = await crawler_client.get_status()
        print(f"   API Status: {status}")
        
        if status.get("status") == "error":
             print("⚠️  Warning: API returned error status. Is it running?")

        # Call the crawler service
        print("⏳ Starting crawl job (this may take a minute)...")
        data = await crawler_client.crawl_and_wait(platform, keyword, timeout=120)
        
        if data:
            print(f"✅ Crawl successful! Retrieved {len(data)} items.")
            print("\n--- First Item Preview ---")
            first_item = data[0]
            print(f"Title: {first_item.get('title', 'No Title')}")
            print(f"Author: {first_item.get('nickname', 'Unknown')}")
            print(f"Desc: {first_item.get('desc', '')[:100]}...")
            print("--------------------------")
        else:
            print("❌ Crawl finished but returned no data.")
            
    except Exception as e:
        print(f"💥 Error during test: {e}")
        print("💡 Tip: Make sure the MediaCrawler API is running on port 8080")
        print("   Run command: cd MediaCrawler && python -m api.main")

if __name__ == "__main__":
    asyncio.run(test_crawler())
