import httpx
import asyncio
import json
from typing import List, Dict, Any, Optional
from app.config import settings

class MediaCrawlerClient:
    def __init__(self, base_url: str = settings.MEDIA_CRAWLER_API_URL):
        self.base_url = base_url

    async def start_crawler(self, platform: str, keywords: str, crawler_type: str = "search") -> bool:
        url = f"{self.base_url}/crawler/start"
        payload = {
            "platform": platform,
            "keywords": keywords,
            "crawler_type": crawler_type,
            "save_option": "json",
            "start_page": 1,
            "headless": True # Run headless by default
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=10.0)
                resp.raise_for_status()
                return True
            except Exception as e:
                print(f"Error starting crawler: {e}")
                return False

    async def get_status(self) -> Dict[str, Any]:
        url = f"{self.base_url}/crawler/status"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=5.0)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                print(f"Error getting status: {e}")
                return {"status": "error", "error_message": str(e)}

    async def get_latest_data_file(self, platform: str) -> Optional[str]:
        url = f"{self.base_url}/data/files"
        params = {"platform": platform, "file_type": "json"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, timeout=5.0)
                resp.raise_for_status()
                data = resp.json()
                files = data.get("files", [])
                if not files:
                    return None
                # Files are already sorted by modified_at desc
                return files[0]["path"]
            except Exception as e:
                print(f"Error listing files: {e}")
                return None

    async def get_file_content(self, file_path: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/data/files/{file_path}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=30.0)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                print(f"Error getting file content: {e}")
                return []

    async def crawl_and_wait(self, platform: str, keywords: str, timeout: int = 120) -> List[Dict[str, Any]]:
        # 1. Start
        print(f"🚀 Starting crawler for {platform} with keywords: {keywords}")
        if not await self.start_crawler(platform, keywords):
            print("Failed to start crawler. Is the MediaCrawler API running?")
            return []

        # 2. Wait for completion
        start_time = asyncio.get_event_loop().time()
        # Wait a bit for status to change to running
        await asyncio.sleep(2)
        
        while True:
            status_data = await self.get_status()
            status = status_data.get("status")
            print(f"Crawler status: {status}")
            
            if status == "idle":
                # Check if it finished successfully (we assume if it's idle after running, it's done)
                break
            
            if status == "error":
                print(f"Crawler error: {status_data.get('error_message')}")
                return []

            if asyncio.get_event_loop().time() - start_time > timeout:
                print("Crawler timed out")
                return []
            
            await asyncio.sleep(2)

        # 3. Fetch data
        print("Crawler finished, fetching data...")
        latest_file = await self.get_latest_data_file(platform)
        if not latest_file:
            print("No data file found.")
            return []
        
        print(f"Found data file: {latest_file}")
        content = await self.get_file_content(latest_file)
        return content

crawler_client = MediaCrawlerClient()
