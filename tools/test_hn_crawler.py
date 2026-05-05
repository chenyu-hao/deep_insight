import asyncio

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.crawler.foreign_news_crawler_service import foreign_crawler_service


async def main() -> None:
    parser = argparse.ArgumentParser(description="Hacker News crawler smoke test")
    parser.add_argument(
        "--topic",
        default="electric vehicles",
        help="Search topic/keywords (default: electric vehicles)",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=30,
        help="Max stories to crawl (default: 30)",
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=80,
        help="Max comments per story to include (default: 80)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Total crawl timeout seconds (default: 180)",
    )
    args = parser.parse_args()

    items = await foreign_crawler_service.crawl_platform(
        "hn",
        args.topic,
        max_items=args.max_items,
        max_comments=args.max_comments,
        timeout=args.timeout,
    )

    print("topic:", args.topic)
    print("items:", len(items))
    if not items:
        return

    for idx, item in enumerate(items, start=1):
        print("\n" + "=" * 90)
        print(f"#{idx}  {item.get('title','')}")
        print(f"URL: {item.get('url','')}")
        interactions = item.get("interactions") or {}
        print(
            "Interactions:",
            f"points={interactions.get('liked_count', 0)}",
            f"comments={interactions.get('comment_count', 0)}",
        )
        print("-" * 90)
        # Print full content (title + comments) so you can review everything.
        print(item.get("content", ""))


if __name__ == "__main__":
    asyncio.run(main())
