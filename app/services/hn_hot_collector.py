#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hacker News 热榜收集器
从 HN 的 Top Stories 和 Best Stories 获取热门内容
参照 TopHub 收集器的设计模式
"""

import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger


# HN 榜单配置
HN_SOURCES = {
    "top": {"name": "HN 最热", "category": "国外科技", "platform": "hackernews", "priority": 0},
    "best": {"name": "HN 最佳", "category": "国外科技", "platform": "hackernews", "priority": 1},
    "new": {"name": "HN 最新", "category": "国外科技", "platform": "hackernews", "priority": 2},
}


class HNHotCollector:
    """Hacker News 热榜收集器"""
    
    def __init__(self, use_cache: bool = True):
        """初始化收集器
        
        Args:
            use_cache: 是否启用缓存功能
        """
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.use_cache = use_cache
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        
        # 导入缓存服务
        if self.use_cache:
            try:
                from app.services.hot_news_cache import hot_news_cache
                self.cache_service = hot_news_cache
            except Exception:
                logger.warning("缓存服务导入失败，将禁用缓存")
                self.cache_service = None
        else:
            self.cache_service = None
    
    async def _fetch_item(self, client: httpx.AsyncClient, item_id: int) -> Optional[Dict]:
        """获取单个 HN item 详情
        
        Args:
            client: HTTP 客户端
            item_id: HN item ID
            
        Returns:
            item 数据字典，或 None 如果获取失败
        """
        try:
            url = f"{self.base_url}/item/{item_id}.json"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.debug(f"获取 item {item_id} 失败: {e}")
            return None
    
    async def fetch_source_news(self, source_id: str, max_items: int = 30) -> Dict:
        """从指定的 HN 榜单获取新闻
        
        Args:
            source_id: HN 榜单ID（"top", "best", "new"）
            max_items: 返回最多多少条新闻
            
        Returns:
            包含新闻数据的字典
        """
        source_info = HN_SOURCES.get(source_id, {"name": "未知来源", "category": "国外科技"})
        source_name = source_info["name"]
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # 获取热榜 ID 列表
                endpoint = f"{self.base_url}/{source_id}stories.json"
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                
                story_ids: List[int] = response.json() or []
                logger.info(f"✓ {source_name}: 获取到 {len(story_ids)} 个 story ID")
                
                # 限制 ID 列表（避免请求过多）
                story_ids = story_ids[:min(len(story_ids), max_items * 2)]
                
                # 并发获取 item 详情（限制并发数）
                news_items: List[Dict] = []
                semaphore = asyncio.Semaphore(10)  # 最多 10 个并发
                
                async def fetch_with_semaphore(idx: int, item_id: int):
                    async with semaphore:
                        item_data = await self._fetch_item(client, item_id)
                        if item_data:
                            # 过滤掉死链和无标题的 item
                            if item_data.get("type") == "story" and item_data.get("title"):
                                return (idx + 1, item_data)
                        return None
                
                # 创建任务
                tasks = [
                    fetch_with_semaphore(idx, item_id)
                    for idx, item_id in enumerate(story_ids)
                ]
                
                # 并发执行
                results = await asyncio.gather(*tasks, return_exceptions=False)
                
                # 整理结果
                for result in results:
                    if result:
                        rank, item_data = result
                        # 计算热度：score（得分）+ descendants（评论数）
                        score = item_data.get("score", 0)
                        descendants = item_data.get("descendants", 0)
                        hot_value = f"{score}分 · {descendants}条评论"
                        
                        news_items.append({
                            'rank': rank,
                            'title': item_data.get("title", ""),
                            'url': item_data.get("url", ""),
                            'hot_value': hot_value,
                            'score': score,
                            'descendants': descendants,
                            'by': item_data.get("by", ""),
                            'time': item_data.get("time", 0),
                        })
                        
                        if len(news_items) >= max_items:
                            break
                
                logger.info(f"✓ {source_name}: 成功获取 {len(news_items)} 条新闻")
                
                return {
                    'source_id': source_id,
                    'source_name': source_name,
                    'category': source_info['category'],
                    'status': 'success',
                    'news_count': len(news_items),
                    'news_items': news_items,
                    'timestamp': datetime.now().isoformat()
                }
                
        except httpx.TimeoutException:
            logger.error(f"✗ {source_name}: 请求超时")
            return {
                'source_id': source_id,
                'source_name': source_name,
                'status': 'timeout',
                'error': '请求超时',
                'news_items': [],
                'timestamp': datetime.now().isoformat()
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"✗ {source_name}: HTTP错误 {e.response.status_code}")
            return {
                'source_id': source_id,
                'source_name': source_name,
                'status': 'http_error',
                'error': f'HTTP {e.response.status_code}',
                'news_items': [],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.exception(f"✗ {source_name}: 未知错误 - {e}")
            return {
                'source_id': source_id,
                'source_name': source_name,
                'status': 'error',
                'error': str(e),
                'news_items': [],
                'timestamp': datetime.now().isoformat()
            }

    
    async def collect_news(
        self,
        source_ids: Optional[List[str]] = None,
        max_items: int = 30,
        force_refresh: bool = False
    ) -> Dict:
        """收集 HN 热点新闻
        
        Args:
            source_ids: 指定要收集的榜单ID列表，None表示 ["top"]
            max_items: 返回最多多少条新闻
            force_refresh: 是否强制刷新（忽略缓存）
            
        Returns:
            包含收集结果的字典
        """
        # 如果不强制刷新，尝试从缓存读取（可选）
        if not force_refresh and self.use_cache and self.cache_service:
            try:
                cached_data = self.cache_service.get_cached_data(cache_key='hn')
                if cached_data:
                    logger.info("📦 使用缓存数据")
                    return cached_data
            except Exception:
                pass  # 缓存失败则继续
        
        logger.info("=" * 80)
        logger.info("🚀 开始从 Hacker News 收集热点新闻...")
        logger.info(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 选择要收集的榜单
        if source_ids is None:
            source_ids = ["top"]
        
        logger.info(f"📊 将从 {len(source_ids)} 个榜单收集数据:")
        for source_id in source_ids:
            source_name = HN_SOURCES.get(source_id, {}).get('name', source_id)
            logger.info(f"   - {source_name}")
        logger.info("=" * 80)
        
        try:
            # 并发获取所有榜单的新闻
            results = []
            for source_id in source_ids:
                result = await self.fetch_source_news(source_id, max_items=max_items)
                results.append(result)
                # 避免请求过快
                await asyncio.sleep(0.3)
            
            # 统计信息
            successful_sources = sum(1 for r in results if r['status'] == 'success')
            total_news = sum(r.get('news_count', 0) for r in results)
            
            # 整理所有新闻为统一格式
            all_news = []
            for result in results:
                if result['status'] == 'success':
                    for item in result['news_items']:
                        news_obj = {
                            'id': f"{result['source_id']}_{item['rank']}",
                            'title': item['title'],
                            'url': item['url'],
                            'hot_value': item['hot_value'],
                            'rank': item['rank'],
                            'source': result['source_name'],
                            'source_id': result['source_id'],
                            'category': result['category'],
                            # HN 特有字段
                            'score': item.get('score'),
                            'descendants': item.get('descendants'),
                            'author': item.get('by'),
                            'posted_time': item.get('time'),
                        }
                        all_news.append(news_obj)
                        
                        if len(all_news) >= max_items:
                            break
                    if len(all_news) >= max_items:
                        break
            
            # 打印统计信息
            logger.info("=" * 80)
            logger.info(f"📈 收集统计:")
            logger.info(f"   总榜单数: {len(results)}")
            logger.info(f"   成功数: {successful_sources}")
            logger.info(f"   总新闻数: {total_news}")
            logger.info(f"   已整理: {len(all_news)}")
            logger.info("=" * 80)
            
            result_data = {
                'success': True,
                'news_list': all_news,
                'raw_results': results,
                'successful_sources': successful_sources,
                'total_sources': len(results),
                'total_news': total_news,
                'collection_time': datetime.now().isoformat(),
                'from_cache': False,
            }
            
            # 保存到缓存
            if self.use_cache and self.cache_service:
                self.cache_service.save_to_cache(result_data, cache_key='hn')
            
            return result_data
            
        except Exception as e:
            logger.exception(f"❌ 收集新闻失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'news_list': [],
                'total_news': 0
            }



# 全局实例
hn_hot_collector = HNHotCollector()
