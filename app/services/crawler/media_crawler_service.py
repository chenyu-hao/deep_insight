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
MEDIA_CRAWLER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "MediaCrawler")
if MEDIA_CRAWLER_PATH not in sys.path:
    sys.path.insert(0, MEDIA_CRAWLER_PATH)

from app.services.crawler.in_memory_store import InMemoryStore
from app.services.crawler.cookie_manager import cookie_manager


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
            # All major platforms need visible browser for login (wb, bili, xhs, tieba, dy, ks, zhihu)
            # Check if we have saved cookies first
            saved_cookie = cookie_manager.get_cookie(normalized_platform)
            has_cookie_str = bool(saved_cookie and saved_cookie.strip())

            # Check for browser data directory (User Data Dir)
            # Path: project_root/browser_data/{platform}_user_data_dir
            browser_data_dir = "browser_data"
            
            # Check for specific profile types
            standard_user_data_dir = os.path.join(browser_data_dir, f"{normalized_platform}_user_data_dir")
            cdp_user_data_dir = os.path.join(browser_data_dir, f"cdp_{normalized_platform}_user_data_dir")
            
            has_standard_data = os.path.exists(standard_user_data_dir) and os.path.isdir(standard_user_data_dir)
            has_cdp_data = os.path.exists(cdp_user_data_dir) and os.path.isdir(cdp_user_data_dir)
            
            has_browser_data = has_standard_data or has_cdp_data
            has_valid_cookie = has_cookie_str or has_browser_data

            print(f"[DEBUG] Platform: {normalized_platform}")
            print(f"[DEBUG] Saved Cookie Length: {len(saved_cookie) if saved_cookie else 0}")
            print(f"[DEBUG] Data Exists - Standard: {has_standard_data}, CDP: {has_cdp_data}")
            print(f"[DEBUG] Has Valid Login State: {has_valid_cookie}")

            # Determine mode based on login requirement and cookie existence
            # Platforms that require login: wb, bili, xhs, tieba, dy, ks, zhihu
            login_required_platforms = ["wb", "bili", "xhs", "tieba", "dy", "ks", "zhihu"]
            
            if normalized_platform in login_required_platforms:
                if has_valid_cookie:
                    # Have cookie OR browser data -> Run Headless (Silent)
                    mc_config.HEADLESS = True
                    mc_config.CDP_HEADLESS = True
                    
                    # Smart Mode Selection: Use CDP only if we have CDP data or Cookies (defaulting to CDP for fresh cookies)
                    # If we ONLY have standard data, force standard mode to retain login
                    if has_cdp_data:
                        mc_config.ENABLE_CDP_MODE = True
                        mode_name = "CDP模式"
                    elif has_standard_data:
                        mc_config.ENABLE_CDP_MODE = False
                        mode_name = "普通模式"
                    else:
                        # Fallback for Cookie-only case: Prefer CDP for new sessions
                        mc_config.ENABLE_CDP_MODE = True
                        mode_name = "CDP模式(基于Cookie)"

                    if has_cookie_str:
                        mc_config.LOGIN_TYPE = "cookie"
                        mc_config.COOKIES = saved_cookie
                        login_method = "Cookie字符串"
                    else:
                        mc_config.LOGIN_TYPE = "qrcode"
                        login_method = "浏览器缓存数据"
                    
                    platform_names = {"xhs": "小红书", "tieba": "贴吧", "dy": "抖音", "ks": "快手", "zhihu": "知乎", "bili": "B站", "wb": "微博"}
                    platform_cn = platform_names.get(normalized_platform, normalized_platform)
                    print(f"[配置] {platform_cn} 检测到有效 {login_method}，启用静默爬虫 ({mode_name})")
                else:
                    # No cookie -> Show Browser for Login
                    mc_config.HEADLESS = False
                    mc_config.CDP_HEADLESS = False
                    mc_config.ENABLE_CDP_MODE = False # Disable CDP for stable manual login
                    mc_config.LOGIN_TYPE = "qrcode"
                    
                    platform_names = {"xhs": "小红书", "tieba": "贴吧", "dy": "抖音", "ks": "快手", "zhihu": "知乎", "bili": "B站", "wb": "微博"}
                    platform_cn = platform_names.get(normalized_platform, normalized_platform)
                    print(f"[配置] {platform_cn} 未检测到登录状态，将弹出浏览器进行扫码登录 (HEADLESS=False)")
            else:
                # Platforms that don't strictly require login
                mc_config.HEADLESS = True
                mc_config.CDP_HEADLESS = True
                mc_config.ENABLE_CDP_MODE = True
                print(f"[配置] 平台 {normalized_platform} 不需要登录，启用静默模式")
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
                print(f"警告: 在 {store_module_name} 中未找到工厂类 {factory_class_name}")
                return None
            
            factory_class = getattr(store_module, factory_class_name)
            
            # Save original create_store method
            if not hasattr(factory_class, "create_store"):
                print(f"警告: 在 {factory_class_name} 中未找到 create_store 方法")
                return None
            
            original_create = factory_class.create_store
            
            # Patch with in-memory store
            @staticmethod
            def patched_create_store():
                return self.in_memory_store
            
            factory_class.create_store = patched_create_store
            
            return original_create
            
        except Exception as e:
            print(f"警告: 无法为平台 {platform} 修补存储: {e}")
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
                
                # Force re-check configuration after crawler creation for login-required platforms
                # This is needed because MediaCrawler might cache config during import
                if normalized_platform in ["wb", "bili", "xhs", "tieba", "dy", "ks", "zhihu"]:
                    import config as mc_config
                    print(f"[诊断] 爬虫创建后检查配置: ENABLE_CDP_MODE={mc_config.ENABLE_CDP_MODE}, HEADLESS={mc_config.HEADLESS}")
                
                # Start crawler (this will call search internally)
                try:
                    # For Bilibili and Weibo, we might need to handle login timeout differently
                    if normalized_platform == "bili":
                        # Bilibili login can take a long time, increase effective timeout
                        # But also add a shorter timeout for the login check itself
                        print(f"[信息] 正在启动B站爬虫 (超时时间: {timeout}秒)")
                        print(f"[提示] 如需登录，请在浏览器窗口中扫描二维码")
                        print(f"[提示] 登录超时时间为10分钟。如果不登录，将会失败。")
                    elif normalized_platform == "wb":
                        # Weibo also requires login
                        print(f"[信息] 正在启动微博爬虫 (超时时间: {timeout}秒)")
                        print(f"[提示] 浏览器将首先打开微博首页，请稍候...")
                        print(f"[提示] 如果浏览器长时间停在空白页面，可能是网络问题，请检查网络连接")
                        print(f"[提示] 如需登录，会自动跳转到登录页面，请在浏览器窗口中扫描二维码")
                        print(f"[提示] 登录超时时间为10分钟。如果不登录，将会失败。")
                    elif normalized_platform in ["xhs", "tieba", "dy", "ks", "zhihu"]:
                        # Other platforms also require login
                        platform_names = {"xhs": "小红书", "tieba": "贴吧", "dy": "抖音", "ks": "快手", "zhihu": "知乎"}
                        platform_cn = platform_names.get(normalized_platform, normalized_platform)
                        print(f"[信息] 正在启动{platform_cn}爬虫 (总超时时间: {timeout}秒)")
                        print(f"[提示] 请在浏览器窗口中扫描二维码登录")
                        print(f"[提示] 登录等待时间最长10分钟，请尽快完成登录。")
                    
                    # Run with timeout
                    await asyncio.wait_for(crawler.start(), timeout=timeout)
                    
                    # After successful start, try to extract and save cookies
                    # This will save cookies for next time, avoiding QR code login
                    print(f"[DEBUG] 爬取结束，尝试提取 Cookie 以便下次静默登录...")
                    try:
                        extracted_cookies = None
                        
                        # Strategy 1: check browser_context (Playwright)
                        if hasattr(crawler, "browser_context") and crawler.browser_context:
                            print(f"[DEBUG] 检测到 browser_context，尝试获取 cookies")
                            extracted_cookies = await crawler.browser_context.cookies()
                            
                        # Strategy 2: check page environment (DrissionPage/Playwright fallback)
                        elif hasattr(crawler, "page"):
                            print(f"[DEBUG] 检测到 page 对象，尝试获取 cookies")
                            if hasattr(crawler.page, "context"):
                                extracted_cookies = await crawler.page.context.cookies()
                            elif hasattr(crawler.page, "cookies"):
                                # DrissionPage often returns cookies as list of dicts or dict
                                cookies_res = crawler.page.cookies
                                if callable(cookies_res):
                                    extracted_cookies = cookies_res(as_dict=False) # Get list of dicts
                                else:
                                    extracted_cookies = cookies_res

                        if extracted_cookies:
                            print(f"[DEBUG] 成功提取到 {len(extracted_cookies)} 个 Cookie，正在保存到 cookies.json...")
                            cookie_manager.save_cookies_from_browser(normalized_platform, extracted_cookies)
                        else:
                            print(f"[DEBUG] 未能提取到 Cookie: crawler 对象中未找到可用 Cookie 数据")
                            if hasattr(crawler, "__dict__"):
                                print(f"[DEBUG] Crawler 属性列表: {list(crawler.__dict__.keys())}")
                                
                    except Exception as e:
                        # Cookie extraction is optional, don't fail if it doesn't work
                        print(f"[提示] 未能自动保存 Cookie（详细错误）: {e}")
                        
                except asyncio.TimeoutError:
                    print(f"[警告] 平台 {platform} 爬取超时，已等待 {timeout} 秒")
                    if normalized_platform == "bili":
                        print(f"[信息] B站登录可能已超时。请尝试使用cookie登录方式。")
                    elif normalized_platform in ["wb", "xhs", "tieba", "dy", "ks", "zhihu"]:
                        platform_names = {"wb": "微博", "xhs": "小红书", "tieba": "贴吧", "dy": "抖音", "ks": "快手", "zhihu": "知乎"}
                        platform_cn = platform_names.get(normalized_platform, normalized_platform)
                        print(f"[信息] {platform_cn}登录可能已超时。请尝试使用cookie登录方式。")
                except SystemExit as e:
                    # MediaCrawler's weibo login code may call sys.exit() on login failure.
                    # If not handled, it will terminate the whole uvicorn process.
                    print(f"[警告] 平台 {platform} 登录流程触发 SystemExit（通常是未找到二维码/登录失败），将跳过该平台继续流程: {e}")
                except Exception as e:
                    print(f"[警告] 平台 {platform} 爬取出错: {e}")
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
            
        except SystemExit as e:
            # Prevent sys.exit() from killing the server; treat as platform failure.
            print(f"[错误] 爬取平台 {platform} 触发 SystemExit（登录失败/二维码未出现等），已跳过该平台: {e}")
            return []
        except Exception as e:
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII chars for Windows
            print(f"[错误] 爬取平台 {platform} 时出错: {error_msg}")
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
                print(f"[错误] 平台爬取失败: {result}")
                continue
            platform, items = result
            result_dict[platform] = items
        
        return result_dict


# Global service instance
crawler_service = MediaCrawlerService()
