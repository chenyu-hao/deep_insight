"""Crawler router service.

Keeps existing MediaCrawler integration intact while allowing additional
platforms (e.g. foreign news/discussion sources) to plug into the same workflow.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.config import settings
from app.services.media_crawler_service import crawler_service as media_crawler_service
from app.services.foreign_news_crawler_service import (
    foreign_crawler_service,
)


class CrawlerRouterService:
    """Routes crawl requests to the appropriate backend service."""

    DOMESTIC_PLATFORMS = {"wb", "dy", "ks", "bili", "tieba", "zhihu", "xhs"}
    FOREIGN_PLATFORMS = {"hn", "reddit"}

    @property
    def supported_platforms(self) -> List[str]:
        return sorted(self.DOMESTIC_PLATFORMS | self.FOREIGN_PLATFORMS)

    def normalize_platform(self, platform: str) -> str:
        p = (platform or "").lower().strip()
        p = media_crawler_service.PLATFORM_MAP.get(p, p)
        p = foreign_crawler_service.PLATFORM_MAP.get(p, p)
        return p

    async def crawl_platform(
        self,
        platform: str,
        keywords: str,
        max_items: int = 15,
        timeout: int = 180,
    ) -> List[Dict[str, Any]]:
        normalized = self.normalize_platform(platform)

        limits = settings.CRAWLER_LIMITS.get(normalized, {})
        max_items = int(limits.get("max_items", max_items))
        max_comments = int(limits.get("max_comments", 10))

        # Make it easy to diagnose “HN returns 0 items” situations.
        print(
            f"[CRAWLER][LIMITS] platform={normalized} max_items={max_items} max_comments={max_comments} timeout={timeout}"
        )

        # Treat max_items<=0 as an explicit disable flag.
        if max_items <= 0:
            print(f"[CRAWLER][LIMITS] platform={normalized} is disabled (max_items<=0), skipping")
            return []

        if normalized in self.DOMESTIC_PLATFORMS:
            return await media_crawler_service.crawl_platform(
                platform=normalized,
                keywords=keywords,
                max_items=max_items,
                timeout=timeout,
            )

        if normalized in self.FOREIGN_PLATFORMS:
            return await foreign_crawler_service.crawl_platform(
                platform=normalized,
                keywords=keywords,
                max_items=max_items,
                max_comments=max_comments,
                timeout=timeout,
            )

        raise ValueError(f"Unsupported platform: {platform}")


crawler_router_service = CrawlerRouterService()
