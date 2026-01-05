import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.foreign_news_crawler_service import foreign_crawler_service


def _required_env_missing() -> list[str]:
    missing = []
    for k in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]:
        if not (os.getenv(k) or "").strip():
            missing.append(k)
    return missing


async def main() -> None:
    missing = _required_env_missing()
    if missing:
        print("Missing env vars:", ", ".join(missing))
        print("Set them in your .env, then re-run this script.")
        return

    try:
        items = await foreign_crawler_service.crawl_platform(
            "reddit", "OpenAI", max_items=3, max_comments=8, timeout=30
        )
    except Exception as e:
        msg = str(e)
        print("Reddit crawl failed:")
        print(msg)
        if "approval" in msg.lower() or "responsible builder" in msg.lower() or "denied" in msg.lower():
            print("\nWhat to do next:")
            print("- Reddit may require approval for new OAuth access now.")
            print("- If you previously had working tokens/apps, those often continue to work.")
            print("- Otherwise, follow Reddit's Responsible Builder Policy / Devvit guidance to request API access approval.")
        return

    print("items", len(items))
    if not items:
        return
    first = items[0]
    print(first["title"])
    print(first["url"])
    print(first["content"][:400])


if __name__ == "__main__":
    asyncio.run(main())
