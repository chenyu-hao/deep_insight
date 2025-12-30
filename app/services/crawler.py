import sys
import os
import asyncio
import re
import logging
from typing import List, Dict, Any
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MediaCrawler Integration ---
# Add MediaCrawler to sys.path to allow imports
MEDIA_CRAWLER_PATH = os.path.join(os.getcwd(), "MediaCrawler")
if MEDIA_CRAWLER_PATH not in sys.path:
    sys.path.append(MEDIA_CRAWLER_PATH)

try:
    import config
    from main import CrawlerFactory
    from base.base_crawler import AbstractStore
    from store.weibo import WeibostoreFactory
    from store.douyin import DouyinStoreFactory
    from store.kuaishou import KuaishouStoreFactory
    from store.bilibili import BiliStoreFactory
    from store.tieba import TieBaStoreFactory
    from store.zhihu import ZhihuStoreFactory
    from store.xhs import XhsStoreFactory
except ImportError as e:
    logger.error(f"Failed to import MediaCrawler modules: {e}")
    # We don't raise here to allow MockCrawler to work even if MediaCrawler fails
    pass

# --- Custom Store to Capture Data ---
class MemoryStore(AbstractStore):
    def __init__(self):
        self.results = []

    async def store_content(self, content_item: Dict):
        logger.info(f"Captured content: {content_item.get('note_id')}")
        self.results.append(content_item)

    async def store_comment(self, comment_item: Dict):
        pass 

    async def store_creator(self, creator: Dict):
        pass

# --- Unified Crawler Wrapper ---
class UnifiedCrawler:
    def __init__(self):
        self.memory_store = MemoryStore()
        self.store_factories = {
            "wb": WeibostoreFactory,
            "dy": DouyinStoreFactory,
            "ks": KuaishouStoreFactory,
            "bili": BiliStoreFactory,
            "tieba": TieBaStoreFactory,
            "zhihu": ZhihuStoreFactory,
            "xhs": XhsStoreFactory
        }

    async def crawl(self, inputs: List[str], platforms: List[str] = ["wb"]) -> str:
        """
        Crawl URLs or Search Keywords using MediaCrawler.
        Supports multiple platforms: wb, dy, ks, bili, tieba, zhihu, xhs.
        """
        # Reset store
        self.memory_store.results = []
        
        keywords = []
        urls = []
        for item in inputs:
             if "http" in item or "www" in item or ".com" in item or ".cn" in item:
                 urls.append(item)
             else:
                 keywords.append(item)

        results_text = ""
        
        # 1. Process Keywords (Search Mode) across all requested platforms
        if keywords:
            search_keywords = ",".join(keywords)
            logger.info(f"Starting Search for Keywords: {search_keywords} on platforms: {platforms}")
            
            # DEBUG: Check Event Loop Type
            loop = asyncio.get_running_loop()
            logger.info(f"🕷️ [DEBUG] Current Event Loop: {type(loop)}")
            
            for platform in platforms:
                if platform not in self.store_factories:
                    logger.warning(f"Platform {platform} not supported.")
                    continue
                    
                await self._run_mediacrawler(platform=platform, mode="search", keywords=search_keywords)

        # Collect Results
        max_items = settings.CRAWLER_LIMITS.get("wb", {}).get("max_items", 10) 
        
        limited_results = self.memory_store.results[:max_items]
        
        for item in limited_results:
            results_text += f"Platform: {item.get('platform', 'Unknown')}\n"
            results_text += f"URL: {item.get('note_url', 'N/A')}\n"
            results_text += f"Author: {item.get('nickname', 'Unknown')}\n"
            results_text += f"Content: {item.get('content', '')}\n"
            results_text += f"Time: {item.get('create_date_time', '')}\n"
            results_text += "-" * 50 + "\n"

        if not results_text:
            return ""

        return results_text

    async def _run_mediacrawler(self, platform: str, mode: str, weibo_ids: List[str] = None, keywords: str = None):
        factory = self.store_factories.get(platform)
        if not factory:
            return

        # 1. Monkeypatch Store Factory
        original_create_store = factory.create_store
        factory.create_store = lambda: self.memory_store

        # 2. Configure MediaCrawler
        # Save original config to restore later
        try:
            original_platform = config.PLATFORM
            original_crawler_type = config.CRAWLER_TYPE
            original_weibo_ids = getattr(config, 'WEIBO_SPECIFIED_ID_LIST', [])
            original_keywords = getattr(config, 'KEYWORDS', "")
            original_headless = config.HEADLESS
            original_proxy = config.ENABLE_IP_PROXY
            original_cdp = getattr(config, 'ENABLE_CDP_MODE', True)
            original_login_type = getattr(config, 'LOGIN_TYPE', "qrcode")
            original_max_notes = getattr(config, 'CRAWLER_MAX_NOTES_COUNT', 20)
            original_max_comments = getattr(config, 'CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES', 20)
        except AttributeError:
             # Handle case where config might not have all attributes
             pass
        
        try:
            config.PLATFORM = platform
            config.CRAWLER_TYPE = mode
            if mode == "detail" and weibo_ids and platform == "wb":
                config.WEIBO_SPECIFIED_ID_LIST = weibo_ids
            if mode == "search" and keywords:
                config.KEYWORDS = keywords
            
            config.HEADLESS = False # Set to False to allow login if needed
            config.ENABLE_IP_PROXY = False # Disable proxy for stability
            config.ENABLE_CDP_MODE = False # Disable CDP to ensure clean Playwright session
            config.LOGIN_TYPE = "qrcode"

            # Apply Limits
            platform_limits = settings.CRAWLER_LIMITS.get(platform, {})
            config.CRAWLER_MAX_NOTES_COUNT = platform_limits.get("max_items", 5)
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = platform_limits.get("max_comments", 10)
            
            # 3. Run Crawler
            logger.info(f"Running MediaCrawler: Platform={platform}, Mode={mode}, MaxNotes={config.CRAWLER_MAX_NOTES_COUNT}")
            crawler = CrawlerFactory.create_crawler(platform)
            await crawler.start()
            
        except Exception as e:
            logger.error(f"MediaCrawler execution failed for {platform}: {e}")
        finally:
            # Restore Config & Factory
            try:
                config.PLATFORM = original_platform
                config.CRAWLER_TYPE = original_crawler_type
                config.WEIBO_SPECIFIED_ID_LIST = original_weibo_ids
                config.KEYWORDS = original_keywords
                config.HEADLESS = original_headless
                config.ENABLE_IP_PROXY = original_proxy
                config.ENABLE_CDP_MODE = original_cdp
                config.LOGIN_TYPE = original_login_type
                config.CRAWLER_MAX_NOTES_COUNT = original_max_notes
                config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = original_max_comments
            except:
                pass
            factory.create_store = original_create_store
