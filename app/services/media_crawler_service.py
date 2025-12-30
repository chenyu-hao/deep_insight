"""
MediaCrawler Service - Direct library integration
Encapsulates MediaCrawler crawler calls with proper configuration isolation
"""
import asyncio
import sys
import os
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import importlib

# Add MediaCrawler to path if needed
MEDIA_CRAWLER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "MediaCrawler")
if MEDIA_CRAWLER_PATH not in sys.path:
    sys.path.insert(0, MEDIA_CRAWLER_PATH)

from app.services.in_memory_store import InMemoryStore


class MediaCrawlerService:
    """Service for crawling social media platforms using MediaCrawler library"""
    
    # Platform mapping
    PLATFORM_MAP = {
        "xhs": "xhs",
        "xiaohongshu": "xhs",
        "dy": "dy",
        "douyin": "dy",
        "ks": "ks",
        "kuaishou": "ks",
        "bili": "bili",
        "bilibili": "bili",
        "wb": "wb",
        "weibo": "wb",
        "tieba": "tieba",
        "zhihu": "zhihu",
    }
    
    def __init__(self):
        self.in_memory_store = InMemoryStore()
        self._crawler_instances: Dict[str, Any] = {}
    
    def _normalize_platform(self, platform: str) -> str:
        """Normalize platform name to MediaCrawler format"""
        platform_lower = platform.lower()
        return self.PLATFORM_MAP.get(platform_lower, platform_lower)
    
    @contextmanager
    def _configure_mediacrawler(self, platform: str, keywords: str, max_items: int = 20):
        """Context manager to temporarily configure MediaCrawler"""
        # Import config module
        import config as mc_config
        
        # Normalize platform first
        normalized_platform = self._normalize_platform(platform)
        
        # Save original values
        original_platform = getattr(mc_config, "PLATFORM", None)
        original_keywords = getattr(mc_config, "KEYWORDS", None)
        original_max_notes = getattr(mc_config, "CRAWLER_MAX_NOTES_COUNT", None)
        original_save_option = getattr(mc_config, "SAVE_DATA_OPTION", None)
        original_crawler_type = getattr(mc_config, "CRAWLER_TYPE", None)
        original_headless = getattr(mc_config, "HEADLESS", None)
        original_cdp_headless = getattr(mc_config, "CDP_HEADLESS", None)
        original_enable_cdp = getattr(mc_config, "ENABLE_CDP_MODE", None)
        original_enable_medias = getattr(mc_config, "ENABLE_GET_MEIDAS", None)
        original_enable_comments = getattr(mc_config, "ENABLE_GET_COMMENTS", None)
        original_enable_sub_comments = getattr(mc_config, "ENABLE_GET_SUB_COMMENTS", None)
        
        try:
            # Set temporary configuration
            mc_config.PLATFORM = normalized_platform
            mc_config.KEYWORDS = keywords
            mc_config.CRAWLER_MAX_NOTES_COUNT = max_items
            mc_config.CRAWLER_TYPE = "search"
            # For platforms that require login, use non-headless mode
            # Bilibili and Weibo need visible browser for login
            if normalized_platform in ["wb", "bili"]:
                mc_config.HEADLESS = False  # Need visible browser for login
                mc_config.CDP_HEADLESS = False
            else:
                mc_config.HEADLESS = True  # Other platforms can use headless
                mc_config.CDP_HEADLESS = True
            mc_config.ENABLE_CDP_MODE = True  # Use CDP mode for better stability
            mc_config.SAVE_DATA_OPTION = "json"  # We'll intercept store calls
            # Set login type - use cookie if available, otherwise qrcode
            # For Bilibili, prefer cookie login to avoid manual QR code scanning
            if normalized_platform == "bili":
                # Try cookie login first if cookies are available
                if mc_config.COOKIES and mc_config.COOKIES.strip():
                    mc_config.LOGIN_TYPE = "cookie"  # Use saved cookies
                else:
                    # No cookie available, will need QR code login
                    # But we'll set a shorter timeout for login
                    mc_config.LOGIN_TYPE = "qrcode"  # Will show QR code for manual login
                    print(f"[INFO] Bilibili requires login. Browser will open for QR code login.")
                    print(f"[INFO] Please scan the QR code within 2 minutes, or configure COOKIES to skip login.")
            else:
                mc_config.LOGIN_TYPE = "qrcode"  # Default to QR code login
            # Disable media download to speed up crawling
            mc_config.ENABLE_GET_MEIDAS = False
            mc_config.ENABLE_GET_COMMENTS = True  # Keep comments enabled
            mc_config.ENABLE_GET_SUB_COMMENTS = False  # Disable sub-comments to speed up
            
            # Set source keyword var
            from var import source_keyword_var
            source_keyword_var.set(keywords)
            
            yield
            
        finally:
            # Restore original values
            if original_platform is not None:
                mc_config.PLATFORM = original_platform
            if original_keywords is not None:
                mc_config.KEYWORDS = original_keywords
            if original_max_notes is not None:
                mc_config.CRAWLER_MAX_NOTES_COUNT = original_max_notes
            if original_save_option is not None:
                mc_config.SAVE_DATA_OPTION = original_save_option
            if original_crawler_type is not None:
                mc_config.CRAWLER_TYPE = original_crawler_type
            if original_headless is not None:
                mc_config.HEADLESS = original_headless
            if original_cdp_headless is not None:
                mc_config.CDP_HEADLESS = original_cdp_headless
            if original_enable_cdp is not None:
                mc_config.ENABLE_CDP_MODE = original_enable_cdp
            if original_enable_medias is not None:
                mc_config.ENABLE_GET_MEIDAS = original_enable_medias
            if original_enable_comments is not None:
                mc_config.ENABLE_GET_COMMENTS = original_enable_comments
            if original_enable_sub_comments is not None:
                mc_config.ENABLE_GET_SUB_COMMENTS = original_enable_sub_comments
    
    def _patch_store_for_platform(self, platform: str):
        """Patch store factory to use InMemoryStore"""
        normalized_platform = self._normalize_platform(platform)
        
        # Map platform to store module and factory class name
        platform_config = {
            "xhs": ("store.xhs", "XhsStoreFactory"),
            "dy": ("store.douyin", "DouyinStoreFactory"),
            "ks": ("store.kuaishou", "KuaishouStoreFactory"),
            "bili": ("store.bilibili", "BiliStoreFactory"),
            "wb": ("store.weibo", "WeibostoreFactory"),  # Note: lowercase 's' in WeibostoreFactory
            "tieba": ("store.tieba", "TieBaStoreFactory"),
            "zhihu": ("store.zhihu", "ZhihuStoreFactory"),
        }
        
        config = platform_config.get(normalized_platform)
        if not config:
            return None
        
        store_module_name, factory_class_name = config
        
        try:
            # Import store module
            store_module = importlib.import_module(store_module_name)
            
            # Get factory class
            if not hasattr(store_module, factory_class_name):
                print(f"Warning: Factory class {factory_class_name} not found in {store_module_name}")
                return None
            
            factory_class = getattr(store_module, factory_class_name)
            
            # Save original create_store method
            if not hasattr(factory_class, "create_store"):
                print(f"Warning: create_store method not found in {factory_class_name}")
                return None
            
            original_create = factory_class.create_store
            
            # Patch with in-memory store
            @staticmethod
            def patched_create_store():
                return self.in_memory_store
            
            factory_class.create_store = patched_create_store
            
            return original_create
            
        except Exception as e:
            print(f"Warning: Could not patch store for {platform}: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    async def crawl_platform(
        self, 
        platform: str, 
        keywords: str, 
        max_items: int = 20,
        timeout: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Crawl a single platform
        
        Args:
            platform: Platform name (xhs, dy, bili, wb, zhihu, tieba, ks)
            keywords: Search keywords
            max_items: Maximum number of items to crawl
            timeout: Timeout in seconds
            
        Returns:
            List of crawled content items
        """
        normalized_platform = self._normalize_platform(platform)
        
        # Clear store for this crawl
        self.in_memory_store.clear()
        
        # Patch store to use in-memory store
        original_store_factory = self._patch_store_for_platform(normalized_platform)
        
        try:
            with self._configure_mediacrawler(normalized_platform, keywords, max_items):
                # Import crawler factory from MediaCrawler main module
                # Try different import paths
                try:
                    from MediaCrawler.main import CrawlerFactory
                except ImportError:
                    # Fallback: import from main if MediaCrawler is in path
                    import sys
                    import os
                    mc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "MediaCrawler")
                    if mc_path not in sys.path:
                        sys.path.insert(0, mc_path)
                    from main import CrawlerFactory
                
                # Create crawler instance
                crawler = CrawlerFactory.create_crawler(normalized_platform)
                
                # Start crawler (this will call search internally)
                try:
                    # For Bilibili, we might need to handle login timeout differently
                    if normalized_platform == "bili":
                        # Bilibili login can take a long time, increase effective timeout
                        # But also add a shorter timeout for the login check itself
                        print(f"[INFO] Starting Bilibili crawler (timeout: {timeout}s)")
                        print(f"[NOTE] If login is required, please scan QR code in the browser window")
                        print(f"[NOTE] Login has a 10-minute timeout. If you don't login, it will fail.")
                    # Run with timeout
                    await asyncio.wait_for(crawler.start(), timeout=timeout)
                except asyncio.TimeoutError:
                    print(f"[WARNING] Crawler timeout for {platform} after {timeout}s")
                    if normalized_platform == "bili":
                        print(f"[INFO] Bilibili login might have timed out. Try using cookie login instead.")
                except Exception as e:
                    print(f"[WARNING] Crawler error for {platform}: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Cleanup browser context if exists
                if hasattr(crawler, "browser_context"):
                    try:
                        await crawler.browser_context.close()
                    except:
                        pass
                
                if hasattr(crawler, "cdp_manager") and crawler.cdp_manager:
                    try:
                        await crawler.cdp_manager.cleanup(force=True)
                    except:
                        pass
            
            # Get collected data
            contents = self.in_memory_store.get_all_contents()
            
            # Standardize data format
            standardized = []
            for item in contents:
                standardized.append(self._standardize_item(item, normalized_platform))
            
            return standardized
            
        except Exception as e:
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII chars for Windows
            print(f"[ERROR] Error crawling {platform}: {error_msg}")
            import traceback
            try:
                traceback.print_exc()
            except:
                pass  # Ignore encoding errors in traceback
            return []
        
        finally:
            # Restore original store factory if patched
            if original_store_factory:
                normalized_platform = self._normalize_platform(platform)
                platform_config = {
                    "xhs": ("store.xhs", "XhsStoreFactory"),
                    "dy": ("store.douyin", "DouyinStoreFactory"),
                    "ks": ("store.kuaishou", "KuaishouStoreFactory"),
                    "bili": ("store.bilibili", "BiliStoreFactory"),
                    "wb": ("store.weibo", "WeibostoreFactory"),
                    "tieba": ("store.tieba", "TieBaStoreFactory"),
                    "zhihu": ("store.zhihu", "ZhihuStoreFactory"),
                }
                config = platform_config.get(normalized_platform)
                if config:
                    store_module_name, factory_class_name = config
                    try:
                        store_module = importlib.import_module(store_module_name)
                        if hasattr(store_module, factory_class_name):
                            factory_class = getattr(store_module, factory_class_name)
                            factory_class.create_store = staticmethod(original_store_factory)
                    except:
                        pass
    
    def _standardize_item(self, item: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Standardize item format across platforms"""
        standardized = {
            "platform": platform,
            "content_id": (
                item.get("note_id") or 
                item.get("aweme_id") or 
                item.get("video_id") or 
                item.get("bvid") or 
                item.get("id") or 
                ""
            ),
            "title": item.get("title") or item.get("desc", "")[:100] or "",
            "content": item.get("desc") or item.get("title", "") or "",
            "author": {
                "user_id": item.get("user_id") or item.get("uid", ""),
                "nickname": item.get("nickname") or "",
                "avatar": item.get("avatar") or "",
            },
            "interactions": {
                "liked_count": item.get("liked_count") or item.get("digg_count") or 0,
                "comment_count": item.get("comment_count") or 0,
                "share_count": item.get("share_count") or 0,
                "collected_count": item.get("collected_count") or item.get("collect_count") or 0,
            },
            "timestamp": item.get("time") or item.get("create_time") or "",
            "url": item.get("note_url") or item.get("aweme_url") or item.get("video_url") or "",
            "raw_data": item,  # Keep original data
        }
        return standardized
    
    async def crawl_multiple_platforms(
        self,
        platforms: List[str],
        keywords: str,
        max_items_per_platform: int = 15,
        timeout_per_platform: int = 300,
        max_concurrent: int = 2
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Crawl multiple platforms concurrently
        
        Args:
            platforms: List of platform names
            keywords: Search keywords
            max_items_per_platform: Max items per platform
            timeout_per_platform: Timeout per platform
            max_concurrent: Maximum concurrent crawlers
            
        Returns:
            Dictionary mapping platform to list of items
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(platform: str):
            async with semaphore:
                return platform, await self.crawl_platform(
                    platform, keywords, max_items_per_platform, timeout_per_platform
                )
        
        tasks = [crawl_with_semaphore(p) for p in platforms]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        result_dict = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"[ERROR] Platform crawl failed: {result}")
                continue
            platform, items = result
            result_dict[platform] = items
        
        return result_dict


# Global service instance
crawler_service = MediaCrawlerService()
