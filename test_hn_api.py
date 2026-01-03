#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HN API Test"""

import httpx
import json
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"


async def test_hn_api():
    """Test HN API"""
    async with httpx.AsyncClient() as client:
        
        # Test 1: Top 30
        print("=" * 80)
        print("TEST 1: Get HN Top Stories (first 30 items)")
        print("=" * 80)
        
        try:
            response = await client.get(
                f"{BASE_URL}/api/hotnews/hn",
                params={"limit": 30, "story_type": "top", "force_refresh": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("[OK] Success - Status %d" % response.status_code)
                print("Total items: %d" % data.get('total'))
                print("Source: %s" % data.get('source'))
                print("Story Type: %s" % data.get('story_type'))
                
                items = data.get('items', [])
                print("\nFirst 3 items:")
                for item in items[:3]:
                    print("\n[%d] %s" % (item['rank'], item['title'][:70]))
                    print("    Hot: %s" % item['hot_value'])
                    print("    Score: %d | Comments: %d" % (item['score'], item['descendants']))
                    print("    Author: %s" % item['author'])
                
                if len(items) > 3:
                    print("\nLast 2 items:")
                    for item in items[-2:]:
                        print("\n[%d] %s" % (item['rank'], item['title'][:70]))
                        print("    Hot: %s" % item['hot_value'])
            else:
                print("[ERROR] Status %d" % response.status_code)
        except Exception as e:
            print("[ERROR] %s" % str(e))
        
        # Test 2: Best 50
        print("\n" + "=" * 80)
        print("TEST 2: Get HN Best Stories (first 50 items)")
        print("=" * 80)
        
        try:
            response = await client.get(
                f"{BASE_URL}/api/hotnews/hn",
                params={"limit": 50, "story_type": "best", "force_refresh": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("[OK] Success - Status %d" % response.status_code)
                print("Total items: %d" % data.get('total'))
                print("Story Type: %s" % data.get('story_type'))
            else:
                print("[ERROR] Status %d" % response.status_code)
        except Exception as e:
            print("[ERROR] %s" % str(e))
        
        # Test 3: New 20
        print("\n" + "=" * 80)
        print("TEST 3: Get HN New Stories (first 20 items)")
        print("=" * 80)
        
        try:
            response = await client.get(
                f"{BASE_URL}/api/hotnews/hn",
                params={"limit": 20, "story_type": "new", "force_refresh": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("[OK] Success - Status %d" % response.status_code)
                print("Total items: %d" % data.get('total'))
                print("Story Type: %s" % data.get('story_type'))
            else:
                print("[ERROR] Status %d" % response.status_code)
        except Exception as e:
            print("[ERROR] %s" % str(e))
        
        # Test 4: Item Structure
        print("\n" + "=" * 80)
        print("TEST 4: Single Item Structure")
        print("=" * 80)
        
        try:
            response = await client.get(
                f"{BASE_URL}/api/hotnews/hn",
                params={"limit": 1, "story_type": "top", "force_refresh": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    item = data['items'][0]
                    print("\nFirst item structure:")
                    print(json.dumps(item, ensure_ascii=False, indent=2))
            else:
                print("[ERROR] Status %d" % response.status_code)
        except Exception as e:
            print("[ERROR] %s" % str(e))
        
        print("\n" + "=" * 80)
        print("All tests completed!")
        print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_hn_api())
